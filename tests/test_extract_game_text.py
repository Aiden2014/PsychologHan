import csv
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.extract_game_text import (
    FlowEvent,
    ResourceIndex,
    decode_csharp_string,
    parse_game_manager,
    run_extraction,
    _enrich_flow_events,
    _parse_audio_aliases,
    scan_invocations,
    split_top_level_args,
)


class ExtractGameTextTests(unittest.TestCase):
    def test_scanner_handles_multiline_delegate_and_commas_inside_string(self):
        source = '''
        boss(15455, "Oh, hello, Doc.", 15456, delegate
        {
            playSoundEffect(bathroomVera, 0.6f);
        });
        '''
        calls = scan_invocations(source, {"boss", "playSoundEffect"})
        boss = next(call for call in calls if call.name == "boss")
        args = split_top_level_args(boss.arguments)

        self.assertEqual(
            [decode_csharp_string(args[i]) for i in (0, 1, 2)],
            ["15455", "Oh, hello, Doc.", "15456"],
        )
        self.assertIn("playSoundEffect", boss.arguments)

    def test_decode_csharp_verbatim_and_escaped_strings(self):
        self.assertEqual(decode_csharp_string('@"line 1\\nline 2"'), "line 1\\nline 2")
        self.assertEqual(
            decode_csharp_string('"He said \\\"Doc\\\"."'),
            'He said "Doc".',
        )

    def test_parse_game_manager_extracts_dialogue_choices_context_and_names(self):
        source = Path(self._tmp_dir()) / "GameManager.cs"
        source.write_text(
            '''
        public void boss(int id, string text, int toId, Action customFuncIn = null) { }
        public void vera(int id, string text, int toId, Action customFuncIn = null)
        { addSpeaker(id, "VERA", text, toId, customFuncIn, "vera"); }
        void Build() {
            illustrate(15455, "office");
            boss(15455, "Oh. Hello.", 15456, delegate { playSoundEffect(bathroomVera, 0.6f); });
            vera(15456, "I am here.", 15457);
            addOpt(15457, 1545701L, "Hello, Doc.", 15460);
            addCutscene(15460, "plasticSurgery1", 15461);
            addMusic(15461, "veraSessions", 0.3f);
            sitItems[10].text = "Floor " + gS.homeworkFloor;
        }
        ''',
            encoding="utf-8",
        )

        data = parse_game_manager(source)

        self.assertEqual(
            [(row.node_id, row.speaker, row.text, row.to_id) for row in data.dialogues],
            [
                (15455, "BOSS", "Oh. Hello.", 15456),
                (15456, "VERA", "I am here.", 15457),
            ],
        )
        self.assertEqual(
            [(row.key_suffix, row.text) for row in data.items],
            [("10|||12", "Floor {EXPR_1}")],
        )
        self.assertEqual(
            [(row.from_id, row.option_id, row.text, row.to_id) for row in data.choices],
            [(15457, 1545701, "Hello, Doc.", 15460)],
        )
        self.assertTrue(
            {event.event_type for event in data.flow_events}
            >= {"image", "sound", "cutscene", "music", "dynamic_text"}
        )
        self.assertEqual(data.character_names, {"BOSS", "VERA"})

    def test_flow_context_records_story_module_dialogue_order_and_choices(self):
        source = Path(self._tmp_dir()) / "GameManager.cs"
        source.write_text(
            '''
        public void vera(int id, string text, int toId, Action customFuncIn = null)
        { addSpeaker(id, "VERA", text, toId, customFuncIn, "vera"); }
        private void storyIntro() {
            vera(1, "Hello", 2);
            addChoice(2);
            addOpt(2, 2001L, "Continue", 3);
        }
        ''',
            encoding="utf-8",
        )

        data = parse_game_manager(source)
        context = [(event.event_type, event.details) for event in data.flow_events]

        self.assertTrue(any(kind == "story_module" and "storyIntro" in details for kind, details in context))
        self.assertTrue(any(kind == "dialogue_edge" and "storyIntro" in details and "to=2" in details for kind, details in context))
        self.assertTrue(any(kind == "choice_edge" and "storyIntro" in details and "to=3" in details for kind, details in context))

    def test_parse_game_state_and_death_runes(self):
        data = parse_game_manager(
            Path("resources/Assembly-CSharp-decompiled/GameManager.cs")
        )
        self.assertTrue(any("Vera" in row.text for row in data.client_info))
        self.assertTrue(any("Vera Mills" in row.text for row in data.ending))

    def test_resource_index_resolves_audio_source_to_audio_clip(self):
        root = Path(self._tmp_dir()) / "resources"
        (root / "AudioSource").mkdir(parents=True)
        (root / "AudioClip").mkdir()
        (root / "GameObject").mkdir()
        (root / "AudioSource" / "AudioSource-level1-8.json").write_text(
            '{"m_GameObject":{"m_FileID":0,"m_PathID":3},'
            '"m_audioClip":{"m_FileID":2,"m_PathID":156}}',
            encoding="utf-8",
        )
        (root / "AudioClip" / "bathroomVera-sharedassets1.assets-156.ogg").write_bytes(
            b"ogg"
        )
        (root / "GameObject" / "speaker-level1-3.json").write_text(
            '{"m_Name":"speaker"}', encoding="utf-8"
        )

        index = ResourceIndex.from_root(root)
        audio_source = index.find_by_path_id("level1", 8)
        clip = index.resolve(
            audio_source.data["m_audioClip"], audio_source, {"AudioClip"}
        )

        self.assertIsNotNone(clip)
        self.assertEqual(clip.name, "bathroomVera")

    def test_flow_audio_field_resolves_audio_source_to_audio_clip(self):
        root = Path(self._tmp_dir()) / "resources"
        (root / "MonoBehaviour").mkdir(parents=True)
        (root / "AudioSource").mkdir()
        (root / "AudioClip").mkdir()
        (root / "MonoBehaviour" / "GameManager-level1-1.json").write_text(
            '{"veraSessions":{"m_FileID":0,"m_PathID":2}}', encoding="utf-8"
        )
        (root / "AudioSource" / "AudioSource-level1-2.json").write_text(
            '{"m_audioClip":{"m_FileID":0,"m_PathID":3}}', encoding="utf-8"
        )
        (root / "AudioClip" / "veraSessions-sharedassets1.assets-3.ogg").write_bytes(b"ogg")

        index = ResourceIndex.from_root(root)
        data = type("Data", (), {"flow_events": [
            FlowEvent(10, "music", "name=veraSessions; volume=1", 1),
        ]})()
        _enrich_flow_events(data, index)

        self.assertIn("veraSessions-sharedassets1.assets-3.ogg", data.flow_events[0].details)

    def test_flow_image_includes_exported_png_when_available(self):
        root = Path(self._tmp_dir()) / "resources"
        (root / "Sprite").mkdir(parents=True)
        (root / "Sprite" / "office-resources.assets-9.json").write_text(
            '{"m_Name":"office"}', encoding="utf-8"
        )
        (root / "Sprite" / "office-resources.assets-9.png").write_bytes(b"png")

        index = ResourceIndex.from_root(root)
        data = type("Data", (), {"flow_events": [
            FlowEvent(10, "image", "image=office", 1),
        ]})()
        _enrich_flow_events(data, index)

        self.assertIn("office-resources.assets-9.png", data.flow_events[0].details)

    def test_unresolved_flow_asset_is_reported(self):
        root = Path(self._tmp_dir()) / "resources"
        root.mkdir(parents=True)
        index = ResourceIndex.from_root(root)
        data = type("Data", (), {"flow_events": [
            FlowEvent(10, "image", "image=missingBackground", 1),
        ]})()

        _enrich_flow_events(data, index)

        self.assertTrue(index.unresolved)

    def test_known_flow_sentinels_are_not_unresolved(self):
        root = Path(self._tmp_dir()) / "resources"
        root.mkdir(parents=True)
        index = ResourceIndex.from_root(root)
        data = type("Data", (), {"flow_events": [
            FlowEvent(None, "image", "image=backgroundImage", 1),
            FlowEvent(10, "music", "name=nothing; volume=1", 2),
        ]})()

        _enrich_flow_events(data, index)

        self.assertEqual(index.unresolved, [])

    def test_str_to_audio_aliases_resolve_to_game_manager_fields(self):
        source = Path(self._tmp_dir()) / "GameManager.cs"
        source.write_text(
            'switch (str) { case "carpenterRoad": return street2Ambience; '
            'case "subway": return subwayAmbience; }',
            encoding="utf-8",
        )

        self.assertEqual(
            _parse_audio_aliases(source),
            {"carpenterRoad": "street2Ambience", "subway": "subwayAmbience"},
        )

    def test_flow_audio_alias_resolves_through_game_manager_field(self):
        root = Path(self._tmp_dir()) / "resources"
        (root / "MonoBehaviour").mkdir(parents=True)
        (root / "AudioSource").mkdir()
        (root / "AudioClip").mkdir()
        (root / "MonoBehaviour" / "GameManager-level1-1.json").write_text(
            '{"street2Ambience":{"m_FileID":0,"m_PathID":2}}', encoding="utf-8"
        )
        (root / "AudioSource" / "AudioSource-level1-2.json").write_text(
            '{"m_audioClip":{"m_FileID":0,"m_PathID":3}}', encoding="utf-8"
        )
        (root / "AudioClip" / "carpenterRoad-sharedassets1.assets-3.ogg").write_bytes(b"ogg")

        index = ResourceIndex.from_root(root)
        data = type("Data", (), {"flow_events": [
            FlowEvent(10, "ambience", "name=carpenterRoad; volume=1", 1),
        ]})()
        _enrich_flow_events(data, index, {"carpenterRoad": "street2Ambience"})

        self.assertIn("carpenterRoad-sharedassets1.assets-3.ogg", data.flow_events[0].details)

    def test_asset_index_keys_include_export_file_identity(self):
        root = Path(self._tmp_dir()) / "resources"
        (root / "Sprite").mkdir(parents=True)
        (root / "Sprite" / "office-resources.assets-9.json").write_text(
            '{"m_Name":"office"}', encoding="utf-8"
        )
        (root / "Sprite" / "office-resources.assets-9.png").write_bytes(b"png")
        project = root.parent
        (project / "resources" / "Assembly-CSharp-decompiled").mkdir(parents=True)

        stats = run_extraction(project, project / "out")
        with (project / "out" / "asset_index.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(len(rows), len({row[0] for row in rows}))
        self.assertEqual(stats.asset_count, 2)

    def test_ui_and_category_csv_rows_have_three_columns(self):
        project = Path(self._tmp_dir())
        resources = project / "resources"
        (resources / "MonoBehaviour").mkdir(parents=True)
        (resources / "MonoBehaviour" / "TextMeshProUGUI-level1-31389.json").write_text(
            '{"m_Name":"BackButton","m_text":"Back to main menu"}', encoding="utf-8"
        )
        (resources / "MonoBehaviour" / "TextMeshProUGUI-level1-31390.json").write_text(
            '{"m_Name":"InputPlaceholder","m_text":"____________________"}', encoding="utf-8"
        )
        (resources / "Assembly-CSharp-decompiled").mkdir()
        (resources / "Assembly-CSharp-decompiled" / "GameManager.cs").write_text(
            'public void vera(int id, string text, int toId, Action x = null) { '
            'addSpeaker(id, "VERA", text, toId, x, "vera"); }\n'
            'public void build() { vera(1, "Hello", 2); }',
            encoding="utf-8",
        )
        output = project / "out"
        stats = run_extraction(project, output)

        with (output / "ui.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(
            rows,
            [[
                "level1|||31389|||TextMeshProUGUI|||BackButton",
                "Back to main menu",
                "",
            ]],
        )
        self.assertTrue((output / "item.csv").exists())
        for file in output.glob("*.csv"):
            with file.open(encoding="utf-8-sig", newline="") as handle:
                file_rows = list(csv.reader(handle))
            self.assertTrue(all(len(row) == 3 for row in file_rows))
            self.assertTrue(len({row[0] for row in file_rows}) == len(file_rows))
            self.assertTrue(all(len(row[0]) <= 512 for row in file_rows))
            if file.name != "asset_index.csv":
                self.assertTrue(all(not row[0].startswith(file.stem + "|||") for row in file_rows))
                self.assertTrue(all("=" not in row[0] for row in file_rows))
        self.assertEqual(stats.ui_count, 1)
        self.assertEqual(stats.character_name_count, 1)

    def test_cli_accepts_explicit_project_root_and_output(self):
        project = Path(self._tmp_dir()) / "project"
        (project / "resources" / "Assembly-CSharp-decompiled").mkdir(parents=True)
        (project / "resources" / "Assembly-CSharp-decompiled" / "GameManager.cs").write_text(
            "public void build() {}", encoding="utf-8"
        )
        output = Path(self._tmp_dir()) / "result"
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parents[1] / "scripts" / "extract_game_text.py"),
                "--project-root",
                str(project),
                "--output-dir",
                str(output),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((output / "dialogue.csv").exists())

    def _tmp_dir(self):
        import tempfile

        path = tempfile.mkdtemp(prefix="psycholog-extract-")
        self.addCleanup(lambda: __import__("shutil").rmtree(path, ignore_errors=True))
        return path


if __name__ == "__main__":
    unittest.main()
