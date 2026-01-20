import json
import os
import subprocess
from typing import List, Dict

from converter import Converter, ConverterExternalGeneric
from schema_types import SchemaLanguage


def get_external_converter_info(executable_path: str, converter_type: str) -> List[Dict]:
    """Get available converters from an external service"""
    try:
        if converter_type == "node":
            result = subprocess.run(
                ["node", executable_path, "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
        elif converter_type == "java":
            result = subprocess.run(
                ["java", "-jar", executable_path, "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            return []

        if result.returncode == 0:
            print("External converter info:", result.stdout)
            output_data = json.loads(result.stdout)
            return output_data.get("converters", [])
        else:
            print(f"Return code: {result.stdout}")
            print(f"Failed to get converter info from {executable_path}: {result.stderr}")
            return []

    except Exception as e:
        print(f"Error getting converter info from {executable_path}: {e}")
        return []


def register_external_converters() -> List[Converter]:
    """Register all external subprocess-based converters"""
    converters = []

    # Node.js service
    node_executable = os.path.join(os.path.dirname(__file__), "external_converters", "node", "dist", "index.js")
    if os.path.exists(node_executable):
        print(f"Found Node.js converter at: {node_executable}")
        converter_infos = get_external_converter_info(node_executable, "node")

        for info in converter_infos:
            try:
                converter = ConverterExternalGeneric(
                    name=info['name'],
                    executable_path=f"node {node_executable}",
                    source_language=SchemaLanguage(info['sourceLanguage']),
                    target_language=SchemaLanguage(info['targetLanguage']),
                    converter_type="node"
                )
                converters.append(converter)
                print(
                    f"Registered Node.js converter: {info['name']} ({info['sourceLanguage']} -> {info['targetLanguage']})")
            except Exception as e:
                print(f"Failed to register Node.js converter {info.get('name', 'unknown')}: {e}")
    else:
        print(f"Node.js converter not found at: {node_executable}")

    # Java service
    java_jar = os.path.join(os.path.dirname(__file__), "external_converters", "java", "converter.jar")
    if os.path.exists(java_jar):
        print(f"Found Java converter at: {java_jar}")
        converter_infos = get_external_converter_info(java_jar, "java")
        print("Java converter infos:", converter_infos)
        for info in converter_infos:
            try:
                converter = ConverterExternalGeneric(
                    name=info['name'],
                    executable_path=f"java -jar {java_jar}",
                    source_language=SchemaLanguage(info['sourceLanguage']),
                    target_language=SchemaLanguage(info['targetLanguage']),
                    converter_type="java"
                )
                converters.append(converter)
                print(
                    f"Registered Java converter: {info['name']} ({info['sourceLanguage']} -> {info['targetLanguage']})")
            except Exception as e:
                print(f"Failed to register Java converter {info.get('name', 'unknown')}: {e}")
    else:
        print(f"Java converter not found at: {java_jar}")

    return converters
