package com.example.converter;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.HashMap;

@SpringBootApplication
@RestController
public class ConverterApplication {

    public static void main(String[] args) {
        SpringApplication.run(ConverterApplication.class, args);
    }

    @PostMapping("/convert")
    public Map<String, String> convert(@RequestBody Map<String, String> body) {
        String schema = body.get("schema");
        String sourceFormat = body.get("sourceFormat");
        String targetFormat = body.get("targetFormat");
        Map<String, String> result = new HashMap<>();
        result.put("schema", "[Java Dummy] Converted from " + sourceFormat + " to " + targetFormat + ": " + schema);
        return result;
    }
}
