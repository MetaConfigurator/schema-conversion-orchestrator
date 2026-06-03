from typing import List
from schema_conversion_orchestrator.converters.python.linkml import (
    ConverterFromLinkMl,
    ConverterJsonSchemaToLinkMl,
    ConverterOwlToLinkMl,
)
from schema_conversion_orchestrator.converters.python.mdmodels import (
    ConverterFromMdModels,
    ConverterJsonSchemaToMdModels,
)
from schema_conversion_orchestrator.converters.python.rdflib import ConverterTtlToJsonLd

from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


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
