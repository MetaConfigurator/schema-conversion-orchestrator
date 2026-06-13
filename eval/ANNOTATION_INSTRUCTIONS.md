# Annotation Instructions

These instructions define how the outputs of the broad orchestrator evaluation are annotated. They are the instructions given to the annotating agent and are versioned here so that the annotation criteria are explicit and the annotation is reproducible.

## Workflow

1. **Agent pass.** The first annotation pass is performed by a coding agent (Claude Code running Claude Sonnet 4.6). The agent goes through `results/orchestrator_outputs/review/final_outputs.csv`, reads the referenced input and produced output files, and fills the `status` column according to the rules below. Intermediate-step rows in `edge_outputs.csv` are deprecated optional diagnostics and are not required for the default paper-facing scores.
2. **Human review.** Every label is then reviewed by a human with the interactive annotation viewer (`PYTHONPATH=src python3 eval/annotate_outputs.py`), which shows the input and the produced output side by side with a `G`/`L`/`I` dropdown and a notes field.
3. **Instruction refinement.** When the human disagrees with the agent, the label is usually corrected directly in review; where the disagreement reveals an unclear criterion, these instructions are refined and the agent is re-run on the affected rows. The current rules are the result of several such iterations.

## Labels

- `G` good: practically usable; minor gaps or minimal mechanical cleanup are fine.
- `L` lacking: partially useful but missing important structure/constraints, or requiring broader cleanup before practical use.
- `I` invalid: failed, empty, wrong target language, or so malformed/incomplete that it is unusable.

The runner pre-fills `I` for failed or automatically detected invalid outputs; these rows need no agent judgement.

## What to compare each output against

- `final_outputs.csv`: judge the final schema against the original source and modeling intent, i.e. the end-to-end usefulness of the orchestrator's result.
- `edge_outputs.csv`: deprecated optional diagnostics. If this table is annotated for troubleshooting, judge each converter's output against its **direct input only**, given by the `input_step_index` and `input_path` columns (the original source for `step_index == 1`, otherwise the previous step's output). These annotations are not used by the default edge reliability scores.

## Judging rules

- Judge the actual schema content, not cosmetic artifacts. For example, a structurally complete conversion whose generated schema name is bloated (e.g., it embeds the converter library name and a date) is still `G`; downgrade for naming only when the naming makes the schema impractical to use.
- `G` tolerates imperfect details (descriptions, ordering, formatting) and small mechanical fixes such as adjusting a package/schema name or obvious scalar spelling, as long as the structure and constraints of the input are represented and the result is usable as a starting point without major rework.
- `L` applies when the output carries a meaningful schema structure but misses important structure or constraints, or when it needs non-trivial cleanup before it can be used in practice. A target-language-like output with recoverable systematic syntax issues is `L` if the model structure is still clear.
- `I` covers everything unusable: conversion errors, empty output, output in the wrong target language, unrecoverably malformed output, or output so incomplete that it carries no useful information about the input.
- Use the `notes` column to capture the relevant practical judgement concisely: what the output preserves well, what exactly is lacking, and any concrete steps needed to make the schema usable.
- When unsure between two labels, record the doubt in the `notes` column so the human review can settle it.
