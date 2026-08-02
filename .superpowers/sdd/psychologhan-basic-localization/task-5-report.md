# Task 5 Report: Build and verify the package

## Status

Implemented `scripts/validate_localization.py` and `tests/test_validate_localization.py`, validated the real approved translation workspace, produced the ignored `dist/` package after a successful Release build, and removed the temporary ignored `Directory.Build.props` used only for build verification.

## Changed files

- `scripts/validate_localization.py`
- `tests/test_validate_localization.py`
- `.superpowers/sdd/psychologhan-basic-localization/task-5-report.md`

No extractor/source CSVs, files under `resources/work/approved-translations/`, files under `resources/extracted/`, Steam game directory files, or unrelated tracked source files were modified.

## What `validate_localization.py` does

Required CLI:

```powershell
python scripts/validate_localization.py --project-root . --translations resources/work/approved-translations --profile localization/project-profile.json --dist dist
```

Implemented checks:

- Parses `localization/project-profile.json`.
- Parses `localization/translation-scope.json`.
- Parses `resources/work/translation-version.json`.
- Runs `scripts.translation_workspace.validate_import(...)` against `resources/work/entries.jsonl` and the approved translations directory.
- Requires approved categories in `translation-scope.json` to match `translation-version.json`.
- Allows fallback categories `dialogue` and `choice` to be absent.
- Verifies approved category files exist and match approved row counts from `translation-version.json`.
- Verifies CSV readability with UTF-8 / UTF-8 BOM handling.
- Reports malformed rows, duplicate keys, original-text drift, empty translations, newline-count drift, and protected-token drift via `translation_workspace.validate_import`.
- Inspects build output for `bin/Release/**/PsychologHan.dll` first, then other `bin/**/PsychologHan.dll` outputs if needed.
- When `--dist` is supplied and validation succeeds, creates only:
  - `dist/BepInEx/plugins/PsychologHan/PsychologHan.dll`
  - `dist/BepInEx/plugins/PsychologHan/localization/*.csv` for approved categories only
  - `dist/BepInEx/plugins/PsychologHan/package-manifest.json`

The validator never copies game DLLs, the game executable, or writes into the Steam install.

## Tests added

`tests/test_validate_localization.py` covers:

- successful validation + package creation;
- missing/invalid translation failures;
- dist-package allowlist enforcement;
- real CLI execution path (`python scripts/validate_localization.py ...`) from the repo root.

## TDD / debug notes

### Red-green cycle 1: validator behavior

Started with a missing module failure because `scripts/validate_localization.py` did not exist yet.

Command:

```powershell
python -m unittest tests.test_validate_localization.ValidateLocalizationTests.test_main_validates_workspace_and_builds_dist_package -v
```

Initial result:

```text
ModuleNotFoundError: No module named 'scripts.validate_localization'
```

Then implemented the validator and got the focused tests green.

### Red-green cycle 2: real CLI entrypoint

The imported module path worked, but the required CLI form failed because `python scripts/validate_localization.py` did not have the repo root on `sys.path`.

Command:

```powershell
python -m unittest tests.test_validate_localization.ValidateLocalizationTests.test_cli_script_execution_works_from_repo_root -v
```

Initial result:

```text
ModuleNotFoundError: No module named 'scripts'
```

Fix: add the repo root to `sys.path` when the script is executed as a file entrypoint. Re-ran the targeted test and the full Python suite successfully.

## Verification commands and outputs

### Full Python test suite

Command:

```powershell
python -m unittest discover -s tests -v
```

Result:

```text
Ran 30 tests in 1.704s

OK
```

### Release build: sandbox limitation

First sandboxed attempt:

```powershell
dotnet build -c Release
```

Result:

```text
error MSB4184: Access to the path 'C:\Users\LiuZhuoHeng\AppData\Local\Microsoft SDKs' is denied.
```

This was a sandbox limitation, not a project-code failure.

### Release build: baseline escalated attempt without local props

Command:

