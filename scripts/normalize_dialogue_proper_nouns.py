#!/usr/bin/env python3
"""Normalize proper nouns in the approved dialogue translations.

Only the translation column is changed. Source keys and originals remain
byte-for-byte represented by the CSV fields so the localization validator can
continue to enforce source identity.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


REPLACEMENTS = {
    "Benny's": "本尼餐馆",
    "Longhorn Street": "长角街",
    "Vera": "薇拉",
    "Jaden": "杰登",
    "Emily": "艾米莉",
    "Wilson": "威尔逊",
    "Jackson": "杰克逊",
    "Steven": "史蒂文",
    "Julie": "朱莉",
    "Mandy": "曼迪",
    "Mark": "马克",
    "Hannah": "汉娜",
    "Thompson": "汤普森",
    "Jennifer": "珍妮弗",
    "Frank": "弗兰克",
    "Joe": "乔",
    "Em": "艾米",
}

TOKEN_PATTERN = re.compile(
    r"(?<![A-Za-z])(?:Longhorn\s+街|[A-Za-z]+(?:'[A-Za-z]+)?)(?![A-Za-z])",
    re.IGNORECASE,
)


def normalize_translation(text: str) -> tuple[str, int]:
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        token = match.group(0)
        if token.casefold() == "longhorn 街":
            replacement = "长角街"
        else:
            replacement = next(
                (value for key, value in REPLACEMENTS.items() if key.casefold() == token.casefold()),
                token,
            )
        if replacement != token:
            replacements += 1
        return replacement

    normalized = TOKEN_PATTERN.sub(replace, text)
    chinese_terms = [*REPLACEMENTS.values(), "长角街"]
    for term in chinese_terms:
        normalized = re.sub(rf"(?<=[\u4e00-\u9fff])\s+{re.escape(term)}", term, normalized)
        normalized = re.sub(rf"{re.escape(term)}\s+(?=[\u4e00-\u9fff])", term, normalized)
    normalized = normalized.replace("JW 大楼", "JW大楼")
    normalized = normalized.replace("杰登 汤普森", "杰登·汤普森")
    return normalized, replacements


def normalize_csv(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    total_replacements = 0
    for row in rows:
        if len(row) != 3:
            raise ValueError(f"{path}: expected three columns, got {len(row)}")
        row[2], replacements = normalize_translation(row[2])
        total_replacements += replacements

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)
    return total_replacements


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()
    count = normalize_csv(args.path)
    print(f"normalized {count} proper-noun occurrences in {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
