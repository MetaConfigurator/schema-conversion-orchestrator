import json
import tempfile
from typing import Dict, Type

import schema_automator
from linkml.utils.generator import Generator
from linkml_runtime import SchemaView
from linkml_runtime.loaders import yaml_loader

from data_structures import ConverterInternal, SchemaFeature, SchemaLanguage

from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml.generators.protogen import ProtoGenerator
from linkml.generators.graphqlgen import GraphqlGenerator
from linkml.generators.jsonldgen import JSONLDGenerator
from linkml.generators.shexgen import ShExGenerator
from linkml.generators.shaclgen import ShaclGenerator
from linkml.generators.owlgen import OwlSchemaGenerator
from linkml.generators.docgen import DocGenerator
from linkml.generators.pythongen import PythonGenerator
from linkml.generators.sqlalchemygen import SQLAlchemyGenerator


class ConverterLinkMlToJsonSchema(ConverterInternal):
    def __init__(self):
        super().__init__(
            name="LinkML JsonSchemaGenerator",
            service_address="internal",
            source_format=SchemaLanguage.LinkMl,
            target_format=SchemaLanguage.JsonSchema,
            supported_features=[
                SchemaFeature.Comments,
                SchemaFeature.Hierarchy,
                SchemaFeature.References,
                SchemaFeature.Constraints,
                SchemaFeature.Properties,
                SchemaFeature.Attributes,
                SchemaFeature.Composition
            ]
        )

    def converter_logic(self, schema: str) -> str:
        with tempfile.NamedTemporaryFile("w+", suffix=".yaml") as f:
            f.write(schema)
            f.flush()
            json_schema = JsonSchemaGenerator(f.name).serialize()
        return json_schema

    def validate_input(self, schema: str) -> bool:
        # Implement validation logic for LinkML schema
        return True

    def validate_output(self, schema: str) -> bool:
        # Implement validation logic for JSON Schema
        return True

class ConverterFromLinkMl(ConverterInternal):
    def __init__(self, target_format: SchemaLanguage):
        super().__init__(
            name="LinkML " + target_format.name + " Generator",
            service_address="internal",
            source_format=SchemaLanguage.LinkMl,
            target_format=target_format,
            supported_features=[
                SchemaFeature.Comments,
                SchemaFeature.Hierarchy,
                SchemaFeature.References,
                SchemaFeature.Constraints,
                SchemaFeature.Properties,
                SchemaFeature.Attributes,
                SchemaFeature.Composition
            ]
        )

    def converter_logic(self, schema: str) -> str:
        # Save schema to a temporary file
        with tempfile.NamedTemporaryFile("w+", suffix=".yaml") as f:
            f.write(schema)
            f.flush()

            schema_path = f.name

            # Pick generator based on target format
            fmt = self.target_format

            gen_map: Dict[SchemaLanguage, Type[Generator]] = {
                SchemaLanguage.JsonSchema: JsonSchemaGenerator,
                SchemaLanguage.Protobuf: ProtoGenerator,
                SchemaLanguage.GraphQL: GraphqlGenerator,
                SchemaLanguage.JsonLD: JSONLDGenerator,
                SchemaLanguage.SHACL: ShaclGenerator,
                SchemaLanguage.Owl: OwlSchemaGenerator,
                #"Markdown": DocGenerator,
                SchemaLanguage.Python: PythonGenerator,
                #"SQLAlchemy": SQLAlchemyGenerator
            }
            if fmt not in gen_map:
                raise ValueError(f"Unsupported target format: {fmt}")

            try:
                GeneratorClass: Type[Generator] = gen_map[fmt]
                gen = GeneratorClass(schema_path)
                return gen.serialize()
            except Exception as e:
                raise RuntimeError(f"Error during conversion to {fmt}: {str(e)}.")

    def validate_input(self, schema: str) -> bool:
        # Implement validation logic for JSON Schema
        return True

    def validate_output(self, schema: str) -> bool:
        # Implement validation logic for LinkML schema
        return True

class ConverterJsonSchemaToLinkMl(ConverterInternal):
    def __init__(self):
        super().__init__(
            name="LinkMl schema_automator JsonSchemaImportEngine",
            service_address="internal",
            source_format=SchemaLanguage.JsonSchema,
            target_format=SchemaLanguage.LinkMl,
            supported_features=[
                SchemaFeature.Comments,
                SchemaFeature.Hierarchy,
                SchemaFeature.References,
                SchemaFeature.Constraints,
                SchemaFeature.Properties,
                SchemaFeature.Attributes,
                SchemaFeature.Composition
            ]
        )

    def converter_logic(self, schema: str) -> str:
        schema_dict: dict = json.loads(schema)
        # LinkML specific clean-up
        schema_dict.pop("$schema", None)
        # schema_dict.pop("$id", None)

        schema = json.dumps(schema_dict)

        # Import
        import_engine = schema_automator.JsonSchemaImportEngine()
        schema_def: SchemaDefinition = import_engine.loads(schema_dict)
        return yaml_dumper.dumps(schema_def)

    def validate_input(self, schema: str) -> bool:
        # Implement validation logic for JSON Schema
        return True

    def validate_output(self, schema: str) -> bool:
        # Implement validation logic for LinkML schema
        return True
