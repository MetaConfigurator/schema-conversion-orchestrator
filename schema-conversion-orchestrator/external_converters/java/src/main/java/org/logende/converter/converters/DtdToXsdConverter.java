package org.logende.converter.converters;

import java.io.*;
import com.thaiopensource.relaxng.translate.Driver;

import java.util.Collections;
import java.util.List;
import org.logende.converter.ConverterService;

public class DtdToXsdConverter implements ConverterService.Converter {

    @Override
    public String getName() {
        return "Trang";
    }

    @Override
    public String getSourceFormat() {
        return "Dtd";
    }

    @Override
    public String getTargetFormat() {
        return "Xsd";
    }

    @Override
    public List<String> getSupportedFeatures() {
        return Collections.emptyList();
    }

    @Override
    public String convert(String schema) throws Exception {
        // Write DTD schema to temp file
        File inputFile = File.createTempFile("schema", ".dtd");
        try (FileWriter fw = new FileWriter(inputFile)) {
            fw.write(schema);
        }

        File outputFile = File.createTempFile("schema", ".xsd");

        // Call Trang programmatically
        String[] args = {inputFile.getAbsolutePath(), outputFile.getAbsolutePath()};
        Driver.main(args);

        // Read result
        String result = new String(java.nio.file.Files.readAllBytes(outputFile.toPath()));

        inputFile.delete();
        outputFile.delete();

        return result;
    }
}
