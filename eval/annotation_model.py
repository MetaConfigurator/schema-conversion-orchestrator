"""Shared model for reviewing and annotating evaluation outputs."""

from __future__ import annotations

import csv
import threading
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
RESULTS_DIR = EVAL_DIR / "results"
OUTPUT_DIR = RESULTS_DIR / "orchestrator_outputs"
INPUT_DIR = EVAL_DIR / "real_world_inputs"
REVIEW_DIR = OUTPUT_DIR / "review"
FINAL_CSV = REVIEW_DIR / "final_outputs.csv"
EDGE_CSV = REVIEW_DIR / "edge_outputs.csv"
ALLOWED_STATUSES = {"", "G", "L", "I"}


class AnnotationModel:
    """File-backed annotation model for final and edge review CSVs."""

    def __init__(
        self,
        final_csv: Path = FINAL_CSV,
        edge_csv: Path = EDGE_CSV,
        eval_dir: Path = EVAL_DIR,
        input_dir: Path = INPUT_DIR,
        output_dir: Path = OUTPUT_DIR,
    ) -> None:
        self.paths = {"final": final_csv, "edge": edge_csv}
        self.eval_dir = eval_dir
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.lock = threading.Lock()

    def rows(
        self,
        kind: str,
        status_filter: str = "all",
        search: str = "",
        multi_hop_only: bool = False,
    ) -> list[dict[str, str]]:
        rows = self.read_rows(kind)[1]
        return self.filter_rows(
            rows,
            status_filter=status_filter,
            search=search,
            multi_hop_only=multi_hop_only,
        )

    def read_rows(self, kind: str) -> tuple[list[str], list[dict[str, str]]]:
        path = self._path(kind)
        if not path.exists():
            raise FileNotFoundError(f"Review CSV not found: {path}")
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            rows = []
            for index, row in enumerate(reader):
                clean = {key: value or "" for key, value in row.items()}
                clean["__rowid"] = str(index)
                rows.append(clean)
        return fieldnames, rows

    def filter_rows(
        self,
        rows: list[dict[str, str]],
        status_filter: str = "all",
        search: str = "",
        multi_hop_only: bool = False,
    ) -> list[dict[str, str]]:
        needle = search.strip().lower()
        filtered = []
        for row in rows:
            status = row.get("status", "")
            if multi_hop_only and self.path_step_count(row) <= 1:
                continue
            if status_filter == "blank" and status:
                continue
            if status_filter in {"G", "L", "I"} and status != status_filter:
                continue
            if needle and not any(needle in str(value).lower() for value in row.values()):
                continue
            filtered.append(row)
        return filtered

    def row(self, kind: str, row_id: int | str) -> dict[str, str]:
        row_index = int(row_id)
        _, rows = self.read_rows(kind)
        if row_index < 0 or row_index >= len(rows):
            raise IndexError("row index out of range")
        return rows[row_index]

    def comparison(self, kind: str, row_id: int | str) -> dict[str, str | bool]:
        row = self.row(kind, row_id)
        input_field = "input_file" if kind == "final" else "input_path"
        input_path, input_content, input_error = self.read_review_file(
            self.resolve_review_path(kind, row, input_field)
        )
        output_path, output_content, output_error = self.read_review_file(
            self.resolve_review_path(kind, row, "output_path")
        )
        return {
            "input_path": input_path,
            "input_content": input_content,
            "input_error": input_error,
            "output_path": output_path,
            "output_content": output_content,
            "output_error": output_error,
        }

    def update(self, kind: str, row_id: int | str, status: str, notes: str) -> None:
        if status not in ALLOWED_STATUSES:
            raise ValueError("status must be blank, G, L, or I")
        row_index = int(row_id)
        with self.lock:
            fieldnames, rows = self.read_rows(kind)
            if row_index < 0 or row_index >= len(rows):
                raise IndexError("row index out of range")
            rows[row_index]["status"] = status
            rows[row_index]["notes"] = notes
            for row in rows:
                row.pop("__rowid", None)
            path = self._path(kind)
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            with tmp_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            tmp_path.replace(path)

    def navigable_row_id(
        self,
        kind: str,
        current_row_id: int | str,
        direction: int,
        status_filter: str = "all",
        search: str = "",
        skip_invalid: bool = True,
        multi_hop_only: bool = False,
    ) -> str | None:
        filtered = self.rows(
            kind,
            status_filter=status_filter,
            search=search,
            multi_hop_only=multi_hop_only,
        )
        ids = [row["__rowid"] for row in filtered]
        current = str(current_row_id)
        try:
            start = ids.index(current)
        except ValueError:
            start = -1 if direction > 0 else len(ids)
        for index in range(start + direction, len(ids) if direction > 0 else -1, direction):
            row = filtered[index]
            if skip_invalid and row.get("status", "") == "I":
                continue
            return row["__rowid"]
        return None

    def title(self, kind: str, row: dict[str, str]) -> str:
        if kind == "edge":
            return (
                f"{row.get('edge_source_language', '')} -> "
                f"{row.get('edge_target_language', '')} via {row.get('converter_name', '')}"
            )
        return f"{row.get('source_language', '')} -> {row.get('target_language', '')} {row.get('path_id', '')}"

    def meta_fields(self, kind: str) -> list[str]:
        if kind == "edge":
            return ["input_file", "path_id", "step_index", "edge_signature", "input_path", "output_path"]
        return ["input_file", "path_rank", "path_count", "path_signature", "output_path"]

    def path_step_count(self, row: dict[str, str]) -> int:
        signature = row.get("path_signature", "")
        if not signature:
            return 0
        return len([step for step in signature.split(" -> ") if step.strip()])

    def resolve_review_path(self, kind: str, row: dict[str, str], field: str) -> Path | None:
        value = row.get(field) or ""
        if not value:
            return None
        path = Path(value)
        if path.is_absolute():
            return path
        if kind == "final" and field == "input_file":
            return self.input_dir / path
        if value.startswith("real_world_inputs/"):
            return self.eval_dir / path
        return self.output_dir / path

    def read_review_file(self, path: Path | None) -> tuple[str, str, bool]:
        if path is None:
            return "", "", True
        label = str(path.relative_to(self.eval_dir)) if path.is_relative_to(self.eval_dir) else str(path)
        if not path.exists():
            return label, f"File not found: {path}", True
        try:
            return label, path.read_text(encoding="utf-8", errors="replace"), False
        except OSError as exc:
            return label, f"Could not read {path}: {exc}", True

    def _path(self, kind: str) -> Path:
        if kind not in self.paths:
            raise ValueError("kind must be final or edge")
        return self.paths[kind]
