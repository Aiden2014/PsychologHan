#!/usr/bin/env python3
"""Export and validate a translation workspace from extracted Psycholog CSVs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

TRANSLATION_CATEGORIES = (
    "dialogue",
    "choice",
    "item",
    "character_name",
    "client_info",
    "ending",
    "ui",
)
BRACE_TOKEN_PREFIXES = ("{EXPR_",)


def translation_key(category: str, key: str) -> str:
    return f"{category}|||{key}"


def protected_tokens(text: str) -> tuple[str, ...]:
    tokens: list[str] = []
    index = 0
    while index < len(text):
        if text.startswith("\r\n", index):
            tokens.append("\n")
            index += 2
            continue
        char = text[index]
        if char in "\r\n":
            tokens.append("\n")
            index += 1
            continue
        if char == "\\" and index + 1 < len(text) and text[index + 1] in {'\\', "n", "r", "t", '"', "'"}:
            tokens.append(text[index:index + 2])
            index += 2
            continue
        if char == "{":
            closing = text.find("}", index + 1)
            if closing > index + 1:
                candidate = text[index:closing + 1]
                inner = candidate[1:-1]
                if inner.isdigit() or inner.isidentifier() or inner.startswith(BRACE_TOKEN_PREFIXES):
                    tokens.append(candidate)
                    index = closing + 1
                    continue
        if char == "<":
            closing = text.find(">", index + 1)
            if closing > index + 1:
                candidate = text[index:closing + 1]
                if "\n" not in candidate and "\r" not in candidate:
                    tokens.append(candidate)
                    index = closing + 1
                    continue
        index += 1
    return tuple(tokens)


def export_entries(project_root: Path, output_dir: Path) -> dict[str, int]:
    extracted_dir = project_root / "resources" / "extracted"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "approved-translations").mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    for category in TRANSLATION_CATEGORIES:
        source_path = extracted_dir / f"{category}.csv"
        if not source_path.exists():
            continue
        rows = _read_source_rows(source_path)
        if not rows:
            continue
        counts[category] = len(rows)
        _write_csv(output_dir / f"{category}.csv", rows)
        for row_number, (key, original, _translated) in enumerate(rows, start=1):
            entries.append(
                {
                    "category": category,
                    "key": key,
                    "original": original,
                    "source_csv": source_path.name,
                    "row_number": row_number,
                    "source_hash": _source_hash(category, key, original, source_path.name, row_number),
                }
            )

    _write_entries_jsonl(output_dir / "entries.jsonl", entries)
    _write_manifest(project_root, extracted_dir, output_dir / "source-manifest.sha256")
    return counts


def validate_import(entries_path: Path, translations_dir: Path) -> list[str]:
    entries, load_errors = _load_entries(entries_path)
    if load_errors:
        return load_errors
    if not translations_dir.exists():
        return []

    errors: list[str] = []
    seen_keys: set[str] = set()
    for csv_path in sorted(translations_dir.glob("*.csv")):
        category = csv_path.stem
        for row_number, row in _iter_csv_rows(csv_path):
            if len(row) != 3:
                errors.append(f"{csv_path.name}:{row_number}: malformed row length {len(row)}")
                continue
            key, original, translated = row
            combined_key = translation_key(category, key)
            if combined_key in seen_keys:
                errors.append(f"{csv_path.name}:{row_number}: duplicate key {key}")
            else:
                seen_keys.add(combined_key)

            entry = entries.get(combined_key)
            if entry is None:
                errors.append(f"{csv_path.name}:{row_number}: unknown key {key}")
                continue
            if original != entry["original"]:
                errors.append(f"{csv_path.name}:{row_number}: changed original for {key}")
            if translated == "":
                errors.append(f"{csv_path.name}:{row_number}: empty translation for {key}")
            if _newline_count(original) != _newline_count(translated):
                errors.append(f"{csv_path.name}:{row_number}: newline count changed for {key}")
            if protected_tokens(original) != protected_tokens(translated):
                errors.append(f"{csv_path.name}:{row_number}: protected token change for {key}")
    return errors


def _iter_csv_rows(path: Path) -> list[tuple[int, list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(enumerate(csv.reader(handle), start=1))


def _read_source_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for row_number, row in _iter_csv_rows(path):
        if len(row) != 3:
            raise ValueError(f"{path.name}:{row_number}: expected 3 columns, found {len(row)}")
        rows.append(row)
    return rows


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


def _write_entries_jsonl(path: Path, entries: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def _write_manifest(project_root: Path, extracted_dir: Path, manifest_path: Path) -> None:
    lines: list[str] = []
    if extracted_dir.exists():
        for source_path in sorted(extracted_dir.glob("*.csv")):
            digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
            lines.append(f"{digest} *{source_path.relative_to(project_root).as_posix()}")
    manifest_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _source_hash(category: str, key: str, original: str, source_csv: str, row_number: int) -> str:
    digest = hashlib.sha256()
    digest.update(category.encode("utf-8"))
    digest.update(b"\0")
    digest.update(key.encode("utf-8"))
    digest.update(b"\0")
    digest.update(original.encode("utf-8"))
    digest.update(b"\0")
    digest.update(source_csv.encode("utf-8"))
    digest.update(b"\0")
    digest.update(str(row_number).encode("utf-8"))
    return digest.hexdigest()


def _load_entries(entries_path: Path) -> tuple[dict[str, dict[str, object]], list[str]]:
    if not entries_path.exists():
        return {}, [f"entries file not found: {entries_path}"]

    entries: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    for row_number, line in enumerate(entries_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{entries_path.name}:{row_number}: invalid JSON ({exc.msg})")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{entries_path.name}:{row_number}: entry must be an object")
            continue
        category = str(payload.get("category", ""))
        key = str(payload.get("key", ""))
        original = str(payload.get("original", ""))
        combined_key = translation_key(category, key)
        payload["original"] = original
        entries[combined_key] = payload
    return entries, errors


def _newline_count(text: str) -> int:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.count("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--project-root", type=Path, required=True)
    export_parser.add_argument("--output-dir", type=Path, required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--entries", type=Path, required=True)
    validate_parser.add_argument("--translations", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "export":
        counts = export_entries(args.project_root.resolve(), args.output_dir.resolve())
        print(json.dumps(counts, ensure_ascii=False, sort_keys=True))
        return 0

    errors = validate_import(args.entries.resolve(), args.translations.resolve())
    if errors:
        for error in errors:
            print(error)
        return 1
    print("validation ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
