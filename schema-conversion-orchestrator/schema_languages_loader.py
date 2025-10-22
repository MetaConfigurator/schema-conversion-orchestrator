import json
from schema_types import SchemaLanguage, SchemaFeature, SchemaFeatureSupport, SchemaLanguagesFeatures
from schema_languages_generated import SchemaLanguageFeatures, schema_language_features_from_dict


def load_schema_language_features() -> SchemaLanguagesFeatures:
    """Load schema language features from the configuration file."""

    schema_languages_config_path = "configuration/schemaLanguages.json"
    # load content from schema languages config into this string by reading the file
    with open(schema_languages_config_path, 'r') as f:
        schema_languages_config_string = f.read()
        schema_languages_config = json.loads(schema_languages_config_string)

    schema_language_features: SchemaLanguageFeatures = schema_language_features_from_dict(schema_languages_config)

    result = {}
    for lang in schema_language_features.schema_languages:
        feature_map = {}
        for feature, support in lang.supportedFeatures.items():
            try:
                feature_enum = SchemaFeature(feature)
                support_enum = SchemaFeatureSupport(support)
                feature_map[feature_enum] = support_enum
            except ValueError as e:
                print(f"Unknown feature or support level: {e}")
        try:
            lang_enum = SchemaLanguage(lang.name)
            result[lang_enum] = feature_map
        except ValueError as e:
            print(f"Unknown schema language: {e}")

    return result
