from schema_conversion_orchestrator.domain.conversion_types import ConversionResults


def serialize_conversion_results(results: ConversionResults):
    serialized_results = []
    for attempt in results:
        success, result_schema_or_error, path, failed_step_index = attempt
        serialized_results.append({
            "success": success,
            "result": result_schema_or_error,
            "failedStepIndex": failed_step_index,
            "conversionPath": [
                                 {
                                     "sourceLanguage": conv.source_language.value,
                                     "targetLanguage": conv.target_language.value,
                                     "serviceName": conv.service_name,
                                     "converterName": conv.name,
                                     "library": conv.library,
                                     "libraryVersion": conv.library_version,
                                     "libraryUrl": conv.library_url
                                 } for conv in path]
        })
    return serialized_results
