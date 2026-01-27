from converter import ConversionResults


def serialize_conversion_results(results: ConversionResults):
    serialized_results = []
    for attempt in results:
        success, result_schema_or_error, path = attempt
        serialized_results.append({
            "success": success,
            "result": result_schema_or_error,
            "conversionPath": [
                                 {
                                     "sourceLanguage": conv.source_language.value,
                                     "targetLanguage": conv.target_language.value,
                                     "serviceName": conv.service_name,
                                     "converterName": conv.name
                                 } for conv in path]
        })
    return serialized_results
