from enum import StrEnum
from typing import List


class SchemaFormat(StrEnum):
    JsonSchema = "JsonSchema"
    MdModels = "MdModels"
    LinkMl = "LinkMl"
    Dtd = "Dtd"
    OntologyRdf = "OntologyRdf"
    Xsd = "Xsd"

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
    def __init__(self, serviceAddress: str, sourceFormat: SchemaFormat, targetFormat: SchemaFormat, supportedFeatures: List[SchemaFeature]):
        self.serviceAddress = serviceAddress
        self.sourceFormat = sourceFormat
        self.targetFormat = targetFormat
        self.supportedFeatures = supportedFeatures