
from strenum import StrEnum


class SchemaLanguage(StrEnum):
    LinkMl = "LinkMl"
    MdModels = "MdModels"
    Dtd = "Dtd"
    Xsd = "Xsd"
    JsonSchema = "JsonSchema"
    SHACL_TTL = "SHACL_TTL"
    SHACL_JSON_LD = "SHACL_JSON_LD"
    Owl_TTL = "Owl_TTL"
    Owl_XML = "Owl_XML"
    Owl_OFN = "Owl_OFN",
    OWL_OBO = "OWL_OBO"
    OntologyRdf = "OntologyRdf"
    GraphQL = "GraphQL"
    Protobuf = "Protobuf"
    Shex = "Shex"
    Mermaid = "Mermaid"
    SqlAlchemy = "SqlAlchemy"


# ignore case when comparing
def schema_language_from_string(s: str) -> SchemaLanguage:
    for lang in SchemaLanguage:
        if lang.lower() == s.lower():
            return lang
    raise ValueError(f"Unknown schema language: {s}")


class SchemaFeatureSupport(StrEnum):
    Preserved = "Preserved"
    Approximated = "Approximated"
    Weakened = "Weakened"
    Lost = "Lost"
