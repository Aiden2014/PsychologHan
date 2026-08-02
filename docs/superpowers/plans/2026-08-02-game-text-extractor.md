# Psycholog 游戏流程与文本提取器 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a repeatable Python extractor that turns Psycholog decompiled code and Unity dump resources into translation CSVs plus flow and asset reference CSVs.

**Architecture:** Keep one importable module at `scripts/extract_game_text.py` with small pure parsing helpers and a CLI entry point. Build a cross-resource index keyed by source file and PathID, parse `GameManager.cs` with a balanced-call scanner, and write translation rows separately from non-translatable flow metadata.

**Tech Stack:** Python 3.9+, standard library (`argparse`, `csv`, `json`, `pathlib`, `re`, `dataclasses`), pytest for tests.

## Global Constraints

- Every generated CSV has exactly three columns: unique key, original/reference content, empty translation column.
- Generate the separate `item.csv` category for runtime `sitItems` text.
- Translation keys use compact positional `|||` fields, omit redundant category/source prefixes, and remain below 512 characters; `asset_index.csv` keeps full resource identity.
- Missing optional `TextAsset`/`ScriptableObject` inputs must not fail the run.
- Do not modify decompiled resources or generated translation files during tests.
- Preserve unresolved Unity references in a report.

---

### Task 1: Establish parser test fixtures and the failing C# scanner test

**Files:**
- Create: `tests/test_extract_game_text.py`
- Create: `scripts/extract_game_text.py`

**Interfaces:**
- The test imports `scan_invocations`, `split_top_level_args`, and `decode_csharp_string` from `scripts.extract_game_text`.
- The first implementation may be absent; the test must fail for the expected missing-function reason before production behavior is added.

- [x] **Step 1: Write the failing test**

Add this test before implementing the scanner:

```python
from scripts.extract_game_text import decode_csharp_string, scan_invocations, split_top_level_args


def test_scanner_handles_multiline_delegate_and_commas_inside_string():
    source = '''
    boss(15455, "Oh, hello, Doc.", 15456, delegate
    {
        playSoundEffect(bathroomVera, 0.6f);
    });
    '''
    calls = scan_invocations(source, {"boss", "playSoundEffect"})
    boss = next(call for call in calls if call.name == "boss")
    args = split_top_level_args(boss.arguments)

    assert [decode_csharp_string(args[i]) for i in (0, 1, 2)] == ["15455", "Oh, hello, Doc.", "15456"]
    assert "playSoundEffect" in boss.arguments


def test_decode_csharp_verbatim_and_escaped_strings():
    assert decode_csharp_string('@"line 1\\nline 2"') == "line 1\\nline 2"
    assert decode_csharp_string('"He said \\\"Doc\\\"."') == 'He said "Doc".'
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_extract_game_text.py::test_scanner_handles_multiline_delegate_and_commas_inside_string -q`

Expected: FAIL because `scripts.extract_game_text` and its scanner functions do not yet exist.

- [x] **Step 3: Write minimal scanner implementation**

Implement:

```python
@dataclass(frozen=True)
class Invocation:
    name: str
    arguments: str
    start: int
    end: int
    line: int


def split_top_level_args(text: str) -> list[str]: ...
def scan_invocations(source: str, names: set[str]) -> list[Invocation]: ...
def decode_csharp_string(token: str) -> str: ...
```

The scanner must skip `//`, `/* */`, normal strings, verbatim strings, and character literals while tracking `()[]{}` nesting. An invocation ends at the matching `)` after its opening `(`.

