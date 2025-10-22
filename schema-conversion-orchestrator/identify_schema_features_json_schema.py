import json
from typing import List
from schema_types import SchemaFeature


def identify_schema_features_json_schema(schema: str) -> List[SchemaFeature]:
    """Determine which Schema Features are used by a given JSON Schema"""
    try:
        schema_dict = json.loads(schema)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON Schema: {e}")
        return []

    features = set()

    def analyze_schema(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "type":
                    possible_types = value if isinstance(value, list) else [value]
                    if "object" in possible_types:
                        features.add(SchemaFeature.Structural_Hierarchy)
                    if "array" in possible_types:
                        features.add(SchemaFeature.Structural_List)
                    if "null" in possible_types:
                        features.add(SchemaFeature.Domain_Nullability)
                    # elif value in ["string", "number", "integer", "boolean", "null"]:
                    # features.add(SchemaFeature.Primitive_Types)
                elif key == "properties":
                    features.add(SchemaFeature.Structural_Hierarchy)
                    for prop in value.values():
                        analyze_schema(prop)
                elif key == "items":
                    analyze_schema(value)
                elif key in ["oneOf", "anyOf", "allOf"]:
                    features.add(SchemaFeature.Structural_Composition)
                    for sub_schema in value:
                        analyze_schema(sub_schema)
                elif key == "$ref":
                    features.add(SchemaFeature.Structural_References)
                elif key in ["minimum", "maximum", "minLength", "maxLength", "pattern"]:
                    features.add(SchemaFeature.Constraint_Datatype)
                elif key in ["minItems", "maxItems", "uniqueItems"]:
                    features.add(SchemaFeature.Constraint_Cardinality)
                elif key in ["if", "then", "else"]:
                    features.add(SchemaFeature.Constraint_Logical)
                elif key == "not":
                    features.add(SchemaFeature.Constraint_Logical)
                elif key == "additionalProperties":
                    features.add(SchemaFeature.Constraint_ClosedShapes)
                elif key == "const":
                    features.add(SchemaFeature.Semantic_FixedValues)
                elif key == "enum":
                    features.add(SchemaFeature.Semantic_FixedValues)
                elif key == "examples":
                    features.add(SchemaFeature.Semantic_Examples)
                elif key == "description":
                    features.add(SchemaFeature.Semantic_Comments)
                elif key == "title":
                    features.add(SchemaFeature.Semantic_Labels)
                elif key == "default":
                    features.add(SchemaFeature.Semantic_Defaults)
                elif key == "deprecated":
                    features.add(SchemaFeature.Semantic_Deprecated)
                elif key == "uniqueItems":
                    features.add(SchemaFeature.Semantic_IdentityConstraints)
                elif key == "format":
                    features.add(SchemaFeature.Constraint_Datatype)

                analyze_schema(value)
        elif isinstance(node, list):
            for item in node:
                analyze_schema(item)

    analyze_schema(schema_dict)

    return list(features)
