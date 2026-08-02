import contextlib
import csv
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_localization import main


class ValidateLocalizationTests(unittest.TestCase):
    def test_main_validates_workspace_and_builds_dist_package(self):
        project = Path(self._tmp_dir()) / "project"
        self._write_fixture_project(
            project,
            approved_counts={"character_name": 1, "ui": 1},
            approved_rows={
                "character_name": [["hero", "Hero", "英雄"]],
                "ui": [["quit", "Quit", "退出"]],
            },
            entries=[
                {"category": "character_name", "key": "hero", "original": "Hero"},
                {"category": "ui", "key": "quit", "original": "Quit"},
                {"category": "dialogue", "key": "intro", "original": "Hello {0}"},
            ],
            include_plugin=True,
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
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

        self.assertEqual(exit_code, 0, stdout.getvalue())
        package_root = project / "dist" / "BepInEx" / "plugins" / "PsychologHan"
        self.assertTrue((package_root / "PsychologHan.dll").exists())
        self.assertTrue((package_root / "localization" / "character_name.csv").exists())
        self.assertTrue((package_root / "localization" / "ui.csv").exists())
        manifest = json.loads((package_root / "package-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["locale"], "zh-CN")
        self.assertEqual(
            sorted(manifest["approved_categories"]),
            ["character_name", "ui"],
        )
        self.assertIn("plugin", manifest["files"])
        self.assertEqual(
            manifest["files"]["plugin"]["sha256"],
            self._sha256(package_root / "PsychologHan.dll"),
        )

    def test_main_rejects_dist_outside_project_without_deleting_existing_package(self):
        project = Path(self._tmp_dir()) / "project"
        outside_dist = Path(self._tmp_dir()) / "external-dist"
        self._write_fixture_project(
            project,
            approved_counts={"character_name": 1},
            approved_rows={"character_name": [["hero", "Hero", "英雄"]]},
            entries=[{"category": "character_name", "key": "hero", "original": "Hero"}],
            include_plugin=True,
        )
        external_package = outside_dist / "BepInEx" / "plugins" / "PsychologHan"
        external_package.mkdir(parents=True)
        protected_file = external_package / "protected.txt"
        protected_file.write_text("must not be deleted", encoding="utf-8")

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--project-root",
                    str(project),
                    "--translations",
                    str(project / "resources" / "work" / "approved-translations"),
                    "--profile",
                    str(project / "localization" / "project-profile.json"),
                    "--dist",
                    str(outside_dist),
                ]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("dist must resolve to project_root/dist", stdout.getvalue())
        self.assertTrue(protected_file.exists())

    def test_main_rejects_project_root_as_dist(self):
        project = Path(self._tmp_dir()) / "project"
        self._write_fixture_project(
            project,
            approved_counts={"character_name": 1},
            approved_rows={"character_name": [["hero", "Hero", "英雄"]]},
            entries=[{"category": "character_name", "key": "hero", "original": "Hero"}],
            include_plugin=True,
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--project-root",
                    str(project),
                    "--translations",
                    str(project / "resources" / "work" / "approved-translations"),
                    "--profile",
                    str(project / "localization" / "project-profile.json"),
                    "--dist",
                    str(project),
                ]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("dist must resolve to project_root/dist", stdout.getvalue())

    def test_main_reports_missing_or_invalid_translations(self):
        project = Path(self._tmp_dir()) / "project"
        self._write_fixture_project(
            project,
            approved_counts={"character_name": 1, "ui": 1, "ending": 1},
            approved_rows={
                "character_name": [["hero", "Hero", "英雄"]],
                "ui": [["quit", "Quit changed", ""]],
            },
            entries=[
                {"category": "character_name", "key": "hero", "original": "Hero"},
                {"category": "ui", "key": "quit", "original": "Quit"},
                {"category": "ending", "key": "good", "original": "Good End"},
            ],
            include_plugin=False,
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(
                [
                    "--project-root",
                    str(project),
                    "--translations",
                    str(project / "resources" / "work" / "approved-translations"),
                    "--profile",
                    str(project / "localization" / "project-profile.json"),
                ]
            )

        self.assertEqual(exit_code, 1)
        output = stdout.getvalue()
        self.assertIn("missing approved translation file: ending.csv", output)
        self.assertIn("changed original for quit", output)
        self.assertIn("empty translation for quit", output)
        self.assertIn("missing plugin dll", output)

    def test_main_dist_package_contains_only_allowlisted_files(self):
        project = Path(self._tmp_dir()) / "project"
        self._write_fixture_project(
            project,
            approved_counts={"character_name": 1},
            approved_rows={"character_name": [["hero", "Hero", "英雄"]]},
            entries=[{"category": "character_name", "key": "hero", "original": "Hero"}],
            include_plugin=True,
        )
        stale_root = project / "dist" / "BepInEx" / "plugins" / "PsychologHan"
        stale_root.mkdir(parents=True)
        (stale_root / "old.txt").write_text("stale", encoding="utf-8")
        (project / "resources" / "work" / "approved-translations" / "notes.txt").write_text(
            "ignore me",
            encoding="utf-8",
        )

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
        package_root = project / "dist" / "BepInEx" / "plugins" / "PsychologHan"
        packaged_files = sorted(
            path.relative_to(package_root).as_posix()
            for path in package_root.rglob("*")
            if path.is_file()
        )
        self.assertEqual(
            packaged_files,
            [
                "PsychologHan.dll",
                "localization/character_name.csv",
                "package-manifest.json",
            ],
        )

    def test_cli_script_execution_works_from_repo_root(self):
        project = Path(self._tmp_dir()) / "project"
        self._write_fixture_project(
            project,
            approved_counts={"character_name": 1},
            approved_rows={"character_name": [["hero", "Hero", "英雄"]]},
            entries=[{"category": "character_name", "key": "hero", "original": "Hero"}],
            include_plugin=True,
        )

        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_localization.py",
                "--project-root",
                str(project),
                "--translations",
                str(project / "resources" / "work" / "approved-translations"),
                "--profile",
                str(project / "localization" / "project-profile.json"),
            ],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("validation ok", result.stdout)

    def _write_fixture_project(
        self,
        project: Path,
        *,
        approved_counts: dict[str, int],
        approved_rows: dict[str, list[list[str]]],
        entries: list[dict[str, str]],
        include_plugin: bool,
    ) -> None:
        profile = {
            "schema_version": 1,
            "paratranz": {
                "approved_categories": [
                    "dialogue",
                    "choice",
                    "character_name",
                    "item",
                    "client_info",
                    "ending",
                    "ui",
                ]
            },
        }
        scope = {
            "schema_version": 1,
            "locale": "zh-CN",
            "approved_categories": list(approved_counts.keys()),
            "fallback_categories": ["dialogue", "choice"],
        }
        version = {
            "schema_version": 1,
            "locale": "zh-CN",
            "source_manifest": {"path": "resources/work/source-manifest.sha256", "sha256": "abc123"},
            "approved_row_counts": approved_counts,
        }
        self._write_json(project / "localization" / "project-profile.json", profile)
        self._write_json(project / "localization" / "translation-scope.json", scope)
        self._write_json(project / "resources" / "work" / "translation-version.json", version)
        (project / "resources" / "work" / "source-manifest.sha256").parent.mkdir(parents=True, exist_ok=True)
        (project / "resources" / "work" / "source-manifest.sha256").write_text(
            "deadbeef *resources/extracted/ui.csv\n",
            encoding="utf-8",
        )
        self._write_entries(project / "resources" / "work" / "entries.jsonl", entries)
        for category, rows in approved_rows.items():
            self._write_csv(project / "resources" / "work" / "approved-translations" / f"{category}.csv", rows)
        if include_plugin:
            plugin_path = project / "bin" / "Release" / "netstandard2.1" / "PsychologHan.dll"
            plugin_path.parent.mkdir(parents=True, exist_ok=True)
            plugin_path.write_bytes(b"test-plugin")

    def _write_csv(self, path: Path, rows: list[list[str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)

    def _write_entries(self, path: Path, entries: list[dict[str, str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            for row_number, entry in enumerate(entries, start=1):
                payload = {
                    "category": entry["category"],
                    "key": entry["key"],
                    "original": entry["original"],
                    "source_csv": f"{entry['category']}.csv",
                    "row_number": row_number,
                    "source_hash": "f" * 64,
                }
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _write_json(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _tmp_dir(self) -> str:
        path = tempfile.mkdtemp(prefix="psycholog-validate-localization-")
        self.addCleanup(lambda: __import__("shutil").rmtree(path, ignore_errors=True))
        return path


if __name__ == "__main__":
    unittest.main()
