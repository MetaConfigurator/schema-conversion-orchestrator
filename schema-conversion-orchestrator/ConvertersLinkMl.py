import json
import tempfile
from typing import Dict, Type

import schema_automator
from linkml.utils.generator import Generator

from converter import ConverterInternal
from schema_types import SchemaLanguage
from utils import simple_cname_convert

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
            service_name="FlaskApp",
            source_format=SchemaLanguage.LinkMl,
            target_format=SchemaLanguage.JsonSchema,
            supported_features=None
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
            service_name="FlaskApp",
            source_format=SchemaLanguage.LinkMl,
            target_format=target_format,
            supported_features=None
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
                SchemaLanguage.Docs_LinkMl: DocGenerator,
                SchemaLanguage.PythonLinkMl: PythonGenerator,
                # SchemaLanguage.Java_LinkMl: JavaGenerator, # needs directory also as argument
                SchemaLanguage.Shex: ShExGenerator,
                SchemaLanguage.SqlAlchemy: SQLAlchemyGenerator
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
            service_name="FlaskApp",
            source_format=SchemaLanguage.JsonSchema,
            target_format=SchemaLanguage.LinkMl,
            supported_features=None
        )

    def converter_logic(self, schema: str) -> str:
        schema_dict: dict = json.loads(schema)
        # LinkML specific clean-up
        schema_dict.pop("$schema", None)
        schema_dict.pop("$id", None)

        # if no title is present, add a dummy title
        if "title" not in schema_dict:
            schema_dict["title"] = "ImportedSchema"
        else:
            # convert title to a simple class name
            schema_dict["title"] = simple_cname_convert(schema_dict["title"])

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


class ConverterOwlToLinkMl(ConverterInternal):
    def __init__(self):
        super().__init__(
            name="LinkMl schema_automator OwlImportEngine",
            service_address="internal",
            service_name="FlaskApp",
            source_format=SchemaLanguage.Owl,
            target_format=SchemaLanguage.LinkMl,
            supported_features=None
        )

    def converter_logic(self, schema: str) -> str:
        schema_dict: dict = json.loads(schema)
        # LinkML specific clean-up
        schema_dict.pop("$schema", None)
        # schema_dict.pop("$id", None)

        # if no title is present, add a dummy title
        if "title" not in schema_dict:
            schema_dict["title"] = "ImportedSchema"

        schema = json.dumps(schema_dict)

        with tempfile.NamedTemporaryFile("w+", suffix=".owl") as f:
            f.write(schema)
            f.flush()
            file_name = f.name

        # Import
        import_engine = schema_automator.OwlImportEngine()
        schema_def: SchemaDefinition = import_engine.convert(file_name)
        return yaml_dumper.dumps(schema_def)

    def validate_input(self, schema: str) -> bool:
        # Implement validation logic for Owl
        return True

    def validate_output(self, schema: str) -> bool:
        # Implement validation logic for LinkML schema
        return True