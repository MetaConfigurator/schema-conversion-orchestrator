import json

from schema_conversion_orchestrator.converters.base import ConverterInternal, get_package_version
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


class ConverterJsonSchemaToShaclCitius(ConverterInternal):
    """JSON Schema -> SHACL via citiususc/jsonschema2shacl.

    Recursively traverses the schema, emitting SHACL NodeShapes /
    PropertyShapes with rdflib.
    """

    def __init__(self) -> None:
        super().__init__(
            name="jsonschema2shacl",
            service_address="internal",
            service_name="FlaskApp",
            source_language=SchemaLanguage.JsonSchema,
            target_language=SchemaLanguage.SHACL_TTL,
            library="jsonschema2shacl",
            library_version=get_package_version("jsonschema2shacl"),
            library_url="https://github.com/citiususc/jsonschema2shacl",
        )

    def converter_logic(self, schema: str) -> str:
        # `parse_json_schema` only json-loads a file, so feed the parsed dict
        # straight into the translator and avoid a temp file round-trip.
        from jsonschema2shacl.json_schema_to_shacl import JsonSchemaToShacl

        parsed = json.loads(schema)
        converter = JsonSchemaToShacl()
        converter.translate(parsed)
        return converter.shacl.serialize(format="turtle")

    def validate_input(self, schema: str) -> bool:
        return True

    def validate_output(self, schema: str) -> bool:
        return True
