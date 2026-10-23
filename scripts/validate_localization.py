#!/usr/bin/env python3
"""Validate approved translations and optionally assemble a release package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.translation_workspace import validate_import
from scripts.font_packaging import (
    FontPackagingError,
    FontSubsetResult,
    collect_font_characters,
    find_patch_sources,
    subset_font,
    write_character_file,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--dist", type=Path)
    return parser.parse_args(argv)


def _read_json_object(path: Path, *, label: str) -> tuple[dict[str, object], list[str]]:
    if not path.exists():
        return {}, [f"missing {label}: {path.as_posix()}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        return {}, [f"{path.name}: invalid UTF-8 ({exc})"]
    except json.JSONDecodeError as exc:
        return {}, [f"{path.name}: invalid JSON ({exc.msg})"]
    if not isinstance(payload, dict):
        return {}, [f"{path.name}: expected a JSON object"]
    return payload, []


def _read_csv_rows(path: Path) -> tuple[list[list[str]], list[str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
    except UnicodeDecodeError as exc:
        return [], [f"{path.name}: invalid UTF-8/BOM readability ({exc})"]
    except OSError as exc:
        return [], [f"{path.name}: failed to read ({exc})"]

    errors: list[str] = []
    for row_number, row in enumerate(rows, start=1):
        if len(row) != 3:
            errors.append(f"{path.name}:{row_number}: malformed row length {len(row)}")
    return rows, errors


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _project_metadata(project_root: Path) -> tuple[str, str | None]:
    csproj_path = project_root / "PsychologHan.csproj"
    if not csproj_path.exists():
        return "PsychologHan", None
    try:
        root = ET.fromstring(csproj_path.read_text(encoding="utf-8"))
    except (ET.ParseError, UnicodeDecodeError):
        return "PsychologHan", None

    assembly_name = "PsychologHan"
    version: str | None = None
    for property_group in root.findall("PropertyGroup"):
        if property_group.findtext("AssemblyName"):
            assembly_name = property_group.findtext("AssemblyName", assembly_name).strip()
        if property_group.findtext("Version"):
            version = property_group.findtext("Version", "").strip() or version
    return assembly_name, version


def _find_plugin_dll(project_root: Path, assembly_name: str) -> Path | None:
    release_candidates = sorted(
        path
        for path in (project_root / "bin" / "Release").rglob(f"{assembly_name}.dll")
        if path.is_file()
    )
    if release_candidates:
        return release_candidates[0]

    any_candidates = sorted(
        path for path in (project_root / "bin").rglob(f"{assembly_name}.dll") if path.is_file()
    )
    return any_candidates[0] if any_candidates else None


def _resolve_dist_dir(project_root: Path, dist_arg: Path) -> tuple[Path | None, str | None]:
    candidate = dist_arg if dist_arg.is_absolute() else project_root / dist_arg
    dist_dir = candidate.resolve()
    expected_dist = (project_root / "dist").resolve()
    if dist_dir != expected_dist:
        return (
            None,
            "dist must resolve to project_root/dist; "
            f"got {dist_dir.as_posix()} (expected {expected_dist.as_posix()})",
        )
    return dist_dir, None


def _validate_categories(
    *,
    translations_dir: Path,
    profile: dict[str, object],
    scope: dict[str, object],
    version: dict[str, object],
) -> tuple[list[str], dict[str, Path]]:
    errors: list[str] = []
    approved = list(scope.get("approved_categories", []))
    fallback = set(scope.get("fallback_categories", []))

    profile_categories = set()
    paratranz = profile.get("paratranz")
    if isinstance(paratranz, dict):
        profile_categories = {str(value) for value in paratranz.get("approved_categories", [])}

    version_counts_raw = version.get("approved_row_counts", {})
    version_counts = (
        {str(key): int(value) for key, value in version_counts_raw.items()}
        if isinstance(version_counts_raw, dict)
        else {}
    )

    if set(approved) != set(version_counts):
        errors.append(
            "approved categories mismatch between translation-scope.json and "
            "resources/work/translation-version.json"
        )
    if profile_categories:
        missing_from_profile = (set(approved) | fallback) - profile_categories
        for category in sorted(missing_from_profile):
            errors.append(f"category not declared in profile approved_categories: {category}")

    present_csvs = {path.stem: path for path in sorted(translations_dir.glob("*.csv"))}
    allowed_categories = set(approved) | fallback
    for category in sorted(set(present_csvs) - allowed_categories):
        errors.append(f"unexpected translation file: {present_csvs[category].name}")

    for category in approved:
        csv_path = translations_dir / f"{category}.csv"
        if not csv_path.exists():
            errors.append(f"missing approved translation file: {csv_path.name}")
            continue
        rows, row_errors = _read_csv_rows(csv_path)
        errors.extend(row_errors)
        if len(rows) != version_counts.get(category, 0):
            errors.append(
                f"{csv_path.name}: expected {version_counts.get(category, 0)} approved rows, "
                f"found {len(rows)}"
            )
    return errors, present_csvs


def _collect_validation(
    *,
    project_root: Path,
    translations_dir: Path,
    profile_path: Path,
) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    details: dict[str, object] = {}

    profile, profile_errors = _read_json_object(profile_path, label="profile")
    errors.extend(profile_errors)

    scope_path = profile_path.with_name("translation-scope.json")
    scope, scope_errors = _read_json_object(scope_path, label="translation scope")
    errors.extend(scope_errors)

    version_path = project_root / "resources" / "work" / "translation-version.json"
    version, version_errors = _read_json_object(version_path, label="translation version")
    errors.extend(version_errors)

    entries_path = project_root / "resources" / "work" / "entries.jsonl"
    if not entries_path.exists():
        errors.append(f"missing entries file: {entries_path.as_posix()}")

    if not translations_dir.exists():
        errors.append(f"missing translations directory: {translations_dir.as_posix()}")

    font_source: Path | None = None
    font_sources: list[Path] = []
    font_character_file: Path | None = None
    fonts = profile.get("fonts")
    if isinstance(fonts, dict) and fonts.get("strategy") == "runtime-ttf":
        configured_font = fonts.get("source_font", "resources/fonts/NotoSansSC-VF.ttf")
        if not isinstance(configured_font, str) or not configured_font:
            errors.append("runtime-ttf profile has no valid source_font")
        else:
            font_source = (project_root / configured_font).resolve()
            if not font_source.is_file():
                errors.append(f"missing runtime font source: {_relative_to(font_source, project_root)}")
            else:
                font_sources.append(font_source)

        mapping_sources = fonts.get("mapping_source_fonts", [])
        if mapping_sources is not None and not isinstance(mapping_sources, list):
            errors.append("runtime-ttf profile mapping_source_fonts must be a list")
        elif isinstance(mapping_sources, list):
            for configured_mapping_font in mapping_sources:
                if not isinstance(configured_mapping_font, str) or not configured_mapping_font:
                    errors.append("runtime-ttf profile has an invalid mapping source font")
                    continue
                mapping_font = (project_root / configured_mapping_font).resolve()
                if not mapping_font.is_file():
                    errors.append(f"missing mapped runtime font source: {_relative_to(mapping_font, project_root)}")
                elif mapping_font not in font_sources:
                    font_sources.append(mapping_font)

        configured_character_file = fonts.get(
            "character_file", "resources/work/font-characters.txt"
        )
        if not isinstance(configured_character_file, str) or not configured_character_file:
            errors.append("runtime-ttf profile has no valid character_file")
        else:
            font_character_file = (project_root / configured_character_file).resolve()

    present_csvs: dict[str, Path] = {}
    if not errors:
        category_errors, present_csvs = _validate_categories(
            translations_dir=translations_dir,
            profile=profile,
            scope=scope,
            version=version,
        )
        errors.extend(category_errors)

    try:
        errors.extend(validate_import(entries_path, translations_dir))
    except UnicodeDecodeError as exc:
        errors.append(f"approved translations contain invalid UTF-8/BOM data ({exc})")

    assembly_name, assembly_version = _project_metadata(project_root)
    plugin_dll = _find_plugin_dll(project_root, assembly_name)
    if plugin_dll is None:
        errors.append(f"missing plugin dll: expected build output under {_relative_to(project_root / 'bin', project_root)}")

    details.update(
        {
            "assembly_name": assembly_name,
            "assembly_version": assembly_version,
            "plugin_dll": plugin_dll,
            "profile_path": profile_path,
            "supported_game": profile.get("game", {}),
            "scope_path": scope_path,
            "scope": scope,
            "version_path": version_path,
            "version": version,
            "present_csvs": present_csvs,
            "font_source": font_source,
            "font_sources": font_sources,
            "font_character_file": font_character_file,
        }
    )
    return errors, details


def _build_manifest(
    *,
    project_root: Path,
    package_root: Path,
    plugin_target: Path,
    translation_targets: dict[str, Path],
    font_target: Path | None,
    font_targets: dict[str, Path],
    font_coverage: dict[str, object] | None,
    details: dict[str, object],
) -> dict[str, object]:
    scope = details["scope"]
    version = details["version"]
    version_path = details["version_path"]
    profile_path = details["profile_path"]
    scope_path = details["scope_path"]

    files = {
        "plugin": {
            "package_path": plugin_target.relative_to(package_root).as_posix(),
            "sha256": _sha256(plugin_target),
            "size": plugin_target.stat().st_size,
        },
        "translations": {},
    }
    if font_target is not None:
        files["font"] = {
            "package_path": font_target.relative_to(package_root).as_posix(),
            "sha256": _sha256(font_target),
            "size": font_target.stat().st_size,
        }
    if font_targets:
        files["fonts"] = {}
        fonts_section: dict[str, object] = files["fonts"]  # type: ignore[assignment]
        for file_name, target in sorted(font_targets.items()):
            fonts_section[file_name] = {
                "package_path": target.relative_to(package_root).as_posix(),
                "sha256": _sha256(target),
                "size": target.stat().st_size,
            }
    translations_section: dict[str, object] = files["translations"]  # type: ignore[assignment]
    for category, target in sorted(translation_targets.items()):
        translations_section[category] = {
            "package_path": target.relative_to(package_root).as_posix(),
            "sha256": _sha256(target),
            "size": target.stat().st_size,
        }

    manifest = {
        "schema_version": 1,
        "locale": scope.get("locale") or version.get("locale"),
        "approved_categories": list(scope.get("approved_categories", [])),
        "fallback_categories": list(scope.get("fallback_categories", [])),
        "profile": _relative_to(profile_path, project_root),
        "translation_scope": _relative_to(scope_path, project_root),
        "translation_version": {
            "path": _relative_to(version_path, project_root),
            "sha256": _sha256(version_path),
            "approved_row_counts": version.get("approved_row_counts", {}),
            "source_manifest": version.get("source_manifest", {}),
        },
        "plugin": {
            "assembly_name": details["assembly_name"],
            "assembly_version": details["assembly_version"],
        },
        "supported_game": details.get("supported_game", {}),
        "files": files,
    }
    if font_coverage is not None:
        manifest["font_coverage"] = font_coverage
    return manifest


def _create_dist_package(
    *,
    project_root: Path,
    translations_dir: Path,
    dist_dir: Path,
    details: dict[str, object],
) -> Path:
    package_root = dist_dir / "BepInEx" / "plugins" / "PsychologHan"
    plugin_dll = details["plugin_dll"]
    assert isinstance(plugin_dll, Path)
    plugin_target = package_root / plugin_dll.name

    font_source = details.get("font_source")
    font_target: Path | None = None
    font_targets: dict[str, Path] = {}
    font_coverage: dict[str, object] | None = None
    font_sources = details.get("font_sources", [])
    typed_font_sources: list[Path] = []
    subset_results: dict[str, FontSubsetResult] = {}
    if isinstance(font_sources, list):
        typed_font_sources = [
            configured_font
            for configured_font in font_sources
            if isinstance(configured_font, Path)
        ]
        if typed_font_sources:
            character_file = details.get("font_character_file")
            if not isinstance(character_file, Path):
                raise FontPackagingError(
                    "runtime-ttf profile has no resolved font character file"
                )

            patch_sources = find_patch_sources(project_root)
            characters = collect_font_characters(translations_dir, patch_sources)
            write_character_file(character_file, characters)

            work_dir = project_root / "resources" / "work"
            work_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(
                prefix="font-subset-", dir=str(work_dir)
            ) as temporary_directory:
                temporary_root = Path(temporary_directory)
                for configured_font in typed_font_sources:
                    if configured_font.name in subset_results:
                        raise FontPackagingError(
                            "multiple configured fonts have the same file name: "
                            f"{configured_font.name}"
                        )
                    subset_target = temporary_root / configured_font.name
                    subset_results[configured_font.name] = subset_font(
                        configured_font,
                        subset_target,
                        characters,
                    )

                if package_root.exists():
                    shutil.rmtree(package_root)
                (package_root / "localization").mkdir(parents=True, exist_ok=True)
                shutil.copy2(plugin_dll, plugin_target)
                for configured_font in typed_font_sources:
                    result = subset_results[configured_font.name]
                    target = package_root / "fonts" / configured_font.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(result.target, target)
                    font_targets[configured_font.name] = target
                    if isinstance(font_source, Path) and configured_font == font_source:
                        font_target = target

            font_coverage = {
                "character_file": _relative_to(character_file, project_root),
                "character_file_sha256": _sha256(character_file),
                "character_count": len(characters),
                "patch_sources": [
                    _relative_to(path, project_root) for path in patch_sources
                ],
                "fonts": {
                    file_name: {
                        "source_path": _relative_to(result.source, project_root),
                        "source_sha256": _sha256(result.source),
                        "source_size": result.source_size,
                        "target_size": result.target_size,
                        "reduction_bytes": result.reduction_bytes,
                        "requested_character_count": result.requested_character_count,
                        "available_character_count": result.available_character_count,
                        "missing_characters": result.missing_characters,
                    }
                    for file_name, result in sorted(subset_results.items())
                },
            }

    if not typed_font_sources:
        if package_root.exists():
            shutil.rmtree(package_root)
        (package_root / "localization").mkdir(parents=True, exist_ok=True)
        shutil.copy2(plugin_dll, plugin_target)

    scope = details["scope"]
    translation_targets: dict[str, Path] = {}
    for category in scope.get("approved_categories", []):
        csv_path = translations_dir / f"{category}.csv"
        target = package_root / "localization" / csv_path.name
        shutil.copy2(csv_path, target)
        translation_targets[str(category)] = target

    manifest = _build_manifest(
        project_root=project_root,
        package_root=package_root,
        plugin_target=plugin_target,
        translation_targets=translation_targets,
        font_target=font_target,
        font_targets=font_targets,
        font_coverage=font_coverage,
        details=details,
    )
    (package_root / "package-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return package_root


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    project_root = args.project_root.resolve()
    translations_dir = args.translations.resolve()
    profile_path = args.profile.resolve()
    dist_dir: Path | None = None
    if args.dist is not None:
        dist_dir, dist_error = _resolve_dist_dir(project_root, args.dist)
        if dist_error is not None:
            print(dist_error)
            return 1

    errors, details = _collect_validation(
        project_root=project_root,
        translations_dir=translations_dir,
        profile_path=profile_path,
    )
    if errors:
        for error in errors:
            print(error)
        return 1

    if dist_dir is not None:
        try:
            package_root = _create_dist_package(
                project_root=project_root,
                translations_dir=translations_dir,
                dist_dir=dist_dir,
                details=details,
            )
        except FontPackagingError as error:
            print(f"font packaging failed: {error}")
            return 1
        print(f"validation ok; package created at {package_root.as_posix()}")
        return 0

    print("validation ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