```powershell
dotnet build -c Release
```

Result:

```text
0 warnings, 418 errors
```

Primary cause:

- SDK default compile globs picked up `resources/Assembly-CSharp-decompiled/**/*.cs`, which pulled decompiled game sources into the plugin build and produced missing Unity UI/Timeline reference failures plus duplicate assembly attributes.

### Release build: verified scoped build with temporary ignored local props

Per the Task 5 brief, I created a temporary git-ignored `Directory.Build.props` only for build verification, using the documented local exclusion/deployment pattern from `Directory.Build.props.example`, and removed it before finishing.

Command:

```powershell
dotnet build -c Release
```

Result:

```text
PsychologHan -> D:\projects\PsychologHan\bin\Release\netstandard2.1\PsychologHan.dll

已成功生成。
    0 个警告
    0 个错误
```

Removal check after verification:

```powershell
Test-Path Directory.Build.props
```

Result:

```text
False
```

### Real workspace validation + dist generation

Command:

```powershell
python scripts/validate_localization.py --project-root . --translations resources/work/approved-translations --profile localization/project-profile.json --dist dist
```

Result:

```text
validation ok; package created at D:/projects/PsychologHan/dist/BepInEx/plugins/PsychologHan
```

## Produced dist package

Package contents:

```text
dist/BepInEx/plugins/PsychologHan/PsychologHan.dll
dist/BepInEx/plugins/PsychologHan/package-manifest.json
dist/BepInEx/plugins/PsychologHan/localization/character_name.csv
dist/BepInEx/plugins/PsychologHan/localization/client_info.csv
dist/BepInEx/plugins/PsychologHan/localization/ending.csv
dist/BepInEx/plugins/PsychologHan/localization/item.csv
dist/BepInEx/plugins/PsychologHan/localization/ui.csv
```

No dialogue or choice CSVs were packaged because they are fallback categories and are not currently part of the approved translation set in `resources/work/translation-version.json`.

## Package manifest snapshot

`dist/BepInEx/plugins/PsychologHan/package-manifest.json` records:

- locale: `zh-CN`
- plugin assembly: `PsychologHan`
- plugin version: `1.0.0`
- approved categories: `character_name`, `item`, `client_info`, `ending`, `ui`
- fallback categories: `dialogue`, `choice`
- translation-version metadata and hashes
- SHA-256 + size for the packaged DLL and each approved CSV

Observed packaged hashes:

- `PsychologHan.dll`: `55c73ecbc29528403b8188bf5a459fc36af76b8e0715a5c724a4d6063f7f090b`
- `localization/character_name.csv`: `f0117055bde203b3cdb1c5497990d2524a5f8d1ba5a75792d780a32d44986a4f`
- `localization/client_info.csv`: `0fcafa683f13ae0cfd5f8dd4f6fc70610bfd0e9db48234b64df557ed23277903`
- `localization/ending.csv`: `b41f55697860d42aa1af736c98d7bb58eb00fcbdbaf2419638537723e0c50f04`
- `localization/item.csv`: `5e4bb66ca9f3511628f2054e74b38fd520561984b1f3d12be8b7df348cd366a7`
- `localization/ui.csv`: `6cb519d01904c963a6153d53a70f8a19855b9d934f44aa93fcb9268de0c903ea`

## Exact limitations encountered

- Sandboxed MSBuild could not access `C:\Users\LiuZhuoHeng\AppData\Local\Microsoft SDKs`; Release build verification required an escalated retry.
- The first escalated Release build still failed until a temporary ignored `Directory.Build.props` excluded local `resources/` and `.skill-build/` C# trees from SDK compile globs.
- The escalated build performed restore checks against the configured NuGet feeds. In this environment they were reachable during the approved escalated build.

## Commit scope

Only the following tracked Task 5 files should be committed:

- `scripts/validate_localization.py`
- `tests/test_validate_localization.py`
- `.superpowers/sdd/psychologhan-basic-localization/task-5-report.md`
