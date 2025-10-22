import json

from converter import ConverterInternal
from schema_types import SchemaLanguage

from mdmodels_core import DataModel, Templates


class ConverterFromMdModels(ConverterInternal):
    def __init__(self, target_format: SchemaLanguage):
        super().__init__(
            name="MdModels Templates: " + target_format.name,
            service_address="internal",
            service_name="FlaskApp",
            source_format=SchemaLanguage.MdModels,
            target_format=target_format,
            supported_features=None
        )

    def converter_logic(self, schema: str) -> str:
        dm = DataModel.from_markdown_string(schema)
        try:
            if self.target_format == SchemaLanguage.Protobuf:
                return dm.convert_to(Templates.Protobuf)
            elif self.target_format == SchemaLanguage.Xsd:
                return dm.convert_to(Templates.XmlSchema)
            elif self.target_format == SchemaLanguage.PythonPydantic:
                return dm.convert_to(Templates.PythonPydantic)
            elif self.target_format == SchemaLanguage.JsonSchema:
                return dm.convert_to(Templates.JsonSchema)  # test difference with JsonSchemaAll
            elif self.target_format == SchemaLanguage.GraphQL:
                return dm.convert_to(Templates.Graphql)
            elif self.target_format == SchemaLanguage.Julia_MdModels:
                return dm.convert_to(Templates.Julia)
            elif self.target_format == SchemaLanguage.Mermaid:
                return dm.convert_to(Templates.Mermaid)
            elif self.target_format == SchemaLanguage.SHACL:
                return dm.convert_to(Templates.Shacl)
            elif self.target_format == SchemaLanguage.Rust_MdModels:
                return dm.convert_to(Templates.Rust)
            elif self.target_format == SchemaLanguage.TypeScript_MdModels:
                return dm.convert_to(Templates.Typescript)
            elif self.target_format == SchemaLanguage.Shex:
                return dm.convert_to(Templates.Shex)
            else:
                raise ValueError(f"Unsupported target format: {self.target_format}")
        except Exception as e:
            raise RuntimeError(f"Error during conversion to {self.target_format}: {str(e)}.")

    def validate_input(self, schema: str) -> bool:
        # Implement validation logic for JSON Schema
        return True

    def validate_output(self, schema: str) -> bool:
        # Implement validation logic for LinkML schema
        return True


class ConverterJsonSchemaToMdModels(ConverterInternal):
    def __init__(self):
        super().__init__(
            name="MdModels DataModel from JsonSchema",
            service_address="internal",
            service_name="FlaskApp",
            source_format=SchemaLanguage.JsonSchema,
            target_format=SchemaLanguage.MdModels,
            supported_features=None
        )

    def converter_logic(self, schema: str) -> str:
        schema_dict: dict = json.loads(schema)
        # Markdown specific clean-up
        schema_dict.pop("$schema", None)
        # schema_dict.pop("$id", None)

        # if no title is present, add a dummy title
        if "title" not in schema_dict:
            schema_dict["title"] = "ImportedSchema"

        schema = json.dumps(schema_dict)

        dm = DataModel.from_json_schema_string(schema)
        return dm.convert_to(Templates.Markdown)

    def validate_input(self, schema: str) -> bool:
        # Implement validation logic for JSON Schema
        return True

    def validate_output(self, schema: str) -> bool:
        # Implement validation logic for LinkML schema
        return True
