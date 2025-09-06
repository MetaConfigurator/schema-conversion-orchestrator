from typing import List
from ConvertersLinkMl import ConverterFromLinkMl, ConverterJsonSchemaToLinkMl, ConverterLinkMlToJsonSchema

from data_structures import Converter, SchemaLanguage


def register_python_converters() -> List[Converter]:
    return [

        ConverterFromLinkMl(target_format=SchemaLanguage.JsonSchema),
        ConverterFromLinkMl(target_format=SchemaLanguage.JsonLD),
        ConverterFromLinkMl(target_format=SchemaLanguage.Protobuf),
        ConverterFromLinkMl(target_format=SchemaLanguage.Python),
        ConverterFromLinkMl(target_format=SchemaLanguage.Owl),
        ConverterFromLinkMl(target_format=SchemaLanguage.SHACL),
        ConverterFromLinkMl(target_format=SchemaLanguage.GraphQL),

        ConverterJsonSchemaToLinkMl(),
        ConverterLinkMlToJsonSchema() # redundant

    ]