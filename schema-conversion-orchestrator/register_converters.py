from typing import List
from converter import Converter
from schema_types import SchemaLanguage
from register_python_converters import register_python_converters
from register_external_converters import register_external_converters


CORE_SCHEMA_LANGUAGES: List[SchemaLanguage] = [
    SchemaLanguage.JsonSchema,
    SchemaLanguage.Xsd,
    SchemaLanguage.SHACL,
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
