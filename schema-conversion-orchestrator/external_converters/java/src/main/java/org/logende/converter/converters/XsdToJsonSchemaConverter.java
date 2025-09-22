package org.logende.converter.converters;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.net.URISyntaxException;
import org.logende.converter.ConverterService;

public class XsdToJsonSchemaConverter implements ConverterService.Converter {

    private static final String JSONIX_JAR_NAME = "jsonix-schema-compiler-full-2.3.9.jar";
    private static final int TIMEOUT_SECONDS = 30;

    @Override
    public String getName() {
        return "Jsonix";
    }

    @Override
    public String getSourceFormat() {
        return "Xsd";
    }

    @Override
    public String getTargetFormat() {
        return "JsonSchema";
    }

    @Override
    public List<String> getSupportedFeatures() {
        return Collections.emptyList();
    }

    @Override
    public String convert(String schema) throws Exception {
        // Resolve Jsonix JAR path relative to this JAR’s directory
        String jarDir = getOwnJarDir();
        String jsonixJar = Paths.get(jarDir, "lib", JSONIX_JAR_NAME).toString();

        // Validate JAR exists
        Path jarPath = Paths.get(jsonixJar);
        if (!Files.exists(jarPath)) {
            throw new RuntimeException("Jsonix JAR not found at: " + jarPath.toAbsolutePath() +
                ". Please download and place it in the lib directory.");
        }

        // Write input XSD to a temp file
        Path tempDir = Files.createTempDirectory("xsd2jsonschema");
        Path xsdFile = tempDir.resolve("input.xsd");
        Files.writeString(xsdFile, schema);

        // Output directory for Jsonix
        Path outDir = tempDir.resolve("out");
        Files.createDirectories(outDir);

        try {
            // Build command to execute Jsonix JAR
            List<String> command = Arrays.asList(
                "java",
                "-jar", jarPath.toAbsolutePath().toString(),
                "-generateJsonSchema",
                "-d", outDir.toString(),
                xsdFile.toString()
            );

            // Execute the command
            ProcessBuilder pb = new ProcessBuilder(command);
            pb.directory(tempDir.toFile());
            pb.redirectErrorStream(true);

            Process process = pb.start();

            // Capture output for debugging
            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }
            }

            // Wait for process to complete with timeout
            boolean finished = process.waitFor(TIMEOUT_SECONDS, TimeUnit.SECONDS);

            if (!finished) {
                process.destroyForcibly();
                throw new RuntimeException("Jsonix process timed out after " + TIMEOUT_SECONDS + " seconds");
            }

            int exitCode = process.exitValue();
            if (exitCode != 0) {
                throw new RuntimeException("Jsonix failed with exit code " + exitCode +
                    ". Output:\n" + output.toString());
            }

        } catch (IOException | InterruptedException e) {
            cleanupTempFiles(tempDir);
            throw new RuntimeException("Failed to execute Jsonix: " + e.getMessage(), e);
        }

        // Find first .json schema file produced
        String result = findJsonSchemaFile(outDir);

        // Clean up temp files
        cleanupTempFiles(tempDir);

        if (result != null) {
            return result;
        }

        throw new RuntimeException("No JSON Schema produced by Jsonix.");
    }

    private String findJsonSchemaFile(Path outDir) throws IOException {
        // Look for .json files in the output directory
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(outDir, "*.json")) {
            for (Path file : stream) {
                return Files.readString(file);
            }
        }

        // Also check subdirectories (Jsonix sometimes creates nested structure)
        try (DirectoryStream<Path> dirStream = Files.newDirectoryStream(outDir,
                path -> Files.isDirectory(path))) {
            for (Path subDir : dirStream) {
                try (DirectoryStream<Path> jsonStream = Files.newDirectoryStream(subDir, "*.json")) {
                    for (Path file : jsonStream) {
                        return Files.readString(file);
                    }
                }
            }
        }

        return null;
    }

    private void cleanupTempFiles(Path tempDir) {
        try {
            Files.walk(tempDir)
                .sorted(Comparator.reverseOrder())
                .map(Path::toFile)
                .forEach(File::delete);
        } catch (IOException e) {
            System.err.println("Warning: Failed to clean up temporary files in " +
                tempDir + ": " + e.getMessage());
        }
    }


    private String getOwnJarDir() throws URISyntaxException {
        // Get path of the running JAR
        File jarFile = new File(
            ConverterService.class.getProtectionDomain()
                .getCodeSource()
                .getLocation()
                .toURI()
        );
        // Return the parent directory
        return jarFile.getParentFile().getAbsolutePath();
    }


}