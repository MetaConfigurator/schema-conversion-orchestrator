from enum import Enum
from typing import Optional, Any, List, Union, TypeVar, Type, cast, Callable


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


class ConstraintCardinality(Enum):
    APPROXIMATED = "approximated"
    LOST = "lost"
    PRESERVED = "preserved"
    WEAKENED = "weakened"


class SchemaFeatures:
    constraint_cardinality: ConstraintCardinality
    constraint_closed_shapes: ConstraintCardinality
    constraint_datatype: ConstraintCardinality
    constraint_dependencies: ConstraintCardinality
    constraint_enumerations: ConstraintCardinality
    constraint_logical: ConstraintCardinality
    domain_inheritance_restrictions: ConstraintCardinality
    domain_nullability: ConstraintCardinality
    domain_ordering: ConstraintCardinality
    domain_polymorphism: ConstraintCardinality
    domain_scoping: ConstraintCardinality
    domain_typed_links: ConstraintCardinality
    graph_node_shapes: ConstraintCardinality
    graph_ontology_alignment: ConstraintCardinality
    graph_path_expressions: ConstraintCardinality
    graph_property_shapes: ConstraintCardinality
    graph_target_declarations: ConstraintCardinality
    graph_ur_is: ConstraintCardinality
    graph_world_assumption: ConstraintCardinality
    runtime_custom_validation: Optional[ConstraintCardinality]
    runtime_extensibility: Optional[ConstraintCardinality]
    runtime_external_references: Optional[ConstraintCardinality]
    semantic_comments: ConstraintCardinality
    semantic_defaults: ConstraintCardinality
    semantic_deprecated: ConstraintCardinality
    semantic_examples: ConstraintCardinality
    semantic_fixed_values: ConstraintCardinality
    semantic_identity_constraints: ConstraintCardinality
    semantic_labels: ConstraintCardinality
    structural_anonymous_types: ConstraintCardinality
    structural_attributes_elements: ConstraintCardinality
    structural_composition: ConstraintCardinality
    structural_hierarchy: ConstraintCardinality
    structural_namespaces: ConstraintCardinality
    structural_references: ConstraintCardinality
    structural_union_intersection: ConstraintCardinality
    structural_list: Any

    def __init__(self, constraint_cardinality: ConstraintCardinality, constraint_closed_shapes: ConstraintCardinality, constraint_datatype: ConstraintCardinality, constraint_dependencies: ConstraintCardinality, constraint_enumerations: ConstraintCardinality, constraint_logical: ConstraintCardinality, domain_inheritance_restrictions: ConstraintCardinality, domain_nullability: ConstraintCardinality, domain_ordering: ConstraintCardinality, domain_polymorphism: ConstraintCardinality, domain_scoping: ConstraintCardinality, domain_typed_links: ConstraintCardinality, graph_node_shapes: ConstraintCardinality, graph_ontology_alignment: ConstraintCardinality, graph_path_expressions: ConstraintCardinality, graph_property_shapes: ConstraintCardinality, graph_target_declarations: ConstraintCardinality, graph_ur_is: ConstraintCardinality, graph_world_assumption: ConstraintCardinality, runtime_custom_validation: Optional[ConstraintCardinality], runtime_extensibility: Optional[ConstraintCardinality], runtime_external_references: Optional[ConstraintCardinality], semantic_comments: ConstraintCardinality, semantic_defaults: ConstraintCardinality, semantic_deprecated: ConstraintCardinality, semantic_examples: ConstraintCardinality, semantic_fixed_values: ConstraintCardinality, semantic_identity_constraints: ConstraintCardinality, semantic_labels: ConstraintCardinality, structural_anonymous_types: ConstraintCardinality, structural_attributes_elements: ConstraintCardinality, structural_composition: ConstraintCardinality, structural_hierarchy: ConstraintCardinality, structural_namespaces: ConstraintCardinality, structural_references: ConstraintCardinality, structural_union_intersection: ConstraintCardinality, structural_list: Any) -> None:
        self.constraint_cardinality = constraint_cardinality
        self.constraint_closed_shapes = constraint_closed_shapes
        self.constraint_datatype = constraint_datatype
        self.constraint_dependencies = constraint_dependencies
        self.constraint_enumerations = constraint_enumerations
        self.constraint_logical = constraint_logical
        self.domain_inheritance_restrictions = domain_inheritance_restrictions
        self.domain_nullability = domain_nullability
        self.domain_ordering = domain_ordering
        self.domain_polymorphism = domain_polymorphism
        self.domain_scoping = domain_scoping
        self.domain_typed_links = domain_typed_links
        self.graph_node_shapes = graph_node_shapes
        self.graph_ontology_alignment = graph_ontology_alignment
        self.graph_path_expressions = graph_path_expressions
        self.graph_property_shapes = graph_property_shapes
        self.graph_target_declarations = graph_target_declarations
        self.graph_ur_is = graph_ur_is
        self.graph_world_assumption = graph_world_assumption
        self.runtime_custom_validation = runtime_custom_validation
        self.runtime_extensibility = runtime_extensibility
        self.runtime_external_references = runtime_external_references
        self.semantic_comments = semantic_comments
        self.semantic_defaults = semantic_defaults
        self.semantic_deprecated = semantic_deprecated
        self.semantic_examples = semantic_examples
        self.semantic_fixed_values = semantic_fixed_values
        self.semantic_identity_constraints = semantic_identity_constraints
        self.semantic_labels = semantic_labels
        self.structural_anonymous_types = structural_anonymous_types
        self.structural_attributes_elements = structural_attributes_elements
        self.structural_composition = structural_composition
        self.structural_hierarchy = structural_hierarchy
        self.structural_namespaces = structural_namespaces
        self.structural_references = structural_references
        self.structural_union_intersection = structural_union_intersection
        self.structural_list = structural_list

    @staticmethod
    def from_dict(obj: Any) -> 'SchemaFeatures':
        assert isinstance(obj, dict)
        constraint_cardinality = ConstraintCardinality(obj.get("Constraint_Cardinality"))
        constraint_closed_shapes = ConstraintCardinality(obj.get("Constraint_ClosedShapes"))
        constraint_datatype = ConstraintCardinality(obj.get("Constraint_Datatype"))
        constraint_dependencies = ConstraintCardinality(obj.get("Constraint_Dependencies"))
        constraint_enumerations = ConstraintCardinality(obj.get("Constraint_Enumerations"))
        constraint_logical = ConstraintCardinality(obj.get("Constraint_Logical"))
        domain_inheritance_restrictions = ConstraintCardinality(obj.get("Domain_InheritanceRestrictions"))
        domain_nullability = ConstraintCardinality(obj.get("Domain_Nullability"))
        domain_ordering = ConstraintCardinality(obj.get("Domain_Ordering"))
        domain_polymorphism = ConstraintCardinality(obj.get("Domain_Polymorphism"))
        domain_scoping = ConstraintCardinality(obj.get("Domain_Scoping"))
        domain_typed_links = ConstraintCardinality(obj.get("Domain_TypedLinks"))
        graph_node_shapes = ConstraintCardinality(obj.get("Graph_NodeShapes"))
        graph_ontology_alignment = ConstraintCardinality(obj.get("Graph_OntologyAlignment"))
        graph_path_expressions = ConstraintCardinality(obj.get("Graph_PathExpressions"))
        graph_property_shapes = ConstraintCardinality(obj.get("Graph_PropertyShapes"))
        graph_target_declarations = ConstraintCardinality(obj.get("Graph_TargetDeclarations"))
        graph_ur_is = ConstraintCardinality(obj.get("Graph_URIs"))
        graph_world_assumption = ConstraintCardinality(obj.get("Graph_WorldAssumption"))
        runtime_custom_validation = from_union([ConstraintCardinality, from_none], obj.get("Runtime_CustomValidation"))
        runtime_extensibility = from_union([ConstraintCardinality, from_none], obj.get("Runtime_Extensibility"))
        runtime_external_references = from_union([ConstraintCardinality, from_none], obj.get("Runtime_ExternalReferences"))
        semantic_comments = ConstraintCardinality(obj.get("Semantic_Comments"))
        semantic_defaults = ConstraintCardinality(obj.get("Semantic_Defaults"))
        semantic_deprecated = ConstraintCardinality(obj.get("Semantic_Deprecated"))
        semantic_examples = ConstraintCardinality(obj.get("Semantic_Examples"))
        semantic_fixed_values = ConstraintCardinality(obj.get("Semantic_FixedValues"))
        semantic_identity_constraints = ConstraintCardinality(obj.get("Semantic_IdentityConstraints"))
        semantic_labels = ConstraintCardinality(obj.get("Semantic_Labels"))
        structural_anonymous_types = ConstraintCardinality(obj.get("Structural_AnonymousTypes"))
        structural_attributes_elements = ConstraintCardinality(obj.get("Structural_AttributesElements"))
        structural_composition = ConstraintCardinality(obj.get("Structural_Composition"))
        structural_hierarchy = ConstraintCardinality(obj.get("Structural_Hierarchy"))
        structural_namespaces = ConstraintCardinality(obj.get("Structural_Namespaces"))
        structural_references = ConstraintCardinality(obj.get("Structural_References"))
        structural_union_intersection = ConstraintCardinality(obj.get("Structural_UnionIntersection"))
        structural_list = obj.get("Structural_List")
        return SchemaFeatures(constraint_cardinality, constraint_closed_shapes, constraint_datatype, constraint_dependencies, constraint_enumerations, constraint_logical, domain_inheritance_restrictions, domain_nullability, domain_ordering, domain_polymorphism, domain_scoping, domain_typed_links, graph_node_shapes, graph_ontology_alignment, graph_path_expressions, graph_property_shapes, graph_target_declarations, graph_ur_is, graph_world_assumption, runtime_custom_validation, runtime_extensibility, runtime_external_references, semantic_comments, semantic_defaults, semantic_deprecated, semantic_examples, semantic_fixed_values, semantic_identity_constraints, semantic_labels, structural_anonymous_types, structural_attributes_elements, structural_composition, structural_hierarchy, structural_namespaces, structural_references, structural_union_intersection, structural_list)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Constraint_Cardinality"] = to_enum(ConstraintCardinality, self.constraint_cardinality)
        result["Constraint_ClosedShapes"] = to_enum(ConstraintCardinality, self.constraint_closed_shapes)
        result["Constraint_Datatype"] = to_enum(ConstraintCardinality, self.constraint_datatype)
        result["Constraint_Dependencies"] = to_enum(ConstraintCardinality, self.constraint_dependencies)
        result["Constraint_Enumerations"] = to_enum(ConstraintCardinality, self.constraint_enumerations)
        result["Constraint_Logical"] = to_enum(ConstraintCardinality, self.constraint_logical)
        result["Domain_InheritanceRestrictions"] = to_enum(ConstraintCardinality, self.domain_inheritance_restrictions)
        result["Domain_Nullability"] = to_enum(ConstraintCardinality, self.domain_nullability)
        result["Domain_Ordering"] = to_enum(ConstraintCardinality, self.domain_ordering)
        result["Domain_Polymorphism"] = to_enum(ConstraintCardinality, self.domain_polymorphism)
        result["Domain_Scoping"] = to_enum(ConstraintCardinality, self.domain_scoping)
        result["Domain_TypedLinks"] = to_enum(ConstraintCardinality, self.domain_typed_links)
        result["Graph_NodeShapes"] = to_enum(ConstraintCardinality, self.graph_node_shapes)
        result["Graph_OntologyAlignment"] = to_enum(ConstraintCardinality, self.graph_ontology_alignment)
        result["Graph_PathExpressions"] = to_enum(ConstraintCardinality, self.graph_path_expressions)
        result["Graph_PropertyShapes"] = to_enum(ConstraintCardinality, self.graph_property_shapes)
        result["Graph_TargetDeclarations"] = to_enum(ConstraintCardinality, self.graph_target_declarations)
        result["Graph_URIs"] = to_enum(ConstraintCardinality, self.graph_ur_is)
        result["Graph_WorldAssumption"] = to_enum(ConstraintCardinality, self.graph_world_assumption)
        if self.runtime_custom_validation is not None:
            result["Runtime_CustomValidation"] = from_union([lambda x: to_enum(ConstraintCardinality, x), from_none], self.runtime_custom_validation)
        if self.runtime_extensibility is not None:
            result["Runtime_Extensibility"] = from_union([lambda x: to_enum(ConstraintCardinality, x), from_none], self.runtime_extensibility)
        if self.runtime_external_references is not None:
            result["Runtime_ExternalReferences"] = from_union([lambda x: to_enum(ConstraintCardinality, x), from_none], self.runtime_external_references)
        result["Semantic_Comments"] = to_enum(ConstraintCardinality, self.semantic_comments)
        result["Semantic_Defaults"] = to_enum(ConstraintCardinality, self.semantic_defaults)
        result["Semantic_Deprecated"] = to_enum(ConstraintCardinality, self.semantic_deprecated)
        result["Semantic_Examples"] = to_enum(ConstraintCardinality, self.semantic_examples)
        result["Semantic_FixedValues"] = to_enum(ConstraintCardinality, self.semantic_fixed_values)
        result["Semantic_IdentityConstraints"] = to_enum(ConstraintCardinality, self.semantic_identity_constraints)
        result["Semantic_Labels"] = to_enum(ConstraintCardinality, self.semantic_labels)
        result["Structural_AnonymousTypes"] = to_enum(ConstraintCardinality, self.structural_anonymous_types)
        result["Structural_AttributesElements"] = to_enum(ConstraintCardinality, self.structural_attributes_elements)
        result["Structural_Composition"] = to_enum(ConstraintCardinality, self.structural_composition)
        result["Structural_Hierarchy"] = to_enum(ConstraintCardinality, self.structural_hierarchy)
        result["Structural_Namespaces"] = to_enum(ConstraintCardinality, self.structural_namespaces)
        result["Structural_References"] = to_enum(ConstraintCardinality, self.structural_references)
        result["Structural_UnionIntersection"] = to_enum(ConstraintCardinality, self.structural_union_intersection)
        result["Structural_List"] = self.structural_list
        return result


