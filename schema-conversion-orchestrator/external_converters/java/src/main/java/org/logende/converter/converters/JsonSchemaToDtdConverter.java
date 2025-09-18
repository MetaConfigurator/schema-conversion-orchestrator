package org.logende.converter.converters;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import org.logende.converter.ConverterService;

public class JsonSchemaToDtdConverter implements ConverterService.Converter {
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public String getName() {
        return "JsonSchemaToDtdConverter";
    }

    @Override
    public String getSourceFormat() {
        return "JsonSchema";
    }

    @Override
    public String getTargetFormat() {
        return "Dtd";
    }

    @Override
    public List<String> getSupportedFeatures() {
        return Arrays.asList("Properties", "Attributes");
    }

    @Override
    public String convert(String schema) throws Exception {
        System.err.println("JsonSchemaToDtdConverter processing schema: " +
                          schema.substring(0, Math.min(100, schema.length())) + "...");

        try {
            JsonNode jsonSchema = objectMapper.readTree(schema);

            StringBuilder dtd = new StringBuilder();
            dtd.append("<!-- DTD converted from JSON Schema by JsonSchemaToDtdConverter -->\n");

            String title = jsonSchema.has("title") ? jsonSchema.get("title").asText() : "root";
            dtd.append("<!DOCTYPE ").append(title).append(" [\n");

            // Convert properties to DTD elements
            if (jsonSchema.has("properties")) {
                dtd.append("  <!ELEMENT ").append(title).append(" (");

                JsonNode properties = jsonSchema.get("properties");
                Iterator<String> fieldNames = properties.fieldNames();
                boolean first = true;

                while (fieldNames.hasNext()) {
                    if (!first) dtd.append(", ");
                    String fieldName = fieldNames.next();
                    dtd.append(fieldName);
                    first = false;
                }

                dtd.append(")*>\n");

                // Define each property as an element
                fieldNames = properties.fieldNames();
                while (fieldNames.hasNext()) {
                    String fieldName = fieldNames.next();
                    JsonNode property = properties.get(fieldName);
                    String type = property.has("type") ? property.get("type").asText() : "string";

                    dtd.append("  <!ELEMENT ").append(fieldName).append(" (#PCDATA)>\n");

                    if (property.has("description")) {
                        dtd.append("  <!-- ").append(property.get("description").asText()).append(" -->\n");
                    }
                }
            } else {
                dtd.append("  <!ELEMENT ").append(title).append(" (#PCDATA)>\n");
            }

            dtd.append("]>");

            return dtd.toString();

        } catch (Exception e) {
            throw new Exception("Failed to parse JSON Schema: " + e.getMessage(), e);
        }
    }
}