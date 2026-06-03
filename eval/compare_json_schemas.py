"""Structural comparison of two JSON Schemas.

This mirrors the comparison used by the shacl-bridge benchmark
(``benchmark/runner/compare-json-schemas.ts``) so that the Schema Conversion
Orchestrator evaluation reports the same F1 / Jaccard metrics as the
shacl-bridge thesis. Both schemas are ``$ref``-resolved, flattened into a set of
``dotted.path -> value`` entries (metadata keys ignored by default), and then
compared key-by-key:

* true positive  — key present in both, with equal value
* false positive — key only in the predicted schema
* false negative — key only in the reference schema
* mismatch       — key present in both but with differing value (counts as both
  a false positive and a false negative)

From these, precision, recall, F1 and the Jaccard index are derived.

Optional semantic property-name normalization (via sentence-transformers) is
available but disabled by default; it is only needed when generated and
reference property names differ lexically. The heavy import is therefore lazy.
"""
import copy
import json
from typing import Any, Dict, Set


def resolve_refs(schema: Any, root: Any = None) -> Any:
    """Resolve local ``#/...`` JSON ``$ref`` pointers in-place (returns a copy).

    Sibling keys alongside a ``$ref`` are merged with the resolved target
    (the target taking precedence), matching the benchmark's TypeScript
    implementation. Non-local refs are left untouched.
    """
    if root is None:
        root = schema

    if isinstance(schema, list):
        return [resolve_refs(item, root) for item in schema]

    if isinstance(schema, dict):
        ref = schema.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/"):
            target: Any = root
            for part in ref[2:].split("/"):
                if isinstance(target, dict):
                    target = target.get(part)
                else:
                    return schema  # unresolvable -> leave as is
            resolved = resolve_refs(target, root)
            siblings = {
                k: resolve_refs(v, root)
                for k, v in schema.items()
                if k not in ("$ref", "$defs")
            }
            if isinstance(resolved, dict):
                return {**siblings, **resolved}
            return resolved
        return {k: resolve_refs(v, root) for k, v in schema.items()}

    return schema


def semantic_normalize_schema(gen_schema, reference_schema, threshold=0.6):
    """Recursively align property names in the generated schema to the ground
    truth using sentence-transformer embeddings.

    Only needed when property names differ lexically between generated and
    reference schemas; ``sentence-transformers`` is imported lazily so the rest
    of this module works without it installed.
    """
    from sentence_transformers import SentenceTransformer, util  # lazy, heavy

    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    gen_schema = copy.deepcopy(gen_schema)  # to avoid modifying original

    if (
        isinstance(gen_schema, dict)
        and "properties" in gen_schema
        and isinstance(reference_schema, dict)
        and "properties" in reference_schema
    ):
        gen_props = list(gen_schema["properties"].keys())
        gt_props = list(reference_schema["properties"].keys())

        if gen_props and gt_props:
            gen_emb = model.encode(gen_props, convert_to_tensor=True)
            gt_emb = model.encode(gt_props, convert_to_tensor=True)
            sim_matrix = util.cos_sim(gen_emb, gt_emb)

            for index, g_key in enumerate(gen_props):
                j = sim_matrix[index].argmax().item()
                best_gt = gt_props[j]
                score = sim_matrix[index][j].item()
                if score >= threshold and g_key != best_gt:
                    gen_schema["properties"][best_gt] = gen_schema["properties"].pop(g_key)
                    print(f"Renamed '{g_key}' -> '{best_gt}' (sim={score:.2f})")

        for prop_key, sub_schema in list(gen_schema["properties"].items()):
            if prop_key in reference_schema.get("properties", {}) and isinstance(sub_schema, dict):
                gen_schema["properties"][prop_key] = semantic_normalize_schema(
                    sub_schema, reference_schema["properties"][prop_key], threshold
                )

    return gen_schema


