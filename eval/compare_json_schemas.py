from sentence_transformers import SentenceTransformer, util
import jsonref
import copy
from typing import Dict, Set, Any
import json


def resolve_refs(schema):
    return jsonref.JsonRef.replace_refs(schema)


def semantic_normalize_schema(gen_schema, gt_schema, threshold=0.6):
    """Recursively align property names in generated schema to ground truth."""
    # Load embedding model
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    semantic_mapped_df = []

    gen_schema = copy.deepcopy(gen_schema)  # to avoid modifying original

    # Only compare if both are objects with properties
    if (
            isinstance(gen_schema, dict)
            and "properties" in gen_schema
            and isinstance(gt_schema, dict)
            and "properties" in gt_schema
    ):
        gen_props = list(gen_schema["properties"].keys())
        gt_props = list(gt_schema["properties"].keys())

        if gen_props and gt_props:
            # Encode all property names once
            gen_emb = model.encode(gen_props, convert_to_tensor=True)
            gt_emb = model.encode(gt_props, convert_to_tensor=True)
            sim_matrix = util.cos_sim(gen_emb, gt_emb)

            for index, g_key in enumerate(gen_props):
                j = sim_matrix[index].argmax().item()
                best_gt = gt_props[j]
                score = sim_matrix[index][j].item()

                # Record the result
                semantic_mapped_df.append({
                    "Generated Property": g_key,
                    "Best Match in GT": best_gt,
                    "Similarity": round(score, 2),
                    "Renamed": "Yes" if score >= threshold and g_key != best_gt else "No"
                })

                if score >= threshold and g_key != best_gt:
                    # Rename property in generated schema
                    gen_schema["properties"][best_gt] = gen_schema["properties"].pop(g_key)
                    print(f"Renamed '{g_key}' → '{best_gt}' (sim={score:.2f})")

        # Recurse into each sub-property
        for prop_key, sub_schema in list(gen_schema["properties"].items()):
            if (
                    prop_key in gt_schema.get("properties", {})
                    and isinstance(sub_schema, dict)
            ):
                gen_schema["properties"][prop_key] = semantic_normalize_schema(
                    sub_schema, gt_schema["properties"][prop_key], threshold
                )

    return gen_schema


