package org.logende.converter.converters;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.net.URISyntaxException;
import org.logende.converter.ConverterService;

public class XsdToJsonSchemaConverter implements ConverterService.Converter {

    private static final String JSONIX_JAR_NAME = "jsonix-schema-compiler-full-2.3.9.jar";
    private static final String ACTIVATION_JAR_NAME = "activation-1.1.1.jar";
    private static final int TIMEOUT_SECONDS = 30;

    @Override
    public String getName() {
        return "Jsonix";
    }

    @Override
    public String getSourceLanguage() {
        return "Xsd";
    }

    @Override
    public String getTargetLanguage() {
        return "JsonSchema";
    }

    @Override
    public String getLibrary() {
        return "jsonix-schema-compiler";
    }

    @Override
    public String getLibraryVersion() {
        return "2.3.9";
    }

    @Override
    public String getLibraryUrl() {
        return "https://github.com/highsource/jsonix";
    }


    @Override
    public String convert(String schema) throws Exception {
        // Get paths
        String jarDir = getOwnJarDir();
        String jsonixJar = Paths.get(jarDir, "lib", JSONIX_JAR_NAME).toString();
        String activationJar = Paths.get(jarDir, "lib", ACTIVATION_JAR_NAME).toString();  // Add this

        // Validate both JARs exist
        Path jarPath = Paths.get(jsonixJar);
        Path activationPath = Paths.get(activationJar);  // Add this
        if (!Files.exists(jarPath)) {
            throw new RuntimeException("Jsonix JAR not found at: " + jarPath.toAbsolutePath());
        }
        if (!Files.exists(activationPath)) {  // Add this
            throw new RuntimeException("Activation JAR not found at: " + activationPath.toAbsolutePath() +
                ". Download from https://repo1.maven.org/maven2/javax/activation/activation/1.1.1/activation-1.1.1.jar");
        }


        // Write input XSD to a temp file
        Path tempDir = Files.createTempDirectory("xsd2jsonschema");
        Path xsdFile = tempDir.resolve("input.xsd");
        Files.writeString(xsdFile, schema);

        // Output directory for Jsonix
        Path outDir = tempDir.resolve("out");
        Files.createDirectories(outDir);

        // Build command: classpath + main class
        List<String> command = Arrays.asList(
            "java",
            // Add these 3 lines for Java 17+ compatibility
            "--add-opens", "java.base/java.lang=ALL-UNNAMED",
            "--add-opens", "java.base/jdk.internal.loader=ALL-UNNAMED",
            "--add-opens", "java.base/java.util=ALL-UNNAMED",
            "-cp", jsonixJar + File.pathSeparator + activationJar,
            "org.hisrc.jsonix.JsonixMain",
            "-generateJsonSchema",
            "-d", outDir.toString(),
            xsdFile.toString()
        );


        try {

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
        // Walk entire tree for .jsonschema first (primary target)
        try (var walk = Files.walk(outDir)) {
            var found = walk.filter(p -> p.getFileName().toString().endsWith(".jsonschema")).findFirst();
            if (found.isPresent()) {
                System.err.println("DEBUG: Found schema: " + found.get());
                return Files.readString(found.get());
            }
        }

        // Fallback: any .json (in case no .jsonschema)
        try (var walk = Files.walk(outDir)) {
            var found = walk.filter(p -> p.getFileName().toString().endsWith(".json")).findFirst();
            if (found.isPresent()) {
                System.err.println("DEBUG: Found json: " + found.get());
                return Files.readString(found.get());
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
