
from strenum import StrEnum


class SchemaLanguage(StrEnum):
    LinkMl = "LinkMl"
    MdModels = "MdModels"
    Dtd = "Dtd"
    Xsd = "Xsd"
    JsonSchema = "JsonSchema"
    SHACL = "SHACL"
    Owl = "Owl"
    OntologyRdf = "OntologyRdf"
    GraphQL = "GraphQL"
    Protobuf = "Protobuf"
    Shex = "Shex"
    Mermaid = "Mermaid"
    SqlAlchemy = "SqlAlchemy"
    # JsonLD = "JsonLD"
    # PythonLinkMl = "Python_LinkMl"
    # PythonPydantic = "Python_Pydantic"
    # Julia_MdModels = "Julia_MdModels"
    # Java_LinkMl = "Java_LinkMl"
    # Rust_MdModels = "Rust_MdModels"
    # TypeScript_MdModels = "TypeScript_MdModels"
    # Docs_LinkMl = "Docs_LinkMl"


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
