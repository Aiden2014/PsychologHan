# Task 2 Report: Build and validate the translation work layer

## Status

Completed. Review fix round 1 applied.

Implemented a standard-library-only translation workspace adapter in `scripts/translation_workspace.py` and focused coverage in `tests/test_translation_workspace.py`, without modifying `scripts/extract_game_text.py`, the existing extraction CSVs, the Steam game directory, or unrelated user files.

## Changed files

- `scripts/translation_workspace.py`
- `tests/test_translation_workspace.py`
- `.superpowers/sdd/psychologhan-basic-localization/task-2-report.md`

## Generated ignored outputs

- `resources/work/entries.jsonl`
- `resources/work/source-manifest.sha256`
- `resources/work/*.csv` review exports for translation-bearing categories present in `resources/extracted/`
- `resources/work/approved-translations/` (empty scaffold)

## Behavior delivered

- Added `export_entries(project_root: Path, output_dir: Path) -> dict[str, int]`
- Added `validate_import(entries_path: Path, translations_dir: Path) -> list[str]`
- Added `translation_key(category: str, key: str) -> str`
- Added `protected_tokens(text: str) -> tuple[str, ...]`
- Added CLI:
  - `python scripts/translation_workspace.py export --project-root . --output-dir resources/work`
  - `python scripts/translation_workspace.py validate --entries resources/work/entries.jsonl --translations resources/work/approved-translations`

## Commands and output

### Red

Command:

```powershell
python -m unittest tests.test_translation_workspace -v
```

Output:

```text
ERROR: ModuleNotFoundError: No module named 'scripts.translation_workspace'
FAILED (errors=1)
```

### New test module after implementation

Command:

```powershell
python -m unittest tests.test_translation_workspace -v
```

Output:

```text
Ran 5 tests in 0.047s
OK
```

### Required verification: existing extractor tests + new tests

Command:

```powershell
python -m unittest tests.test_extract_game_text tests.test_translation_workspace -v
```

Output:

```text
Ran 20 tests in 1.471s
OK
```

### Real workspace export

Command:

```powershell
python scripts/translation_workspace.py export --project-root . --output-dir resources/work
```

Output:

```json
{"character_name": 24, "choice": 1334, "client_info": 10, "dialogue": 2479, "ending": 16, "item": 10, "ui": 1533}
```

Additional check:

```powershell
python -c "from pathlib import Path; print(sum(1 for _ in Path('resources/work/entries.jsonl').open(encoding='utf-8')))"
```

Output:

```text
5406
```

### Real workspace validation

Command:

```powershell
python scripts/translation_workspace.py validate --entries resources/work/entries.jsonl --translations resources/work/approved-translations
```

Output:

```text
validation ok
```

### Review fix round 1: red before BOM fix

Command:

```powershell
python -m unittest tests.test_translation_workspace -v
```

Output:

```text
FAIL: test_export_entries_writes_review_csvs_with_utf8_bom
AssertionError: b'dlg' != b'\xef\xbb\xbf'
FAILED (failures=1)
```

### Review fix round 1: focused verification

Command:

```powershell
python -m unittest tests.test_translation_workspace -v
```

Output:

```text
Ran 7 tests in 0.103s
OK
```

### Review fix round 1: full verification

Command:

```powershell
python -m unittest tests.test_extract_game_text tests.test_translation_workspace -v
```

Output:

```text
Ran 22 tests in 1.515s
OK
```

### Review fix round 1: export and validate

Commands:

```powershell
python scripts/translation_workspace.py export --project-root . --output-dir resources/work
python scripts/translation_workspace.py validate --entries resources/work/entries.jsonl --translations resources/work/approved-translations
```

Output:

```text
{"character_name": 24, "choice": 1334, "client_info": 10, "dialogue": 2479, "ending": 16, "item": 10, "ui": 1533}
validation ok
```

## Concerns

- Validation intentionally treats missing translation files and missing rows as valid so English fallback remains possible. That means an empty `approved-translations/` directory validates cleanly by design.
- The real workspace validation run only exercised the fallback path because no approved translation CSVs were added in Task 2.
- `source-manifest.sha256` is deterministic and currently covers the sorted CSV files under `resources/extracted/`.
- Review CSV exports now use UTF-8 with BOM to match the workspace contract.
- Repeated export is covered by test assertions for identical `entries.jsonl` and `source-manifest.sha256` content across runs.

## Commit

Commit hashes for fix rounds are returned separately and are not embedded here, so the report stays accurate even if later amendments create a new commit ID.
