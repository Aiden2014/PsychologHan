import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.font_packaging import (
    FontSubsetResult,
    collect_font_characters,
    iter_csharp_literal_text,
)
from scripts.validate_localization import main


class FontCharacterCollectionTests(unittest.TestCase):
    def test_csharp_literals_decode_escapes_and_ignore_comments(self):
        source = r'''
        // "评论里的字" must not be collected.
        var regular = "甲\u4e59\n";
        var verbatim = @"丙""丁";
        var symbol = '\u2605';
        /* "块注释里的字" */
        '''

        literals = list(iter_csharp_literal_text(source))

        self.assertEqual(literals, ["甲乙\n", '丙"丁', "★"])

    def test_collection_reads_all_csv_files_and_patch_literals(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            translations = root / "approved-translations"
            translations.mkdir()
            with (translations / "first.csv").open(
                "w", encoding="utf-8-sig", newline=""
            ) as handle:
                csv.writer(handle).writerow(["key", "原文", "翻译甲"])
            nested = translations / "nested"
            nested.mkdir()
            with (nested / "second.csv").open(
                "w", encoding="utf-8", newline=""
            ) as handle:
                csv.writer(handle).writerow(["key2", "乙", "丙"])
            patch_source = root / "GamePatches.cs"
            patch_source.write_text(
                'const string Hardcoded = "补丁\\u2605"; // "不应出现"\n',
                encoding="utf-8",
            )

            characters = collect_font_characters(translations, [patch_source])

            self.assertEqual(characters, "2eky★丁丙乙原文甲翻补译")
            self.assertNotIn("\n", characters)
            self.assertNotIn("不应出现", characters)


class FontPackagingIntegrationTests(unittest.TestCase):
    def test_release_package_subsets_each_configured_font_and_records_coverage(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory) / "project"
            self._write_fixture_project(project)
            subset_calls = []

            def fake_subset(source, target, characters):
                subset_calls.append((source, target, characters))
                target.write_bytes(source.read_bytes() + b"-subset")
                return FontSubsetResult(
                    source=source,
                    target=target,
                    requested_character_count=len(characters),
                    available_character_count=len(characters),
                    missing_characters="",
                    source_size=source.stat().st_size,
                    target_size=target.stat().st_size,
                )

            with patch("scripts.validate_localization.subset_font", side_effect=fake_subset):
                exit_code = main(
                    [
                        "--project-root",
                        str(project),
                        "--translations",
                        str(project / "resources" / "work" / "approved-translations"),
                        "--profile",
                        str(project / "localization" / "project-profile.json"),
                        "--dist",
                        str(project / "dist"),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(subset_calls), 3)
            characters = subset_calls[0][2]
            self.assertTrue(all(character in characters for character in "补丁"))
            self.assertIn("译", characters)
            self.assertEqual({call[2] for call in subset_calls}, {characters})

            package_root = project / "dist" / "BepInEx" / "plugins" / "PsychologHan"
            for file_name in (
                "南西油墨宋.ttf",
                "朝華打字機.ttf",
                "JasonHandwriting1-Regular.ttf",
            ):
                self.assertEqual(
                    (package_root / "fonts" / file_name).read_bytes()[-7:], b"-subset"
                )

            character_file = project / "resources" / "work" / "font-characters.txt"
            self.assertEqual(character_file.read_text(encoding="utf-8")[-1], "\n")
            manifest = json.loads(
                (package_root / "package-manifest.json").read_text(encoding="utf-8")
            )
            coverage = manifest["font_coverage"]
            self.assertEqual(coverage["character_file"], "resources/work/font-characters.txt")
            self.assertEqual(coverage["character_count"], len(characters))
            self.assertEqual(
                sorted(coverage["fonts"]),
                [
                    "JasonHandwriting1-Regular.ttf",
                    "南西油墨宋.ttf",
                    "朝華打字機.ttf",
                ],
            )
            self.assertEqual(coverage["patch_sources"], ["Plugin.cs"])

    def _write_fixture_project(self, project: Path) -> None:
        profile = {
            "paratranz": {"approved_categories": ["ui"]},
            "fonts": {
                "strategy": "runtime-ttf",
                "source_font": "resources/fonts/南西油墨宋.ttf",
                "character_file": "resources/work/font-characters.txt",
                "mapping_source_fonts": [
                    "resources/fonts/朝華打字機.ttf",
                    "resources/fonts/JasonHandwriting1-Regular.ttf",
                ],
            },
        }
        scope = {
            "locale": "zh-CN",
            "approved_categories": ["ui"],
            "fallback_categories": [],
        }
        version = {
            "locale": "zh-CN",
            "source_manifest": {},
            "approved_row_counts": {"ui": 1},
        }
        self._write_json(project / "localization" / "project-profile.json", profile)
        self._write_json(project / "localization" / "translation-scope.json", scope)
        self._write_json(
            project / "resources" / "work" / "translation-version.json", version
        )
        entries_path = project / "resources" / "work" / "entries.jsonl"
        entries_path.parent.mkdir(parents=True, exist_ok=True)
        entries_path.write_text(
            json.dumps(
                {
                    "category": "ui",
                    "key": "hello",
                    "original": "Hello",
                    "source_csv": "ui.csv",
                    "row_number": 1,
                    "source_hash": "f" * 64,
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        translation_path = (
            project / "resources" / "work" / "approved-translations" / "ui.csv"
        )
        translation_path.parent.mkdir(parents=True, exist_ok=True)
        with translation_path.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow(["hello", "Hello", "翻译"])

        (project / "Plugin.cs").write_text(
            'internal const string Marker = "补丁";\n', encoding="utf-8"
        )
        for file_name in (
            "南西油墨宋.ttf",
            "朝華打字機.ttf",
            "JasonHandwriting1-Regular.ttf",
        ):
            path = project / "resources" / "fonts" / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(file_name.encode("utf-8"))
        plugin = project / "bin" / "Release" / "netstandard2.1" / "PsychologHan.dll"
        plugin.parent.mkdir(parents=True, exist_ok=True)
        plugin.write_bytes(b"plugin")

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
