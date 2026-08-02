#!/usr/bin/env python3
"""Validate exact translation batches and merge them into approved CSVs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from translation_workspace import protected_tokens


BATCHES = {
    "dialogue-181-950.csv": ("dialogue", 181, 950),
    "dialogue-951-1720.csv": ("dialogue", 951, 1720),
    "dialogue-1721-2479.csv": ("dialogue", 1721, 2479),
    "choice-1-56.csv": ("choice", 1, 56),
    "choice-57-700.csv": ("choice", 57, 700),
    "choice-701-1334.csv": ("choice", 701, 1334),
    "ui-1-108.csv": ("ui", 1, 108),
    "ui-109-450.csv": ("ui", 109, 450),
    "ui-451-800.csv": ("ui", 451, 800),
    "ui-801-1150.csv": ("ui", 801, 1150),
    "ui-1151-1340.csv": ("ui", 1151, 1340),
    "ui-1341-1533.csv": ("ui", 1341, 1533),
}


def read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def validate_batch(batch_path: Path, source_path: Path, start: int, end: int) -> list[list[str]]:
    rows = read_csv(batch_path)
    if rows and rows[0] == ["key", "original", "translation"]:
        rows = rows[1:]
    expected = read_csv(source_path)[start - 1 : end]
    errors: list[str] = []
    if len(rows) != len(expected):
        errors.append(f"{batch_path.name}: expected {len(expected)} rows, found {len(rows)}")
    expected_pairs = [(row[0], row[1]) for row in expected]
    actual_pairs = [(row[0], row[1]) for row in rows if len(row) >= 2]
    if len(set(actual_pairs)) != len(actual_pairs):
        errors.append(f"{batch_path.name}: duplicate key/original pairs")
    if set(actual_pairs) != set(expected_pairs):
        missing = len(set(expected_pairs) - set(actual_pairs))
        extra = len(set(actual_pairs) - set(expected_pairs))
        errors.append(f"{batch_path.name}: source mismatch (missing={missing}, extra={extra})")
    for index, row in enumerate(rows, start=1):
        if len(row) != 3:
            errors.append(f"{batch_path.name}:{index}: expected 3 columns, found {len(row)}")
            continue
        if row[2] == "":
            errors.append(f"{batch_path.name}:{index}: empty translation")
        if index <= len(expected):
            source = expected[index - 1]
            if row[:2] != source[:2]:
                errors.append(f"{batch_path.name}:{index}: rows are not in source order")
            if protected_tokens(row[1]) != protected_tokens(row[2]):
                errors.append(f"{batch_path.name}:{index}: protected token mismatch")
    if errors:
        raise ValueError("\n".join(errors))
    return rows


def write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--approved-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    batch_dir = args.batch_dir.resolve()
    approved_dir = args.approved_dir.resolve()

    batch_rows: dict[str, list[list[str]]] = {}
    for filename, (category, start, end) in BATCHES.items():
        path = batch_dir / filename
        if not path.exists():
            continue
        batch_rows.setdefault(category, []).extend(
            validate_batch(path, root / "resources" / "extracted" / f"{category}.csv", start, end)
        )

    for category, additions in batch_rows.items():
        target = approved_dir / f"{category}.csv"
        existing = read_csv(target) if target.exists() else []
        existing_pairs = {(row[0], row[1]) for row in existing}
        merged = existing + [row for row in additions if (row[0], row[1]) not in existing_pairs]
        write_csv(target, merged)
        print(f"{category}: {len(existing)} + {len(merged) - len(existing)} = {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
