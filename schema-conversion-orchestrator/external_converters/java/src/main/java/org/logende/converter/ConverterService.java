package org.logende.converter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Stream;
import org.logende.converter.converters.JsonSchemaToDtdConverter;
import org.logende.converter.converters.XsdToDtdConverter;
import org.logende.converter.converters.DtdToXsdConverter;
import org.logende.converter.converters.XsdToJsonSchemaConverter;

public class ConverterService {
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Map<String, Converter> converters = new HashMap<>();
    
    public static class ConversionRequest {
        public String sourceFormat;
        public String targetFormat;
        public String schema;
    }
    
    public static class ConversionResponse {
        public String schema;
        public String error;
        
        public ConversionResponse(String schema) {
            this.schema = schema;
        }
        
        public ConversionResponse(String schema, String error) {
            this.schema = schema;
            this.error = error;
        }
    }
    
    public static class ConverterInfo {
        public String name;
        public String sourceFormat;
        public String targetFormat;
        public List<String> supportedFeatures;
    }
    
    public interface Converter {
        String getName();
        String getSourceFormat();
        String getTargetFormat();
        List<String> getSupportedFeatures();
        String convert(String schema) throws Exception;
    }
    
    public ConverterService() {
        loadConverters();
    }

    private void loadConverters() {
        // Just new them up manually
        register(new JsonSchemaToDtdConverter());
        register(new XsdToDtdConverter());
        register(new DtdToXsdConverter());
        register(new XsdToJsonSchemaConverter());
        // add more as needed
    }

    private void register(Converter converter) {
        String key = converter.getSourceFormat() + "->" + converter.getTargetFormat();
        converters.put(key, converter);
        System.err.println("Loaded converter: " + converter.getName() + " (" + key + ")");
    }
    
    public Converter findConverter(String sourceFormat, String targetFormat) {
        String key = sourceFormat + "->" + targetFormat;
        return converters.get(key);
    }
    
    public List<Converter> getAllConverters() {
        return new ArrayList<>(converters.values());
    }
    
    public void listConverters() throws IOException {
        List<ConverterInfo> infos = new ArrayList<>();
        for (Converter converter : converters.values()) {
            ConverterInfo info = new ConverterInfo();
            info.name = converter.getName();
            info.sourceFormat = converter.getSourceFormat();
            info.targetFormat = converter.getTargetFormat();
            info.supportedFeatures = converter.getSupportedFeatures();
            infos.add(info);
        }
        
        ObjectNode result = objectMapper.createObjectNode();
        result.set("converters", objectMapper.valueToTree(infos));
        System.out.println(objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(result));
    }
    
    public void processConversion(String inputFile) {
        try {
            // Read input file
            ConversionRequest request = objectMapper.readValue(new File(inputFile), ConversionRequest.class);
            
            // Validate request
            if (request.sourceFormat == null || request.targetFormat == null || request.schema == null) {
                throw new IllegalArgumentException("Missing required fields: sourceFormat, targetFormat, schema");
            }
            
            // Find appropriate converter
            Converter converter = findConverter(request.sourceFormat, request.targetFormat);
            
            if (converter == null) {
                List<String> availableConversions = new ArrayList<>();
                for (Converter c : converters.values()) {
                    availableConversions.add(c.getSourceFormat() + "->" + c.getTargetFormat());
                }
                throw new IllegalArgumentException(
                    String.format("No converter found for %s → %s. Available converters: %s",
                                request.sourceFormat, request.targetFormat, 
                                String.join(", ", availableConversions)));
            }
            
            System.err.println("Using converter: " + converter.getName());
            
            // Perform conversion
            String convertedSchema = converter.convert(request.schema);
            
            // Output result to stdout
            ConversionResponse response = new ConversionResponse(convertedSchema);
            System.out.println(objectMapper.writeValueAsString(response));
            
        } catch (Exception e) {
            System.err.println("Conversion error: " + e.getMessage());
            
            // Output error response to stdout
            try {
                ConversionResponse errorResponse = new ConversionResponse("", e.getMessage());
                System.out.println(objectMapper.writeValueAsString(errorResponse));
            } catch (IOException ioException) {
                System.err.println("Failed to serialize error response: " + ioException.getMessage());
            }
            System.exit(1);
        }
    }
    
    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("Usage: java ConverterService <command> [args]");
            System.err.println("Commands:");
            System.err.println("  convert <input_file>     - Convert schema from input file");
            System.err.println("  list                     - List all available converters");
            System.exit(1);
        }
        
        String command = args[0];
        ConverterService service = new ConverterService();
        
        try {
            switch (command) {
                case "list":
                    service.listConverters();
                    break;
                case "convert":
                    if (args.length != 2) {
                        System.err.println("Usage: java ConverterService convert <input_file>");
                        System.exit(1);
                    }
                    service.processConversion(args[1]);
                    break;
                default:
                    System.err.println("Unknown command: " + command);
                    System.exit(1);
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }
}