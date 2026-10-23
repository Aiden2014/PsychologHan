"""Collect localization glyphs and create reduced runtime TTF files.

The release validator imports this module instead of copying the original
fonts.  Character collection intentionally stays standard-library-only; TTF
subsetting uses the well-known ``fontTools`` package at release time because
the Python standard library has no font table writer.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


STRUCTURAL_ASCII_SEPARATORS = frozenset(" \t\r\n\v\f")
PATCH_SOURCE_EXCLUDED_PARTS = frozenset(
    {
        ".git",
        ".skill-build",
        ".venv",
        "artifacts",
        "bin",
        "dist",
        "obj",
        "reports",
        "resources",
        "tests",
    }
)


class FontPackagingError(RuntimeError):
    """Raised when glyph collection or font subsetting cannot complete."""


@dataclass(frozen=True)
class FontSubsetResult:
    """Auditable result for one source font."""

    source: Path
    target: Path
    requested_character_count: int
    available_character_count: int
    missing_characters: str
    source_size: int
    target_size: int

    @property
    def reduction_bytes(self) -> int:
        return self.source_size - self.target_size


def _decode_escape(source: str, index: int) -> tuple[str, int]:
    """Decode one C# escape beginning at ``source[index] == "\\"``."""

    if index + 1 >= len(source):
        return "\\", index + 1

    escaped = source[index + 1]
    simple_escapes = {
        "0": "\0",
        "a": "\a",
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "v": "\v",
        "\\": "\\",
        "\"": "\"",
        "'": "'",
    }
    if escaped in simple_escapes:
        return simple_escapes[escaped], index + 2

    if escaped in {"x", "u", "U"}:
        digit_count = {"x": 4, "u": 4, "U": 8}[escaped]
        end = index + 2 + digit_count
        digits = source[index + 2 : end]
        if len(digits) == digit_count and all(
            character in "0123456789abcdefABCDEF" for character in digits
        ):
            codepoint = int(digits, 16)
            try:
                return chr(codepoint), end
            except ValueError:
                return "", end

        # C# also permits one to four hexadecimal digits for ``\x``.  The
        # exact four-digit branch above handles the common case; consume the
        # longest valid shorter sequence when the full form is not present.
        if escaped == "x":
            end = index + 2
            while (
                end < len(source)
                and end < index + 6
                and source[end] in "0123456789abcdefABCDEF"
            ):
                end += 1
            if end > index + 2:
                return chr(int(source[index + 2 : end], 16)), end

    # Invalid C# escapes are compile errors, but preserving the escaped
    # character keeps collection useful for source that is being edited.
    return escaped, index + 2


def _consume_quoted_literal(
    source: str,
    quote_index: int,
    *,
    quote: str,
    verbatim: bool,
    raw: bool,
) -> tuple[str, int]:
    """Return literal value and the first index after its closing quote."""

    if raw:
        delimiter = quote * 3
        content_start = quote_index + 3
        closing = source.find(delimiter, content_start)
        if closing < 0:
            return source[content_start:], len(source)
        return source[content_start:closing], closing + 3

    index = quote_index + 1
    value: list[str] = []
    while index < len(source):
        character = source[index]
        if character == quote:
            if verbatim and index + 1 < len(source) and source[index + 1] == quote:
                value.append(quote)
                index += 2
                continue
            return "".join(value), index + 1
        if not verbatim and character == "\\":
            decoded, index = _decode_escape(source, index)
            value.append(decoded)
            continue
        value.append(character)
        index += 1
    return "".join(value), len(source)


def iter_csharp_literal_text(source: str) -> Iterator[str]:
    """Yield decoded text from C# string and character literals.

    Comments are ignored.  The parser deliberately treats the literal parts
    of interpolated strings as source text; values produced by interpolation
    are covered by the CSV corpus or by another literal in the patch.
    """

    index = 0
    while index < len(source):
        character = source[index]

        if character == "/" and index + 1 < len(source):
            next_character = source[index + 1]
            if next_character == "/":
                newline = source.find("\n", index + 2)
                index = len(source) if newline < 0 else newline + 1
                continue
            if next_character == "*":
                closing = source.find("*/", index + 2)
                index = len(source) if closing < 0 else closing + 2
                continue

        quote_index = index
        quote = character if character in {"'", '"'} else ""
        verbatim = False
        if not quote and character in "@$":
            prefix_start = index
            while index < len(source) and source[index] in "@$":
                index += 1
            if index < len(source) and source[index] == '"':
                quote_index = index
                quote = '"'
                verbatim = "@" in source[prefix_start:index]
            else:
                index = prefix_start

        if quote:
            raw = quote == '"' and source.startswith('"""', quote_index)
            literal, index = _consume_quoted_literal(
                source,
                quote_index,
                quote=quote,
                verbatim=verbatim,
                raw=raw,
            )
            yield literal
            continue

        index += 1


