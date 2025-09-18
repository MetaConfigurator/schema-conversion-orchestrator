from typing import List
from ConvertersLinkMl import ConverterFromLinkMl, ConverterJsonSchemaToLinkMl, ConverterLinkMlToJsonSchema
from ConvertersMdModels import ConverterFromMdModels, ConverterJsonSchemaToMdModels

from converter import Converter
from schema_types import SchemaLanguage


def register_python_converters() -> List[Converter]:
    return [

        ConverterFromLinkMl(target_format=SchemaLanguage.JsonSchema),
        ConverterFromLinkMl(target_format=SchemaLanguage.JsonLD),
        ConverterFromLinkMl(target_format=SchemaLanguage.Protobuf),
        ConverterFromLinkMl(target_format=SchemaLanguage.PythonLinkMl),
        ConverterFromLinkMl(target_format=SchemaLanguage.Owl),
        ConverterFromLinkMl(target_format=SchemaLanguage.SHACL),
        ConverterFromLinkMl(target_format=SchemaLanguage.GraphQL),
        ConverterFromLinkMl(target_format=SchemaLanguage.SqlAlchemy),
        ConverterFromLinkMl(target_format=SchemaLanguage.Shex),
        ConverterFromLinkMl(target_format=SchemaLanguage.Docs_LinkMl),
        # ConverterFromLinkMl(target_format=SchemaLanguage.Java_LinkMl),

        ConverterJsonSchemaToLinkMl(),

        ConverterFromMdModels(target_format=SchemaLanguage.Protobuf),
        ConverterFromMdModels(target_format=SchemaLanguage.Xsd),
        ConverterFromMdModels(target_format=SchemaLanguage.PythonPydantic),
        ConverterFromMdModels(target_format=SchemaLanguage.JsonSchema),
        ConverterFromMdModels(target_format=SchemaLanguage.GraphQL),
        ConverterFromMdModels(target_format=SchemaLanguage.Julia_MdModels),
        ConverterFromMdModels(target_format=SchemaLanguage.Mermaid),
        ConverterFromMdModels(target_format=SchemaLanguage.SHACL),
        ConverterFromMdModels(target_format=SchemaLanguage.Rust_MdModels),
        ConverterFromMdModels(target_format=SchemaLanguage.TypeScript_MdModels),
        ConverterFromMdModels(target_format=SchemaLanguage.Shex),

        ConverterJsonSchemaToMdModels(),

        ConverterLinkMlToJsonSchema() # redundant

    ]