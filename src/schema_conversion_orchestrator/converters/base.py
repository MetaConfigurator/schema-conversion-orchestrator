from importlib.metadata import PackageNotFoundError, version as _package_version

from schema_conversion_orchestrator.domain.schema_types import SchemaLanguage


def get_package_version(package_name: str) -> str | None:
    """Return the installed version of a distribution, or None if not installed.

    Distribution names are matched case-insensitively and treat '-' / '_' as
    equivalent, so e.g. 'schema-automator' and 'schema_automator' both work.
    """
    try:
        return _package_version(package_name)
    except PackageNotFoundError:
        return None


class Converter:
    """
    Abstract base class for schema converters.
    """

    def __init__(
        self,
        name: str,
        service_address: str,
        service_name: str,
        source_language: SchemaLanguage,
        target_language: SchemaLanguage,
        library: str | None = None,
        library_version: str | None = None,
        library_url: str | None = None,
    ) -> None:
        self.name = name
        self.service_address = service_address
        self.service_name = service_name
        self.source_language = source_language
        self.target_language = target_language
        # Underlying third-party library that performs this conversion, so the
        # frontend can attribute a (failed) step to a specific library + version.
        self.library = library
        self.library_version = library_version
        self.library_url = library_url

    def convert(self, schema: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")


class ConverterInternal(Converter):
    """
    Internal converter that performs conversion using built-in Python logic.
    """

    def convert(self, schema: str) -> str:
        if not self.validate_input(schema):
            raise ValueError("Invalid input schema for the source format.")

        converted_schema = self.converter_logic(schema)

        if not self.validate_output(converted_schema):
            raise ValueError("Converted schema is invalid for the target format.")

        return converted_schema

    def converter_logic(self, schema: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")

    def validate_input(self, schema: str) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")

    def validate_output(self, schema: str) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")