def load_json_schema(schema_path):
    """Load a JSON schema from a file."""
    with open(schema_path, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON schema from {schema_path}: {e}")
            return None


class SchemaComparisonResult:
    def __init__(self, precision: float, recall: float, f1_score: float,
                 true_positives: Set[str], false_positives: Set[str], false_negatives: Set[str],
                 mismatches: Set[str]):
        self.precision = precision
        self.recall = recall
        self.f1_score = f1_score
        self.true_positives = true_positives
        self.false_positives = false_positives
        self.false_negatives = false_negatives
        self.mismatches = mismatches


def _equal_values(v1: Any, v2: Any) -> bool:
    if isinstance(v1, list) and isinstance(v2, list):
        norm1 = [normalize_value(i) for i in v1]
        norm2 = [normalize_value(i) for i in v2]
        norm1_sorted = sorted(norm1, key=lambda x: json.dumps(x, sort_keys=True))
        norm2_sorted = sorted(norm2, key=lambda x: json.dumps(x, sort_keys=True))
        return norm1_sorted == norm2_sorted
    return normalize_value(v1) == normalize_value(v2)


def normalize_value(v: Any) -> Any:
    if isinstance(v, str):
        return v.strip().lower()
    if isinstance(v, set):
        return sorted([normalize_value(i) for i in v])
    if isinstance(v, list):
        return [normalize_value(i) for i in v]
    if isinstance(v, dict):
        return {k: normalize_value(v[k]) for k in sorted(v)}
    return v


def flatten_schema(schema: Any, ignore_metadata: bool, path: str = "") -> Dict[str, Any]:
    flattened_schema = {}

    if isinstance(schema, dict):
        for key, value in schema.items():
            if key in {"title", "description", "examples", "$id", "$schema"} and ignore_metadata:
                continue  # ignore metadata

            new_path = f"{path}.{key}" if path else key
            flattened_schema.update(flatten_schema(value, ignore_metadata, new_path))

    elif isinstance(schema, list):
        normalized = [flatten_schema(item, ignore_metadata) if isinstance(item, (dict, list)) else item for item in
                      schema]
        normalized.sort(key=lambda x: json.dumps(x, sort_keys=True))  # sort normalized list
        flattened_schema[path] = normalized
    else:
        flattened_schema[path] = schema

    return flattened_schema


def normalize_schema(schema: Any, reference_for_semantic_normalization: any | None) \
        -> Dict[str, Any]:
    """Resolves references in the schema. If referenceForSemanticNormalization is provided, also applies
    semantic normalization to align property names. Finally, it flattens the schema for easier comparison."""
    resolved = resolve_refs(schema)
    if reference_for_semantic_normalization:
        resolved = semantic_normalize_schema(resolved, reference_for_semantic_normalization)
    return resolved


def compare_flattened_schemas(
        reference: Dict[str, Any],
        predicted: Dict[str, Any],
        compare_pattern: bool
) -> SchemaComparisonResult:
    ref_keys = set(reference.keys())
    pred_keys = set(predicted.keys())

    true_positives = set()
    value_mismatches = set()
    false_positives = pred_keys - ref_keys
    false_negatives = ref_keys - pred_keys

    for key in ref_keys & pred_keys:
        val1 = reference[key]
        val2 = predicted[key]
        # do not compare values for the '*.pattern' key
        if key.endswith('.pattern') and not compare_pattern:
            true_positives.add(key)
            continue
        if _equal_values(val1, val2):
            true_positives.add(key)
        else:
            value_mismatches.add(key)

    # Count value mismatches as FP and FN
    tp = len(true_positives)
    fp = len(false_positives) + len(value_mismatches)
    fn = len(false_negatives) + len(value_mismatches)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return SchemaComparisonResult(precision, recall, f1, true_positives, false_positives, false_negatives,
                                  value_mismatches)


def compare_schemas(reference, predicted, semantic_normalization: bool, compare_metadata_and_pattern: bool) \
        -> SchemaComparisonResult:
    reference_normalized = normalize_schema(reference, None)
    predicted_normalized = normalize_schema(predicted, reference_normalized if semantic_normalization else None)
    flat1 = flatten_schema(reference_normalized, ignore_metadata=not compare_metadata_and_pattern)
    flat2 = flatten_schema(predicted_normalized, ignore_metadata=not compare_metadata_and_pattern)
    return compare_flattened_schemas(flat1, flat2, compare_metadata_and_pattern)


if __name__ == "__main__":

    TP_total = 0
    FP_total = 0
    FN_total = 0

    results = []

    for i in range(1, 3):
        # gt_schema = f"schema_{i}_expected.json"
        # generated_schema = f"schema_{i}_generated.json"

        with open(f"expected/schema_{i}_expected.json", "r") as f:
            gt_schema = json.load(f)

        with open(f"generated_baseline/generated_{i}.json", "r") as f:
            generated_schema = json.load(f)

        print(gt_schema)
        print(generated_schema)

        gt_schema_ref_resolved = resolve_refs(gt_schema)
        generated_schema_ref_resolved = resolve_refs(generated_schema)

        semantic_normalized_gen_schema = semantic_normalize_schema(generated_schema_ref_resolved,
                                                                   gt_schema_ref_resolved,
                                                                   threshold=0.8)

        print(f"{i} : Comparing Generated Schema with Ground Truth...")

        # Compare the schemas
        result = compare_schemas(gt_schema_ref_resolved, semantic_normalized_gen_schema, True, True)
        results.append(result)

        # Print results in human-readable format
        print("\nEvaluation Metrics:")
        print(f"Precision: {result['precision']:.2f}")
        print(f"Recall: {result['recall']:.2f}")
        print(f"F1 Score: {result['f1_score']:.2f}")
        print(f"True Positives: {len(result['true_positives'])}")
        print(f"False Positives: {len(result['false_positives'])}")
        print(f"False Negatives: {len(result['false_negatives'])}")
        print(f"Mismatches: {len(result['mismatches'])}")

        TP_total = sum(r["tp"] for r in results)
        FP_total = sum(r["fp"] for r in results)
        FN_total = sum(r["fn"] for r in results)

        precision_micro = TP_total / (TP_total + FP_total)
        recall_micro = TP_total / (TP_total + FN_total)
        f1_micro = 2 * precision_micro * recall_micro / (precision_micro + recall_micro)

        # accuracy_union = TP_total / (TP_total + FP_total + FN_total)
    print('\n----- FINAL METRICS (MICRO)--------')
    print(f'PRECISION : {precision_micro}')
    print(f'RECALL : {recall_micro}')
    print(f'F1_MICRO : {f1_micro}')
