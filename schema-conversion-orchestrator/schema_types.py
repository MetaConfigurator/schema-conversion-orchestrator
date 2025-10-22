from typing import Dict

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


class SchemaFeature(StrEnum):
    # Structural Features
    Structural_Hierarchy = "Structural_Hierarchy"  # Inheritance, type derivation
    Structural_List = "Structural_List"
    Structural_Composition = "Structural_Composition"  # allOf, anyOf, oneOf, choice, sequence
    Structural_References = "Structural_References"  # ref, include, import
    Structural_Namespaces = "Structural_Namespaces"  # XML, RDF, SHACL
    Structural_AttributesElements = "Structural_AttributesElements"  # XML attrs vs elements
    Structural_UnionIntersection = "Structural_UnionIntersection"
    Structural_AnonymousTypes = "Structural_AnonymousTypes"  # inline types

    # Constraints & Conditions
    Constraint_Cardinality = "Constraint_Cardinality"  # min/maxOccurs, min/maxCount
    Constraint_Datatype = "Constraint_Datatype"  # regex, numeric ranges, formats
    Constraint_Logical = "Constraint_Logical"  # negation, if-then-else, sh:or/and
    Constraint_Enumerations = "Constraint_Enumerations"
    Constraint_Dependencies = "Constraint_Dependencies"
    Constraint_ClosedShapes = "Constraint_ClosedShapes"  # additionalProperties allowed

    # Semantics & Meaning
    Semantic_Comments = "Semantic_Comments"  # documentation, annotations
    Semantic_Labels = "Semantic_Labels"  # titles, names, human-readable metadata
    Semantic_Defaults = "Semantic_Defaults"
    Semantic_FixedValues = "Semantic_FixedValues"
    Semantic_Examples = "Semantic_Examples"
    Semantic_Deprecated = "Semantic_Deprecated"  # status flags, deprecated
    Semantic_IdentityConstraints = "Semantic_IdentityConstraints"  # unique, key, keyref

    # Graph / RDF-Oriented Features
    Graph_NodeShapes = "Graph_NodeShapes"
    Graph_PropertyShapes = "Graph_PropertyShapes"
    Graph_PathExpressions = "Graph_PathExpressions"
    Graph_WorldAssumption = "Graph_WorldAssumption"  # closed vs open world
    Graph_TargetDeclarations = "Graph_TargetDeclarations"
    Graph_OntologyAlignment = "Graph_OntologyAlignment"
    Graph_URIs = "Graph_URIs"

    # Domain-specific Extras
    Domain_Ordering = "Domain_Ordering"  # sequence, list order
    Domain_Nullability = "Domain_Nullability"  # nullable vs non-null
    Domain_Scoping = "Domain_Scoping"  # local vs global declarations
    Domain_TypedLinks = "Domain_TypedLinks"  # relations, references
    Domain_Polymorphism = "Domain_Polymorphism"  # interfaces, substitution groups
    Domain_InheritanceRestrictions = "Domain_InheritanceRestrictions"  # restrictions/subclass limits


SchemaFeatures = Dict[SchemaFeature, SchemaFeatureSupport]

SchemaLanguagesFeatures = Dict[SchemaLanguage, SchemaFeatures]