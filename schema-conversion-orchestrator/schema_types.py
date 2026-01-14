
from strenum import StrEnum


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
    PythonLinkMl = "Python_LinkMl"
    PythonPydantic = "Python_Pydantic"
    Julia_MdModels = "Julia_MdModels"
    Java_LinkMl = "Java_LinkMl"
    Mermaid = "Mermaid"
    Rust_MdModels = "Rust_MdModels"
    TypeScript_MdModels = "TypeScript_MdModels"
    Shex = "Shex"
    Docs_LinkMl = "Docs_LinkMl"
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