def load_json_schema(schema_path):
    """Load a JSON schema from a file."""
    with open(schema_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON schema from {schema_path}: {e}")
            return None


class SchemaComparisonResult:
    def __init__(self, precision: float, recall: float, f1_score: float, jaccard: float,
                 true_positives: Set[str], false_positives: Set[str], false_negatives: Set[str],
                 mismatches: Set[str]):
        self.precision = precision
        self.recall = recall
        self.f1_score = f1_score
        self.jaccard = jaccard
        self.true_positives = true_positives
        self.false_positives = false_positives
        self.false_negatives = false_negatives
        self.mismatches = mismatches


def _equal_values(v1: Any, v2: Any) -> bool:
    if isinstance(v1, list) and isinstance(v2, list):
        norm1 = sorted((normalize_value(i) for i in v1), key=lambda x: json.dumps(x, sort_keys=True))
        norm2 = sorted((normalize_value(i) for i in v2), key=lambda x: json.dumps(x, sort_keys=True))
        return norm1 == norm2
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


# Metadata keys ignored when ignore_metadata is set (mirrors the benchmark).
METADATA_KEYS = {"title", "description", "examples", "$id", "$schema", "x-shacl-prefixes"}

# Keys whose presence with their default value is semantically equivalent to
# absence, so they are dropped before comparison (mirrors the benchmark).
JSON_SCHEMA_DEFAULTS = {"additionalProperties": True}


def flatten_schema(schema: Any, ignore_metadata: bool, path: str = "") -> Dict[str, Any]:
    flattened_schema = {}

    if isinstance(schema, dict):
        for key, value in schema.items():
            if key in METADATA_KEYS and ignore_metadata:
                continue  # ignore metadata
            if key in JSON_SCHEMA_DEFAULTS and value == JSON_SCHEMA_DEFAULTS[key]:
                continue  # default value == absence
            new_path = f"{path}.{key}" if path else key
            flattened_schema.update(flatten_schema(value, ignore_metadata, new_path))

    elif isinstance(schema, list):
        normalized = [flatten_schema(item, ignore_metadata) if isinstance(item, (dict, list)) else item
                      for item in schema]
        normalized.sort(key=lambda x: json.dumps(x, sort_keys=True))
        flattened_schema[path] = normalized
    else:
        flattened_schema[path] = schema

    return flattened_schema


def normalize_schema(schema: Any, reference_for_semantic_normalization: Any | None) -> Dict[str, Any]:
    """Resolve references and (optionally) semantically align property names."""
    resolved = resolve_refs(schema)
    if reference_for_semantic_normalization:
        resolved = semantic_normalize_schema(resolved, reference_for_semantic_normalization)
    return resolved


def compare_flattened_schemas(reference: Dict[str, Any], predicted: Dict[str, Any],
                              compare_pattern: bool) -> SchemaComparisonResult:
    ref_keys = set(reference.keys())
    pred_keys = set(predicted.keys())

    true_positives = set()
    value_mismatches = set()
    false_positives = pred_keys - ref_keys
    false_negatives = ref_keys - pred_keys

    for key in ref_keys & pred_keys:
        # do not compare values for the '*.pattern' key (regex dialects differ)
        if key.endswith(".pattern") and not compare_pattern:
            true_positives.add(key)
            continue
        if _equal_values(reference[key], predicted[key]):
            true_positives.add(key)
        else:
            value_mismatches.add(key)

    tp = len(true_positives)
    fp = len(false_positives) + len(value_mismatches)
    fn = len(false_negatives) + len(value_mismatches)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    union_size = len(true_positives) + len(false_positives) + len(false_negatives) + len(value_mismatches)
    jaccard = len(true_positives) / union_size if union_size else 0.0

    return SchemaComparisonResult(precision, recall, f1, jaccard, true_positives, false_positives,
                                  false_negatives, value_mismatches)


def compare_schemas(reference, predicted, semantic_normalization: bool,
                    compare_metadata_and_pattern: bool) -> SchemaComparisonResult:
    reference_normalized = normalize_schema(reference, None)
    predicted_normalized = normalize_schema(predicted, reference_normalized if semantic_normalization else None)
    flat1 = flatten_schema(reference_normalized, ignore_metadata=not compare_metadata_and_pattern)
    flat2 = flatten_schema(predicted_normalized, ignore_metadata=not compare_metadata_and_pattern)
    return compare_flattened_schemas(flat1, flat2, compare_metadata_and_pattern)
