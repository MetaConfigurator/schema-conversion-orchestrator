import json
import os
import subprocess
import tempfile
from typing import List, Tuple
from schema_types import SchemaLanguage


class Converter:
    """
    Abstract base class for schema converters
    :param name: Name of the converter
    :param service_address: Address of the converter service or path to executable
    :param service_name: Name of the converter service
    :param source_language: Source schema language
    :param target_language: Target schema language
    """

    def __init__(self, name: str, service_address: str, service_name: str, source_language: SchemaLanguage,
                 target_language: SchemaLanguage):
        self.name = name
        self.service_address = service_address
        self.service_name = service_name
        self.source_language = source_language
        self.target_language = target_language

    def convert(self, schema: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")



class ConverterInternal(Converter):
    """
    Internal converter that performs conversion using built-in logic, in Python
    :param name: Name of the converter
    :param service_address: Address of the converter service or path to executable
    :param service_name: Name of the converter service
    :param source_language: Source schema language
    :param target_language: Target schema language
    """
    def __init__(self, name: str, service_address: str, service_name: str, source_language: SchemaLanguage,
                 target_language: SchemaLanguage):
        super().__init__(name, service_address, service_name, source_language, target_language)

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


class ConverterExternalGeneric(ConverterInternal):
    """Generic external converter that can handle multiple conversion types"""

    def __init__(self, name: str, executable_path: str, source_language: SchemaLanguage,
                 target_language: SchemaLanguage,
                 converter_type: str, input_file_raw_suffix: str = None, output_file_raw_suffix: str = None):
        super().__init__(name, executable_path, converter_type, source_language, target_language)
        self.executable_path = executable_path
        self.converter_type = converter_type
        self.input_file_raw_suffix = input_file_raw_suffix
        self.output_file_raw_suffix = output_file_raw_suffix

    def convert(self, schema: str) -> str:
        print(
            f"Calling external {self.converter_type} converter {self.name} for {self.source_language} to {self.target_language}")

        output_file_path = "output_" + self.output_file_raw_suffix if self.output_file_raw_suffix else None
        input_file_raw = self.input_file_raw_suffix is not None

        if input_file_raw:
            # Create temporary file for input schema
            with tempfile.NamedTemporaryFile(mode='w', suffix=self.input_file_raw_suffix, delete=False) as input_file:
                input_file.write(schema)
                input_file_path = input_file.name

        else:
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
                input_data = {
                    "sourceLanguage": self.source_language.value,
                    "targetLanguage": self.target_language.value,
                    "converterName": self.name,
                    "schema": schema
                }
                json.dump(input_data, input_file)
                input_file_path = input_file.name

        try:
            # Run the subprocess with the convert command
            if self.converter_type == "node":
                cmd = self.executable_path.split() + ["convert", input_file_path]

            elif self.converter_type == "java":
                cmd = self.executable_path.split() + ["convert", input_file_path]

            elif self.converter_type == "robot":
                cmd = self.executable_path.split() + ["convert", "-i", input_file_path, "-o", output_file_path]

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

            if output_file_path:
                # Read output from file
                with open(output_file_path, 'r') as output_file:
                    output_data = output_file.read()
                os.unlink(output_file_path)
                return output_data

            else:
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
    return " -> ".join([f"{conv.source_language.value} to {conv.target_language.value} via {conv.service_name}" for conv in path])


def prepare_conversion_results_for_serializing(results: ConversionResults) -> dict:
    serialized_results = {}
    for idx, (success, schema_or_error, path) in enumerate(results):
        path_str = conversion_path_to_string(path)
        serialized_results[f"Attempt {idx + 1}"] = {
            "success": success,
            "schema_or_error": schema_or_error,
            "conversion_path": path_str
        }
    return serialized_results
