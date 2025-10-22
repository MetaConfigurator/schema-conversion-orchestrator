import json
import os
import subprocess
import tempfile
from typing import List, Tuple
from schema_types import SchemaLanguage, SchemaFeature


class Converter:
    """
    Abstract base class for schema converters
    :param name: Name of the converter
    :param service_address: Address of the converter service or path to executable
    :param service_name: Name of the converter service
    :param source_format: Source schema language
    :param target_format: Target schema language
    :param supported_features: Dictionary mapping SchemaFeature to SchemaFeatureSupport or None if unknown
    """

    def __init__(self, name: str, service_address: str, service_name: str, source_format: SchemaLanguage,
                 target_format: SchemaLanguage, supported_features: set[SchemaFeature]):
        self.name = name
        self.service_address = service_address
        self.service_name = service_name
        self.source_format = source_format
        self.target_format = target_format
        self.supported_features = supported_features

    def convert(self, schema: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")


class ConverterExternal(Converter):
    def __init__(self, name: str, executable_path: str, service_name: str, source_format: SchemaLanguage,
                 target_format: SchemaLanguage, supported_features: set[SchemaFeature]):
        super().__init__(name, executable_path, service_name, source_format, target_format, supported_features)
        self.executable_path = executable_path

    def convert(self, schema: str) -> str:
        print(
            f"Calling external converter {self.name} at {self.executable_path} for {self.source_format} to {self.target_format}")

        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            input_data = {
                "sourceFormat": self.source_format.value,
                "targetFormat": self.target_format.value,
                "converterName": self.name,
                "schema": schema
            }
            json.dump(input_data, input_file)
            input_file_path = input_file.name

        try:
            # Run the subprocess
            result = subprocess.run(
                [self.executable_path, input_file_path],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"External converter failed with exit code {result.returncode}: {result.stderr}")

            # Parse the output
            try:
                output_data = json.loads(result.stdout)
                return output_data["schema"]
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse converter output as JSON: {e}")

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"External converter {self.name} timed out")
        finally:
            # Clean up temporary file
            os.unlink(input_file_path)


class ConverterInternal(Converter):
    def __init__(self, name: str, service_address: str, service_name: str, source_format: SchemaLanguage,
                 target_format: SchemaLanguage, supported_features: set[SchemaFeature]):
        super().__init__(name, service_address, service_name, source_format, target_format, supported_features)

    def convert(self, schema: str) -> str:
        if not self.validate_input(schema):
            raise ValueError("Invalid input schema for the source format.")

        converted_schema = self.converter_logic(schema)

        if not self.validate_output(converted_schema):
            raise ValueError("Converted schema is invalid for the target format.")

        return converted_schema

    # abstract function that needs to be overwritten to perform the conversion
    def converter_logic(self, schema: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")

    # abstract function to check if input is valid
    def validate_input(self, schema: str) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")

    # abstract function to check if output is valid
    def validate_output(self, schema: str) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")


class ConverterExternalGeneric(ConverterExternal):
    """Generic external converter that can handle multiple conversion types"""

    def __init__(self, name: str, executable_path: str, source_format: SchemaLanguage,
                 target_format: SchemaLanguage, supported_features: set[SchemaFeature],
                 converter_type: str):
        super().__init__(name, executable_path, converter_type, source_format, target_format, supported_features)
        self.converter_type = converter_type

    def convert(self, schema: str) -> str:
        print(
            f"Calling external {self.converter_type} converter {self.name} for {self.source_format} to {self.target_format}")

        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            input_data = {
                "sourceFormat": self.source_format.value,
                "targetFormat": self.target_format.value,
                "converterName": self.name,
                "schema": schema
            }
            json.dump(input_data, input_file)
            input_file_path = input_file.name

        try:
            # Run the subprocess with the convert command
            if self.converter_type == "node":
                cmd = ["node"] + self.executable_path.split()[1:] + ["convert", input_file_path]
            elif self.converter_type == "java":
                cmd = ["java", "-jar"] + self.executable_path.split()[2:] + ["convert", input_file_path]
            else:
                cmd = self.executable_path.split() + ["convert", input_file_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"External converter failed with exit code {result.returncode}: {result.stderr}")

            # Parse the output
            try:
                output_data = json.loads(result.stdout)
                if "error" in output_data and output_data["error"]:
                    raise RuntimeError(f"Converter returned error: {output_data['error']}")
                if not "schema" in output_data:
                    raise RuntimeError(f"Converter output missing 'schema' field")
                return output_data["schema"]
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse converter output as JSON: {e}")

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"External converter {self.name} timed out")
        finally:
            # Clean up temporary file
            os.unlink(input_file_path)


ConversionGraph = dict[str, list[Converter]]
ConversionPath = List[Converter]
ConversionPaths = List[ConversionPath]

# Tuple of (success: bool, result_schema_or_error_message: str, conversion_path: ConversionPath)
ConversionResult = Tuple[bool, str, ConversionPath]

# List of results ranked by success
ConversionResults = List[ConversionResult]

ConversionsCache = dict[str, str | None]


def conversion_path_to_string(path: ConversionPath) -> str:
    return " -> ".join([f"{conv.source_format.value} to {conv.target_format.value} via {conv.service_name}" for conv in path])
