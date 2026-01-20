from typing import List
from ConvertersLinkMl import ConverterFromLinkMl, ConverterJsonSchemaToLinkMl, ConverterOwlToLinkMl
from ConvertersMdModels import ConverterFromMdModels, ConverterJsonSchemaToMdModels

from converter import Converter
from schema_types import SchemaLanguage


def register_python_converters() -> List[Converter]:
    return [

        ConverterFromLinkMl(target_language=SchemaLanguage.JsonSchema),
        ConverterFromLinkMl(target_language=SchemaLanguage.JsonLD),
        ConverterFromLinkMl(target_language=SchemaLanguage.Protobuf),
        ConverterFromLinkMl(target_language=SchemaLanguage.PythonLinkMl),
        ConverterFromLinkMl(target_language=SchemaLanguage.Owl),
        ConverterFromLinkMl(target_language=SchemaLanguage.SHACL),
        ConverterFromLinkMl(target_language=SchemaLanguage.GraphQL),
        ConverterFromLinkMl(target_language=SchemaLanguage.SqlAlchemy),
        ConverterFromLinkMl(target_language=SchemaLanguage.Shex),
        ConverterFromLinkMl(target_language=SchemaLanguage.Docs_LinkMl),
        # ConverterFromLinkMl(target_language=SchemaLanguage.Java_LinkMl),

        ConverterJsonSchemaToLinkMl(),
        ConverterOwlToLinkMl(),

        ConverterFromMdModels(target_language=SchemaLanguage.Protobuf),
        ConverterFromMdModels(target_language=SchemaLanguage.Xsd),
        ConverterFromMdModels(target_language=SchemaLanguage.PythonPydantic),
        ConverterFromMdModels(target_language=SchemaLanguage.JsonSchema),
        ConverterFromMdModels(target_language=SchemaLanguage.GraphQL),
        ConverterFromMdModels(target_language=SchemaLanguage.Julia_MdModels),
        ConverterFromMdModels(target_language=SchemaLanguage.Mermaid),
        ConverterFromMdModels(target_language=SchemaLanguage.SHACL),
        ConverterFromMdModels(target_language=SchemaLanguage.Rust_MdModels),
        ConverterFromMdModels(target_language=SchemaLanguage.TypeScript_MdModels),
        ConverterFromMdModels(target_language=SchemaLanguage.Shex),

        ConverterJsonSchemaToMdModels(),

    ]
