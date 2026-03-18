from typing import List
from ConvertersLinkMl import ConverterFromLinkMl, ConverterJsonSchemaToLinkMl, ConverterOwlToLinkMl
from ConvertersMdModels import ConverterFromMdModels, ConverterJsonSchemaToMdModels
from ConvertersRdfLib import ConverterTtlToJsonLd

from converter import Converter
from schema_types import SchemaLanguage


def register_python_converters() -> List[Converter]:
    return [

        ConverterFromLinkMl(target_language=SchemaLanguage.JsonSchema),
        ConverterFromLinkMl(target_language=SchemaLanguage.Protobuf),
        ConverterFromLinkMl(target_language=SchemaLanguage.Owl_TTL),
        ConverterFromLinkMl(target_language=SchemaLanguage.SHACL_TTL),
        ConverterFromLinkMl(target_language=SchemaLanguage.GraphQL),
        ConverterFromLinkMl(target_language=SchemaLanguage.SqlAlchemy),
        ConverterFromLinkMl(target_language=SchemaLanguage.Shex),

        ConverterJsonSchemaToLinkMl(),
        ConverterOwlToLinkMl(),

        ConverterTtlToJsonLd(SchemaLanguage.SHACL_TTL, SchemaLanguage.SHACL_JSON_LD),

        ConverterFromMdModels(target_language=SchemaLanguage.Protobuf),
        ConverterFromMdModels(target_language=SchemaLanguage.Xsd),
        ConverterFromMdModels(target_language=SchemaLanguage.JsonSchema),
        ConverterFromMdModels(target_language=SchemaLanguage.GraphQL),
        ConverterFromMdModels(target_language=SchemaLanguage.Mermaid),
        ConverterFromMdModels(target_language=SchemaLanguage.SHACL_TTL),
        ConverterFromMdModels(target_language=SchemaLanguage.Shex),

        ConverterJsonSchemaToMdModels(),

    ]