def _iter_csv_texts(translations_dir: Path) -> Iterator[str]:
    csv_paths = sorted(
        path for path in translations_dir.rglob("*.csv") if path.is_file()
    )
    if not csv_paths:
        raise FontPackagingError(
            f"no CSV files found under approved translations: {translations_dir.as_posix()}"
        )

    for path in csv_paths:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.reader(handle):
                    yield from row
        except (OSError, UnicodeDecodeError, csv.Error) as error:
            raise FontPackagingError(
                f"could not read translation CSV {path.as_posix()}: {error}"
            ) from error


def find_patch_sources(project_root: Path) -> list[Path]:
    """Find C# source files compiled into the main patch.

    The child ``PsychologEnhance`` project is intentionally excluded because
    it is not compiled into or shipped by ``PsychologHan.csproj``.  Generated
    and extracted directories are excluded so a previous build cannot change
    the glyph set.
    """

    sources: list[Path] = []
    for path in project_root.rglob("*.cs"):
        relative_parts = path.relative_to(project_root).parts
        if any(part in PATCH_SOURCE_EXCLUDED_PARTS for part in relative_parts):
            continue
        if "PsychologEnhance" in relative_parts:
            continue
        if path.is_file():
            sources.append(path)
    return sorted(sources)


def _filtered_characters(values: Iterable[str]) -> str:
    characters: set[str] = set()
    for value in values:
        characters.update(
            character
            for character in value
            if character not in STRUCTURAL_ASCII_SEPARATORS
        )
    return "".join(sorted(characters))


def collect_font_characters(
    translations_dir: Path,
    patch_sources: Sequence[Path],
) -> str:
    """Collect sorted unique glyph characters from translations and patch literals."""

    values: Iterator[str]

    def all_values() -> Iterator[str]:
        yield from _iter_csv_texts(translations_dir)
        for source_path in patch_sources:
            try:
                yield from iter_csharp_literal_text(
                    source_path.read_text(encoding="utf-8-sig")
                )
            except (OSError, UnicodeDecodeError) as error:
                raise FontPackagingError(
                    f"could not read patch source {source_path.as_posix()}: {error}"
                ) from error

    values = all_values()
    characters = _filtered_characters(values)
    if not characters:
        raise FontPackagingError(
            "the approved translations and patch literals produced an empty glyph set"
        )
    return characters


def write_character_file(path: Path, characters: str) -> None:
    """Write the auditable deterministic character file."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(characters + "\n", encoding="utf-8", newline="\n")
    except OSError as error:
        raise FontPackagingError(
            f"could not write font character file {path.as_posix()}: {error}"
        ) from error


def subset_font(source: Path, target: Path, characters: str) -> FontSubsetResult:
    """Subset one TTF with fontTools and return coverage metadata."""

    if not source.is_file():
        raise FontPackagingError(f"missing source font: {source.as_posix()}")

    try:
        from fontTools import subset
    except ImportError as error:
        raise FontPackagingError(
            "font subsetting requires fontTools; install it with "
            "'python -m pip install fonttools' and rerun the release validator"
        ) from error

    requested_codepoints = {ord(character) for character in characters}
    try:
        options = subset.Options()
        # Runtime TMP font creation needs glyphs, metrics, and names, but not
        # the source font's full shaping feature closure.  Keeping layout
        # features empty prevents a feature table from pulling unrelated CJK
        # glyphs back into the reduced file.
        options.layout_features = []
        options.name_IDs = ["*"]
        options.name_languages = ["*"]
        options.notdef_glyph = True
        options.recalc_timestamp = False
        options.canonical_order = True

        font = subset.load_font(str(source), options)
        source_cmap = font.getBestCmap() or {}
        available_codepoints = requested_codepoints.intersection(source_cmap)
        missing_characters = "".join(
            sorted(
                chr(codepoint)
                for codepoint in requested_codepoints - available_codepoints
            )
        )

        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=requested_codepoints)
        subsetter.subset(font)

        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.unlink()
        subset.save_font(font, str(target), options)
    except FontPackagingError:
        raise
    except Exception as error:
        raise FontPackagingError(
            f"could not subset {source.as_posix()} to {target.as_posix()}: "
            f"{type(error).__name__}: {error}"
        ) from error

    if not target.is_file():
        raise FontPackagingError(
            f"font subsetting produced no output: {target.as_posix()}"
        )

    return FontSubsetResult(
        source=source,
        target=target,
        requested_character_count=len(requested_codepoints),
        available_character_count=len(available_codepoints),
        missing_characters=missing_characters,
        source_size=source.stat().st_size,
        target_size=target.stat().st_size,
    )
