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
                timeout=20
            )
        elif converter_type == "java":
            result = subprocess.run(
                ["java", "-jar", executable_path, "list"],
                capture_output=True,
                text=True,
                timeout=20
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
                converter_node = ConverterExternalGeneric(
                    name=info['name'],
                    executable_path=f"node {node_executable}",
                    source_language=SchemaLanguage(info['sourceLanguage']),
                    target_language=SchemaLanguage(info['targetLanguage']),
                    converter_type="node"
                )
                converters.append(converter_node)
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
                converter_java = ConverterExternalGeneric(
                    name=info['name'],
                    executable_path=f"java -jar {java_jar}",
                    source_language=SchemaLanguage(info['sourceLanguage']),
                    target_language=SchemaLanguage(info['targetLanguage']),
                    converter_type="java"
                )
                converters.append(converter_java)
                print(
                    f"Registered Java converter: {info['name']} ({info['sourceLanguage']} -> {info['targetLanguage']})")
            except Exception as e:
                print(f"Failed to register Java converter {info.get('name', 'unknown')}: {e}")
    else:
        print(f"Java converter not found at: {java_jar}")

    # Robot service
    robot_jar = os.path.join(os.path.dirname(__file__), "external_converters", "robot", "robot.jar")
    if os.path.exists(robot_jar):
        print(f"Found Robot converter at: {robot_jar}")
        converter_robot_ttl_to_ofn = ConverterExternalGeneric(
            name="ROBOT OWL TTL TO OWL OFN",
            executable_path=f"java -jar {robot_jar} -vvv",
            source_language=SchemaLanguage.Owl_TTL,
            target_language=SchemaLanguage.Owl_OFN,
            converter_type="robot",
            input_file_raw_suffix=".ttl",
            output_file_raw_suffix=".ofn"
        )
        converter_robot_ttl_to_obo = ConverterExternalGeneric(
            name="ROBOT OWL TTL TO OWL OBO",
            executable_path=f"java -jar {robot_jar} -vvv",
            source_language=SchemaLanguage.Owl_TTL,
            target_language=SchemaLanguage.OWL_OBO,
            converter_type="robot",
            input_file_raw_suffix=".ttl",
            output_file_raw_suffix=".obo"
        )
        converter_robot_ofn_to_ttl = ConverterExternalGeneric(
            name="ROBOT OWL OFN TO OWL TTL",
            executable_path=f"java -jar {robot_jar} -vvv",
            source_language=SchemaLanguage.Owl_OFN,
            target_language=SchemaLanguage.Owl_TTL,
            converter_type="robot",
            input_file_raw_suffix=".ofn",
            output_file_raw_suffix=".ttl"
        )
        converter_robot_obo_to_ttl = ConverterExternalGeneric(
            name="ROBOT OWL Obo TO OWL TTL",
            executable_path=f"java -jar {robot_jar} -vvv",
            source_language=SchemaLanguage.OWL_OBO,
            target_language=SchemaLanguage.Owl_TTL,
            converter_type="robot",
            input_file_raw_suffix=".obo",
            output_file_raw_suffix=".ttl"
        )
        converters.append(converter_robot_ttl_to_ofn)
        converters.append(converter_robot_ttl_to_obo)
        converters.append(converter_robot_ofn_to_ttl)
        converters.append(converter_robot_obo_to_ttl)
        print(f"Registered Robot converters for OWL TTL, OFN, and OBO formats.")
    else:
        print(f"Robot converter not found at: {robot_jar}")

    return converters
