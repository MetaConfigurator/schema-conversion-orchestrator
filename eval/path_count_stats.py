"""Path-count statistics over the conversion graph.

Builds the conversion graph from the registered converters and reports, for the
paper, how many feasible conversion paths the orchestrator considers between two
schema languages: the maximum and the average number of paths.

A *path* here is a full converter chain (the same notion the orchestrator
enumerates and ranks via ``domain.conversion_graph.find_paths``): parallel
converters for the same source/target hop count as *separate* paths, and
multi-hop chains through intermediate languages are included. This differs from
the language-node path-count matrix in ``eval/plotting_conversion_matrix.py``, which
collapses parallel converters into a single edge; here we count what the user
actually sees ranked.

For each ordered pair of distinct schema languages ``(source, target)`` we count
its paths. We report two averages:

  * over all ordered pairs of distinct languages (unreachable pairs count as 0),
  * over only the reachable pairs (at least one path exists).

Usage::

    python eval/path_count_stats.py            # full graph (all languages)
    python eval/path_count_stats.py --core      # only the core-language subset
    python eval/path_count_stats.py --output eval/results/path_count_stats.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
RESULTS_DIR = EVAL_DIR / "results"
sys.path.insert(0, str(REPO_ROOT / "src"))

from schema_conversion_orchestrator.converters.registry import register_converters  # noqa: E402
from schema_conversion_orchestrator.domain.conversion_graph import (  # noqa: E402
    build_conversion_graph,
    find_paths,
)


def all_languages(graph) -> List:
    """Every schema language that appears as a source or a target in the graph."""
    languages = set(graph.keys())
    for converters in graph.values():
        for conv in converters:
            languages.add(conv.target_language)
    # Stable, readable ordering by value.
    return sorted(languages, key=lambda lang: getattr(lang, "value", str(lang)))


def path_counts(graph) -> Dict[Tuple[str, str], int]:
    """Map each ordered pair of distinct languages to its number of converter-chain paths."""
    languages = all_languages(graph)
    counts: Dict[Tuple[str, str], int] = {}
    for src in languages:
        for tgt in languages:
            if src == tgt:
                continue
            n = len(find_paths(src, tgt, graph))
            counts[(getattr(src, "value", str(src)), getattr(tgt, "value", str(tgt)))] = n
    return counts


def summarize(counts: Dict[Tuple[str, str], int]) -> dict:
    all_pairs = list(counts.values())
    reachable = [c for c in all_pairs if c > 0]
    max_pair = max(counts, key=counts.get) if counts else None
    return {
        "languages_in_graph": len({lang for pair in counts for lang in pair}),
        "ordered_pairs_total": len(all_pairs),
        "ordered_pairs_reachable": len(reachable),
        "total_paths": sum(all_pairs),
        "max_paths": max(all_pairs) if all_pairs else 0,
        "max_paths_pair": f"{max_pair[0]} -> {max_pair[1]}" if max_pair else None,
        "avg_paths_over_all_pairs": round(sum(all_pairs) / len(all_pairs), 2) if all_pairs else 0.0,
        "avg_paths_over_reachable_pairs": round(sum(reachable) / len(reachable), 2) if reachable else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", action="store_true",
                        help="restrict to the core-language subset (register_converters(True))")
    parser.add_argument("--output", type=Path, default=RESULTS_DIR / "path_count_stats.json",
                        help="where to write the JSON summary")
    args = parser.parse_args()

    converters: List = register_converters(args.core)
    graph = build_conversion_graph(converters)

    counts = path_counts(graph)
    summary = summarize(counts)
    summary["graph"] = "core" if args.core else "full"

    print(f"Conversion graph: {summary['graph']} "
          f"({summary['languages_in_graph']} languages, {len(converters)} converters)")
    print(f"  ordered pairs of distinct languages : {summary['ordered_pairs_total']}")
    print(f"  reachable pairs (>=1 path)           : {summary['ordered_pairs_reachable']}")
    print(f"  total feasible paths                 : {summary['total_paths']}")
    print(f"  max paths for a single pair          : {summary['max_paths']}  ({summary['max_paths_pair']})")
    print(f"  avg paths over all distinct pairs    : {summary['avg_paths_over_all_pairs']}")
    print(f"  avg paths over reachable pairs       : {summary['avg_paths_over_reachable_pairs']}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"  summary -> {args.output}")


if __name__ == "__main__":
    main()