- [x] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_extract_game_text.py::test_scanner_handles_multiline_delegate_and_commas_inside_string -q`

Expected: PASS.

### Task 2: Parse GameManager dialogue, choices, and flow events

**Files:**
- Modify: `scripts/extract_game_text.py`
- Modify: `tests/test_extract_game_text.py`

**Interfaces:**
- `parse_game_manager(path: Path) -> GameData` returns `dialogues`, `choices`, and `flow_events` lists.
- Each dialogue row carries `node_id`, `speaker`, `text`, `to_id`, `source_line`.
- Each choice row carries `from_id`, `option_id`, `text`, `to_id`, `source_line`.
- Each flow event carries `node_id`, `event_type`, `details`, `source_line`, and `parent_call` when nested in a callback.

- [x] **Step 1: Write the failing test**

Append:

```python
def test_parse_game_manager_extracts_dialogue_choices_and_context(tmp_path):
    source = tmp_path / "GameManager.cs"
    source.write_text('''
    public void boss(int id, string text, int toId, Action customFuncIn = null) { }
    void Build() {
        illustrate(15455, "office");
        boss(15455, "Oh. Hello.", 15456, delegate { playSoundEffect(bathroomVera, 0.6f); });
        addOpt(15456, 1545601L, "Hello, Doc.", 15460);
        addCutscene(15460, "plasticSurgery1", 15461);
        addMusic(15461, "veraSessions", 0.3f);
    }
    ''', encoding="utf-8")

    data = parse_game_manager(source)

    assert [(row.node_id, row.speaker, row.text, row.to_id) for row in data.dialogues] == [(15455, "BOSS", "Oh. Hello.", 15456)]
    assert [(row.from_id, row.option_id, row.text, row.to_id) for row in data.choices] == [(15456, 1545601, "Hello, Doc.", 15460)]
    assert {event.event_type for event in data.flow_events} >= {"image", "sound", "cutscene", "music"}
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_extract_game_text.py::test_parse_game_manager_extracts_dialogue_choices_and_context -q`

Expected: FAIL because `parse_game_manager` and `GameData` are not implemented.

- [x] **Step 3: Implement the minimal GameManager parser**

Use the existing wrapper definitions in `GameManager.cs`: direct `boss`, `vera`, `joe`, `jaden`, `deborah`, `ashley`, `josh`, `shannon`, `jackson`, `tanaka`, `mike`, `passenger`, `raymond`, `green`, `killerWithGlasses`, `killerRevealed`, `killerRaymond`, and `bennett` calls use `(id, text, toId, callback)`. `addMe` uses `(id, text, toId, callback)`, and `addSpeaker` uses `(id, speaker, text, toId, callback)`.

Parse option wrappers with `(fromId, optionId, text, toId)` and collect `addOpt` directly. Parse `illustrate`, `animate`, `addCutscene`, `addMusic`, `addAmbience`, `playSoundEffect`, `addChoice`, `addMap`, `addPac`, and `applyTransition` into flow events. For nested calls, attach the containing invocation's node ID and set `trigger=callback`.

- [x] **Step 4: Run focused tests**

Run: `python -m pytest tests/test_extract_game_text.py::test_parse_game_manager_extracts_dialogue_choices_and_context -q`

Expected: PASS.

### Task 3: Build Unity JSON/resource reference index

**Files:**
- Modify: `scripts/extract_game_text.py`
- Modify: `tests/test_extract_game_text.py`

**Interfaces:**
- `ResourceIndex.from_root(resources_root: Path) -> ResourceIndex`.
- `ResourceIndex.resolve(ref: UnityRef, owner: ResourceObject, expected_types: set[str] | None = None) -> ResourceObject | None`.
- `ResourceObject` exposes `source`, `path_id`, `type_name`, `name`, `path`, and raw `data`.

- [x] **Step 1: Write the failing test**

Append:

```python
def test_resource_index_resolves_audio_source_to_audio_clip(tmp_path):
    root = tmp_path / "resources"
    (root / "AudioSource").mkdir(parents=True)
    (root / "AudioClip").mkdir()
    (root / "GameObject").mkdir()
    (root / "AudioSource" / "AudioSource-level1-8.json").write_text(
        '{"m_GameObject":{"m_FileID":0,"m_PathID":3},"m_audioClip":{"m_FileID":2,"m_PathID":156}}', encoding="utf-8"
    )
    (root / "AudioClip" / "bathroomVera-sharedassets1.assets-156.ogg").write_bytes(b"ogg")
    (root / "GameObject" / "speaker-level1-3.json").write_text('{"m_Name":"speaker"}', encoding="utf-8")

    index = ResourceIndex.from_root(root)
    audio_source = index.find_by_path_id("level1", 8)
    clip = index.resolve(audio_source.data["m_audioClip"], audio_source, {"AudioClip"})

    assert clip is not None
    assert clip.name == "bathroomVera"
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_extract_game_text.py::test_resource_index_resolves_audio_source_to_audio_clip -q`

Expected: FAIL because resource indexing and reference resolution are not implemented.

- [x] **Step 3: Implement indexing and resolution**

Index JSON objects by the source marker and final numeric suffix in the filename. Also index binary exported assets such as `.ogg` and `.png` by normalized basename and PathID suffix. Treat absent `TextAsset`/`ScriptableObject` directories as empty. Resolve local `m_FileID=0` references in the owner source, then external references by expected type and unique PathID; return `None` for ambiguous candidates and record the ambiguity for the report.

- [x] **Step 4: Run focused tests**

Run: `python -m pytest tests/test_extract_game_text.py::test_resource_index_resolves_audio_source_to_audio_clip -q`

Expected: PASS.

### Task 4: Extract JSON UI text and generate all CSV outputs

**Files:**
- Modify: `scripts/extract_game_text.py`
- Modify: `tests/test_extract_game_text.py`

**Interfaces:**
- `extract_ui_rows(index: ResourceIndex) -> list[CsvRow]`.
- `write_rows(path: Path, rows: Iterable[CsvRow]) -> None`.
- `run_extraction(project_root: Path, output_dir: Path) -> ExtractionStats`.

- [x] **Step 1: Write the failing test**

Append:

```python
def test_ui_and_flow_csv_rows_have_three_columns(tmp_path):
    resources = tmp_path / "resources"
    (resources / "MonoBehaviour").mkdir(parents=True)
    (resources / "MonoBehaviour" / "TextMeshProUGUI-level1-31389.json").write_text(
        '{"m_Name":"BackButton","m_text":"Back to main menu"}', encoding="utf-8"
    )
    output = tmp_path / "out"
    stats = run_extraction(tmp_path, output)

    rows = list(csv.reader((output / "ui.csv").open(encoding="utf-8-sig")))
    assert rows == [["ui|||level1|||31389|||TextMeshProUGUI|||BackButton", "Back to main menu", ""]]
    assert all(len(row) == 3 for file in output.glob("*.csv") for row in csv.reader(file.open(encoding="utf-8-sig")))
    assert stats.ui_count == 1
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_extract_game_text.py::test_ui_and_flow_csv_rows_have_three_columns -q`

Expected: FAIL because CSV writing and `run_extraction` are not implemented.

- [x] **Step 3: Implement output generation**

Write UTF-8 BOM, no header, exactly three columns. Generate `dialogue.csv`, `choice.csv`, `item.csv`, `character_name.csv`, `client_info.csv`, `ending.csv`, `ui.csv`, `flow_context.csv`, `asset_index.csv`, and `unresolved_refs.csv`. Deduplicate only identical `(key, original)` pairs; keep export-file identity in asset keys. Extract `m_text` and `m_Text` from TextMeshProUGUI/Text-like objects and C# `.text = "..."` assignments. Resolve scene assets from Sprite `m_Name` and exported PNGs; resolve audio references from `GameManager` AudioSource fields through AudioClip exports.

Extract `GameManager` speaker wrapper names, `GameState` trust/treatment/rune strings, `GameManager.updateProgressionMetricComments()` assignments, `DeathRunes.cs` branch strings, and `died`/`failed`/`fight` system strings into their dedicated CSV categories. For concatenated assignments, preserve literal segments and replace non-literal segments with `{EXPR_1}` while writing the original expression into the flow/reference detail.

- [x] **Step 4: Run focused test**

Run: `python -m pytest tests/test_extract_game_text.py::test_ui_and_flow_csv_rows_have_three_columns -q`

Expected: PASS.

### Task 5: Add CLI and run verification on the real dump

**Files:**
- Modify: `scripts/extract_game_text.py`
- Modify: `tests/test_extract_game_text.py`

**Interfaces:**
- CLI command: `python scripts/extract_game_text.py [--project-root PATH] [--output-dir PATH]`.
- Default project root is the parent of `scripts/`; default output is `<project-root>/resources/extracted`.

- [x] **Step 1: Write the failing CLI test**

Append:

```python
def test_cli_accepts_explicit_project_root_and_output(tmp_path):
    project = tmp_path / "project"
    (project / "resources").mkdir(parents=True)
    output = tmp_path / "result"
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parents[1] / "scripts" / "extract_game_text.py"),
         "--project-root", str(project), "--output-dir", str(output)],
        check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert (output / "dialogue.csv").exists()
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_extract_game_text.py::test_cli_accepts_explicit_project_root_and_output -q`

Expected: FAIL because the CLI entry point is not implemented.

- [x] **Step 3: Implement CLI and diagnostics**

Add argparse options, create output directories, print counts by category, and return exit code 0 for absent optional directories and exit code 2 only when the project root or required C# directory is missing.

- [x] **Step 4: Run the complete test suite**

Run: `python -m pytest -q`

Expected: all tests PASS.

- [x] **Step 5: Run the extractor on the real project dump**

Run: `python scripts/extract_game_text.py`

Verify that the output directory contains all ten CSVs, every row has three columns and unique keys, dialogue, choice, item, character-name and client-info counts are nonzero, and unresolved references are listed rather than silently omitted.

- [x] **Step 6: Review generated samples**

Run: `Get-Content resources\extracted\dialogue.csv -TotalCount 10` and `Get-Content resources\extracted\flow_context.csv -TotalCount 20`.

Verify that keys remain stable metadata keys and that scene/audio paths appear only in reference outputs.

### Task 7: Record story modules and dialogue graph edges in flow context

**Files:**
- Modify: `scripts/extract_game_text.py`
- Modify: `tests/test_extract_game_text.py`
- Modify: `docs/superpowers/specs/2026-08-02-game-text-extractor-design.md`

**Requirements:**
- Detect `story*` method ranges in `GameManager.cs`.
- Write `story_module` rows for each story method.
- Write `dialogue_edge` rows with module, speaker, node and target node.
- Write `choice_edge` rows with module, option ID and target node.
- Keep the output as the existing three-column CSV format.

- [x] **Step 1: Write the failing regression test**
- [x] **Step 2: Run the focused test and verify the old behavior fails**
- [x] **Step 3: Implement story method range scanning and graph-context rows**
- [x] **Step 4: Run the complete test suite and real extraction**

### Task 6: Compact translation keys and filter non-text UI placeholders

**Files:**
- Modify: `scripts/extract_game_text.py`
- Modify: `tests/test_extract_game_text.py`
- Modify: `docs/superpowers/specs/2026-08-02-game-text-extractor-design.md`

**Requirements:**
- Translation CSV keys omit the redundant category/source prefix. `asset_index.csv` keeps its full resource identity key.
- Keys use short positional `|||`-separated fields and fail loudly rather than silently truncate above 512 characters.
- `nothing` audio references are treated as an intentional no-audio sentinel.
- `backgroundImage` method-default references are not unresolved flow assets.
- Pure underscore UI strings are omitted from `ui.csv`.

- [x] **Step 1: Write failing regression tests**

Add assertions that the UI key is `level1|||31389|||TextMeshProUGUI|||BackButton`, that pure underscore JSON text is omitted, that non-asset keys do not start with a category/source prefix and are at most 512 characters, and that `nothing`/`backgroundImage` do not enter unresolved references.

- [x] **Step 2: Run the focused tests and verify the old behavior fails**

Run: `python -m unittest -v tests.test_extract_game_text`

Expected: the old verbose UI key and unresolved special-value behavior fail the new assertions.

- [x] **Step 3: Implement compact keys, sentinel filtering, audio aliases, and UI placeholder filtering**

Use one key builder for translation rows, retain the complete asset key separately, filter only values whose stripped text consists entirely of `_`, skip unresolved reporting for the two known non-missing sentinels, and raise `ValueError` for any generated key over 512 characters.

- [x] **Step 4: Run the complete test suite**

Run: `python -m unittest -v tests.test_extract_game_text`

Expected: all tests pass.

- [x] **Step 5: Regenerate and audit the real CSVs**

Run: `python scripts/extract_game_text.py`, then verify every CSV has three columns, translation keys are unique, non-asset keys are below 512 characters, UI contains no pure underscore rows, and unresolved references contain only genuinely unknown references.
