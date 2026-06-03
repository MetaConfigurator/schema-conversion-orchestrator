import json
import os
import subprocess
import tempfile

from schema_conversion_orchestrator.converters.base import ConverterInternal
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


class ConverterExternalGeneric(ConverterInternal):
    """Generic external converter that can handle multiple conversion types."""

    def __init__(
        self,
        name: str,
        executable_path: str,
        source_language: SchemaLanguage,
        target_language: SchemaLanguage,
        converter_type: str,
        input_file_raw_suffix: str = None,
        output_file_raw_suffix: str = None,
    ) -> None:
        super().__init__(name, executable_path, converter_type, source_language, target_language)
        self.executable_path = executable_path
        self.converter_type = converter_type
        self.input_file_raw_suffix = input_file_raw_suffix
        self.output_file_raw_suffix = output_file_raw_suffix

    def convert(self, schema: str) -> str:
        print(
            f"Calling external {self.converter_type} converter {self.name} "
            f"for {self.source_language} to {self.target_language}"
        )

        output_file_path = "output_" + self.output_file_raw_suffix if self.output_file_raw_suffix else None
        input_file_raw = self.input_file_raw_suffix is not None

        if input_file_raw:
            with tempfile.NamedTemporaryFile(mode="w", suffix=self.input_file_raw_suffix, delete=False) as input_file:
                input_file.write(schema)
                input_file_path = input_file.name
        else:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as input_file:
                input_data = {
                    "sourceLanguage": self.source_language.value,
                    "targetLanguage": self.target_language.value,
                    "converterName": self.name,
                    "schema": schema,
                }
                json.dump(input_data, input_file)
                input_file_path = input_file.name

        try:
            if self.converter_type == "robot":
                cmd = self.executable_path.split() + ["convert", "-i", input_file_path, "-o", output_file_path]
            elif self.converter_type == "shacl-bridge":
                cmd = self.executable_path.split() + ["-i", input_file_path, "-o", output_file_path]
            else:
                cmd = self.executable_path.split() + ["convert", input_file_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"External converter failed with exit code {result.returncode}: {result.stderr}")

            if output_file_path:
                with open(output_file_path) as output_file:
                    output_data = output_file.read()
                os.unlink(output_file_path)
                return output_data

            try:
                output_data = json.loads(result.stdout)
                if "error" in output_data and output_data["error"]:
                    raise RuntimeError(f"Converter returned error: {output_data['error']}")
                if "schema" not in output_data:
                    raise RuntimeError("Converter output missing 'schema' field")
                return output_data["schema"]
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse converter output as JSON: {e}")

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"External converter {self.name} timed out")
        finally:
            os.unlink(input_file_path)
