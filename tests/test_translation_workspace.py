import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.translation_workspace import (
    export_entries,
    protected_tokens,
    validate_import,
)


class TranslationWorkspaceTests(unittest.TestCase):
    def test_export_entries_writes_filtered_jsonl_and_review_csvs(self):
        project = Path(self._tmp_dir()) / "project"
        extracted = project / "resources" / "extracted"
        extracted.mkdir(parents=True)
        self._write_csv(
            extracted / "dialogue.csv",
            [
                ["dlg-1", "Hello {EXPR_1}\n\nWorld", ""],
                ["dlg-2", "Second line", ""],
            ],
        )
        self._write_csv(
            extracted / "ui.csv",
            [["ui-1", "Use <color=#fff>{0}</color>\\nNow", ""]],
        )
        self._write_csv(extracted / "flow_context.csv", [["flow-1", "ignore", ""]])
        self._write_csv(extracted / "asset_index.csv", [["asset-1", "ignore", ""]])
        self._write_csv(extracted / "unresolved_refs.csv", [["ref-1", "ignore", ""]])

        output = project / "resources" / "work"
        counts = export_entries(project, output)

        self.assertEqual(counts, {"dialogue": 2, "ui": 1})
        entries = self._read_jsonl(output / "entries.jsonl")
        self.assertEqual(
            [(entry["category"], entry["key"], entry["original"]) for entry in entries],
            [
                ("dialogue", "dlg-1", "Hello {EXPR_1}\n\nWorld"),
                ("dialogue", "dlg-2", "Second line"),
                ("ui", "ui-1", "Use <color=#fff>{0}</color>\\nNow"),
            ],
        )
        self.assertEqual(
            [(entry["source_csv"], entry["row_number"]) for entry in entries],
            [("dialogue.csv", 1), ("dialogue.csv", 2), ("ui.csv", 1)],
        )
        self.assertTrue(all(len(entry["source_hash"]) == 64 for entry in entries))
        self.assertTrue((output / "dialogue.csv").exists())
        self.assertTrue((output / "ui.csv").exists())
        self.assertFalse((output / "flow_context.csv").exists())

        manifest_text = (output / "source-manifest.sha256").read_text(encoding="utf-8")
        self.assertIn("dialogue.csv", manifest_text)
        self.assertIn("ui.csv", manifest_text)

    def test_export_entries_writes_review_csvs_with_utf8_bom(self):
        project = Path(self._tmp_dir()) / "project"
        extracted = project / "resources" / "extracted"
        extracted.mkdir(parents=True)
        self._write_csv(
            extracted / "dialogue.csv",
            [["dlg-1", "Hello", ""]],
        )

        output = project / "resources" / "work"
        export_entries(project, output)

        self.assertEqual((output / "dialogue.csv").read_bytes()[:3], b"\xef\xbb\xbf")

    def test_export_entries_is_deterministic_across_repeated_runs(self):
        project = Path(self._tmp_dir()) / "project"
        extracted = project / "resources" / "extracted"
        extracted.mkdir(parents=True)
        self._write_csv(
            extracted / "dialogue.csv",
            [["dlg-1", "Hello", ""], ["dlg-2", "World", ""]],
        )
        self._write_csv(
            extracted / "ui.csv",
            [["ui-1", "Quit", ""]],
        )

        output = project / "resources" / "work"
        export_entries(project, output)
        first_entries = (output / "entries.jsonl").read_text(encoding="utf-8")
        first_manifest = (output / "source-manifest.sha256").read_text(encoding="utf-8")

        export_entries(project, output)
        second_entries = (output / "entries.jsonl").read_text(encoding="utf-8")
        second_manifest = (output / "source-manifest.sha256").read_text(encoding="utf-8")

        self.assertEqual(second_entries, first_entries)
        self.assertEqual(second_manifest, first_manifest)

    def test_protected_tokens_covers_placeholders_tags_escapes_and_newlines(self):
        tokens = protected_tokens(
            "Use {EXPR_1} then {0} and {player_name} <color=#fff>go</color>\\nNext\nDone"
        )

        self.assertIn("{EXPR_1}", tokens)
        self.assertIn("{0}", tokens)
        self.assertIn("{player_name}", tokens)
        self.assertIn("<color=#fff>", tokens)
        self.assertIn("</color>", tokens)
        self.assertIn("\\n", tokens)
        self.assertIn("\n", tokens)

    def test_validate_import_reports_invalid_rows(self):
        workspace = Path(self._tmp_dir()) / "workspace"
        workspace.mkdir(parents=True)
        entries_path = workspace / "entries.jsonl"
        translations_dir = workspace / "approved-translations"
        translations_dir.mkdir()
        self._write_entries(
            entries_path,
            [
                {
                    "category": "dialogue",
                    "key": "dlg-1",
                    "original": "Hello {EXPR_1}",
                    "source_csv": "dialogue.csv",
                    "row_number": 1,
                },
                {
                    "category": "ui",
                    "key": "ui-1",
                    "original": "Quit <b>now</b>",
                    "source_csv": "ui.csv",
                    "row_number": 1,
                },
                {
                    "category": "item",
                    "key": "item-1",
                    "original": "Take notes",
                    "source_csv": "item.csv",
                    "row_number": 1,
                },
            ],
        )
        self._write_csv(
            translations_dir / "dialogue.csv",
            [
                ["dlg-1", "Hello {EXPR_1}", ""],
                ["dlg-1", "Hello {EXPR_1}", "你好 {EXPR_1}"],
                ["unknown", "Something else", "??"],
            ],
        )
        with (translations_dir / "dialogue.csv").open("a", encoding="utf-8", newline="") as handle:
            handle.write("bad,row-only\n")
        self._write_csv(
            translations_dir / "ui.csv",
            [["ui-1", "Quit <b>now</b>", "Quit now"]],
        )
        self._write_csv(
            translations_dir / "item.csv",
            [["item-1", "Take notes!", "记笔记"]],
        )

        errors = validate_import(entries_path, translations_dir)
        joined = "\n".join(errors)

        self.assertIn("duplicate key", joined)
        self.assertIn("unknown key", joined)
        self.assertIn("malformed row", joined)
        self.assertIn("empty translation", joined)
        self.assertIn("protected token", joined)
        self.assertIn("changed original", joined)

    def test_validate_import_reports_newline_count_changes(self):
        workspace = Path(self._tmp_dir()) / "workspace"
        workspace.mkdir(parents=True)
        entries_path = workspace / "entries.jsonl"
        translations_dir = workspace / "approved-translations"
        translations_dir.mkdir()
        self._write_entries(
            entries_path,
            [
                {
                    "category": "dialogue",
                    "key": "dlg-1",
                    "original": "Line 1\nLine 2",
                    "source_csv": "dialogue.csv",
                    "row_number": 1,
                }
            ],
        )
        self._write_csv(
            translations_dir / "dialogue.csv",
            [["dlg-1", "Line 1\nLine 2", "第一行 第二行"]],
        )

        errors = validate_import(entries_path, translations_dir)

        self.assertTrue(any("newline count" in error for error in errors))

    def test_validate_import_allows_missing_translation_files_and_rows(self):
        workspace = Path(self._tmp_dir()) / "workspace"
        workspace.mkdir(parents=True)
        entries_path = workspace / "entries.jsonl"
        translations_dir = workspace / "approved-translations"
        translations_dir.mkdir()
        self._write_entries(
            entries_path,
            [
                {
                    "category": "dialogue",
                    "key": "dlg-1",
                    "original": "Hello",
                    "source_csv": "dialogue.csv",
                    "row_number": 1,
                },
                {
                    "category": "choice",
                    "key": "choice-1",
                    "original": "Continue",
                    "source_csv": "choice.csv",
                    "row_number": 1,
                },
            ],
        )
        self._write_csv(
            translations_dir / "dialogue.csv",
            [["dlg-1", "Hello", "你好"]],
        )

        self.assertEqual(validate_import(entries_path, translations_dir), [])

    def _write_csv(self, path: Path, rows: list[list[str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)

    def _write_entries(self, path: Path, entries: list[dict[str, object]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            for entry in entries:
                row = dict(entry)
                row.setdefault("source_hash", "a" * 64)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, object]]:
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _tmp_dir(self) -> str:
        path = tempfile.mkdtemp(prefix="psycholog-translation-workspace-")
        self.addCleanup(lambda: __import__("shutil").rmtree(path, ignore_errors=True))
        return path


if __name__ == "__main__":
    unittest.main()