class SchemaLanguageClass:
    name: str
    schema_features: SchemaFeatures

    def __init__(self, name: str, schema_features: SchemaFeatures) -> None:
        self.name = name
        self.schema_features = schema_features

    @staticmethod
    def from_dict(obj: Any) -> 'SchemaLanguageClass':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        schema_features = SchemaFeatures.from_dict(obj.get("schemaFeatures"))
        return SchemaLanguageClass(name, schema_features)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["schemaFeatures"] = to_class(SchemaFeatures, self.schema_features)
        return result


class SchemaLanguageFeatures:
    schema_languages: Optional[List[Optional[Union[float, int, bool, str, List[Any], SchemaLanguageClass]]]]

    def __init__(self, schema_languages: Optional[List[Optional[Union[float, int, bool, str, List[Any], SchemaLanguageClass]]]]) -> None:
        self.schema_languages = schema_languages

    @staticmethod
    def from_dict(obj: Any) -> 'SchemaLanguageFeatures':
        assert isinstance(obj, dict)
        schema_languages = from_union([lambda x: from_list(lambda x: from_union([from_none, from_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), SchemaLanguageClass.from_dict], x), x), from_none], obj.get("schemaLanguages"))
        return SchemaLanguageFeatures(schema_languages)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.schema_languages is not None:
            result["schemaLanguages"] = from_union([lambda x: from_list(lambda x: from_union([from_none, to_float, from_int, from_bool, from_str, lambda x: from_list(lambda x: x, x), lambda x: to_class(SchemaLanguageClass, x)], x), x), from_none], self.schema_languages)
        return result


def schema_language_features_from_dict(s: Any) -> SchemaLanguageFeatures:
    return SchemaLanguageFeatures.from_dict(s)


def schema_language_features_to_dict(x: SchemaLanguageFeatures) -> Any:
    return to_class(SchemaLanguageFeatures, x)
