#!/usr/bin/env python3
"""Apply reviewed Chinese translations for runtime-generated UI rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


TRANSLATIONS = {
    "March 11": "3月11日",
    "March 12": "3月12日",
    "March 14": "3月14日",
    "March 15": "3月15日",
    "March 18": "3月18日",
    "March 19": "3月19日",
    "March 20": "3月20日",
    "March 21": "3月21日",
    "March 22": "3月22日",
    "Monday morning": "星期一早晨",
    "Monday afternoon": "星期一下午",
    "Tuesday morning": "星期二早晨",
    "Tuesday afternoon": "星期二下午",
    "Wednesday afternoon": "星期三下午",
    "Thursday morning": "星期四早晨",
    "Thursday afternoon": "星期四下午",
    "Friday morning": "星期五早晨",
    "Friday afternoon": "星期五下午",
    "JOE": "乔",
    "DEBORAH": "黛博拉",
    "VERA": "薇拉",
    "JADEN": "杰登",
    "ASHLEY": "阿什莉",
    "RAYMOND": "雷蒙德",
    "MEETING IN THE PARK": "在公园会面",
    "LUNCH AT BENNY'S": "在本尼餐馆吃午饭",
    "(one month later)": "（一个月后）",
    "(exposure session no. 1)": "（第1次暴露练习）",
    "(exposure session no. 2)": "（第2次暴露练习）",
    "(exposure session no. 5)": "（第5次暴露练习）",
    "(first session)": "（第一次会谈）",
    "(second session)": "（第二次会谈）",
    "(third session)": "（第三次会谈）",
    "(fourth session)": "（第四次会谈）",
    "(fifth session)": "（第五次会谈）",
    "(seventh session)": "（第七次会谈）",
    "(visit at the hospital)": "（在医院会面）",
    "(unplanned session)": "（临时会谈）",
}

PROGRESS_BAR_TRANSLATIONS = {
    "TREATMENT": "治疗",
    "TRUST": "信任",
}


def read_csv(path: Path) -> list[list[str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)


def update_translation_version(project_root: Path, approved_ui_count: int) -> None:
    version_path = project_root / "resources" / "work" / "translation-version.json"
    manifest_path = project_root / "resources" / "work" / "source-manifest.sha256"
    if not version_path.exists():
        return

    version = json.loads(version_path.read_text(encoding="utf-8"))
    if not isinstance(version, dict):
        raise ValueError(f"{version_path.name}: expected a JSON object")
    counts = version.setdefault("approved_row_counts", {})
    if not isinstance(counts, dict):
        raise ValueError(f"{version_path.name}: approved_row_counts must be an object")
    counts["ui"] = approved_ui_count

    source_manifest = version.setdefault("source_manifest", {})
    if not isinstance(source_manifest, dict):
        raise ValueError(f"{version_path.name}: source_manifest must be an object")
    if manifest_path.exists():
        source_manifest["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest().upper()

    version_path.write_text(
        json.dumps(version, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def apply_translations(project_root: Path) -> int:
    source_path = project_root / "resources" / "extracted" / "ui.csv"
    target_path = project_root / "resources" / "work" / "approved-translations" / "ui.csv"
    source_rows = read_csv(source_path)
    target_rows = read_csv(target_path)

    rows_by_key: dict[str, list[str]] = {}
    for row in target_rows:
        if len(row) != 3:
            raise ValueError(f"{target_path.name}: expected three columns, found {len(row)}")
        if row[0] in rows_by_key:
            raise ValueError(f"{target_path.name}: duplicate key {row[0]}")
        rows_by_key[row[0]] = row

    title_rows = [row for row in source_rows if len(row) == 3 and "|||ClientSessionTitle|||" in row[0]]
    if not title_rows:
        raise ValueError(f"no ClientSessionTitle rows found in {source_path}")

    heading_rows = [
        row for row in source_rows
        if len(row) == 3 and "|||changeProgressionMetric|||heading|||" in row[0]
    ]
    if not heading_rows:
        raise ValueError(f"no progress-bar heading rows found in {source_path}")

    added_or_updated = 0
    for row in [*title_rows, *heading_rows]:
        key, original = row[:2]
        if "|||ClientSessionTitle|||" in key:
            translation = TRANSLATIONS.get(original)
            row_type = "ClientSessionTitle"
        else:
            translation = PROGRESS_BAR_TRANSLATIONS.get(original)
            row_type = "progress-bar heading"
        if translation is None:
            raise ValueError(f"missing {row_type} translation for {original!r}")

        existing = rows_by_key.get(key)
        if existing is not None:
            if existing[1] != original:
                raise ValueError(f"{target_path.name}: changed original for {key}")
            existing[2] = translation
            added_or_updated += 1
            continue

        translated_row = [key, original, translation]
        target_rows.append(translated_row)
        rows_by_key[key] = translated_row
        added_or_updated += 1

    write_csv(target_path, target_rows)
    update_translation_version(project_root, len(target_rows))
    return added_or_updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    count = apply_translations(args.project_root.resolve())
    print(f"wrote {count} reviewed runtime UI translations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
