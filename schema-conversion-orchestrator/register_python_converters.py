from typing import List
from ConvertersLinkMl import ConverterFromLinkMl, ConverterJsonSchemaToLinkMl, ConverterOwlToLinkMl
from ConvertersMdModels import ConverterFromMdModels, ConverterJsonSchemaToMdModels

from converter import Converter
from schema_types import SchemaLanguage


def register_python_converters() -> List[Converter]:
    return [

        ConverterFromLinkMl(target_language=SchemaLanguage.JsonSchema),
        ConverterFromLinkMl(target_language=SchemaLanguage.Protobuf),
        ConverterFromLinkMl(target_language=SchemaLanguage.Owl),
        ConverterFromLinkMl(target_language=SchemaLanguage.SHACL),
        ConverterFromLinkMl(target_language=SchemaLanguage.GraphQL),
        ConverterFromLinkMl(target_language=SchemaLanguage.SqlAlchemy),
        ConverterFromLinkMl(target_language=SchemaLanguage.Shex),

        ConverterJsonSchemaToLinkMl(),
        ConverterOwlToLinkMl(),

        ConverterFromMdModels(target_language=SchemaLanguage.Protobuf),
        ConverterFromMdModels(target_language=SchemaLanguage.Xsd),
        ConverterFromMdModels(target_language=SchemaLanguage.JsonSchema),
        ConverterFromMdModels(target_language=SchemaLanguage.GraphQL),
        ConverterFromMdModels(target_language=SchemaLanguage.Mermaid),
        ConverterFromMdModels(target_language=SchemaLanguage.SHACL),
        ConverterFromMdModels(target_language=SchemaLanguage.Shex),

        ConverterJsonSchemaToMdModels(),

    ]
