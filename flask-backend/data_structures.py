import requests
from strenum import StrEnum
from typing import List


class SchemaLanguage(StrEnum):
    JsonSchema = "JsonSchema"
    MdModels = "MdModels"
    LinkMl = "LinkMl"
    Dtd = "Dtd"
    OntologyRdf = "OntologyRdf"
    Xsd = "Xsd"
    Owl = "Owl"
    Protobuf = "Protobuf"
    GraphQL = "GraphQL"
    JsonLD = "JsonLD"
    SHACL = "SHACL"
    Python = "Python"

class SchemaFeature(StrEnum):
    Comments = "Comments"
    Hierarchy = "Hierarchy"
    References = "References"
    Conditions = "Conditions"
    Constraints = "Constraints"
    Properties = "Properties"
    Attributes = "Attributes"
    Composition = "Composition"
    Negation = "Negation"


class Converter:
    def __init__(self, name: str, service_address: str, source_format: SchemaLanguage, target_format: SchemaLanguage, supported_features: List[SchemaFeature]):
        self.name = name
        self.service_address = service_address
        self.source_format = source_format
        self.target_format = target_format
        self.supported_features = supported_features

    def convert(self, schema: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")

class ConverterExternal(Converter):

    def __init__(self, name: str, service_address: str, source_format: SchemaLanguage, target_format: SchemaLanguage, supported_features: List[SchemaFeature]):
        super().__init__(name, service_address, source_format, target_format, supported_features)
    def convert(self, schema: str) -> str:
        r = requests.post(self.service_address + "/convert", json={
            "sourceFormat": self.source_format,
            "targetFormat": self.target_format,
            "schema": schema
        })
        return r.json()["schema"]


class ConverterInternal(Converter):
    def __init__(self, name: str, service_address: str, source_format: SchemaLanguage, target_format: SchemaLanguage, supported_features: List[SchemaFeature]):
        super().__init__(name, service_address, source_format, target_format, supported_features)

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



ConversionGraph = dict[str, list[Converter]]
SchemaFeatures = list[SchemaFeature]
ConversionPath = List[Converter]
ConversionPaths = List[ConversionPath]