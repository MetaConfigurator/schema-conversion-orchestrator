from typing import List
from schema_conversion_orchestrator.converters.base import Converter
from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage
from schema_conversion_orchestrator.converters.python_registry import register_python_converters
from schema_conversion_orchestrator.converters.external_registry import register_external_converters


CORE_SCHEMA_LANGUAGES: List[SchemaLanguage] = [
    SchemaLanguage.JsonSchema,
    SchemaLanguage.Xsd,
    SchemaLanguage.SHACL_TTL,
    SchemaLanguage.MdModels,
    SchemaLanguage.LinkMl,
]


def register_converters(only_core_languages: bool = False) -> List[Converter]:
    converters: List[Converter] = register_python_converters()
    converters.extend(register_external_converters())

    # remove converters that do involve non-core schema languages if only_core_languages is True
    if only_core_languages:
        converters = [
            conv for conv in converters
            if conv.source_language in CORE_SCHEMA_LANGUAGES and conv.target_language in CORE_SCHEMA_LANGUAGES
        ]

    return converters
