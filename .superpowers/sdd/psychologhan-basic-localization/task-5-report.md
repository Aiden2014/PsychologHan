# Task 5 Report: Build and verify the package

## Status

Task 5 fix round completed on 2026-08-02.

This round addressed the independent review findings:

- hardened `scripts/validate_localization.py --dist` so the resolved target must be exactly `project_root/dist`;
- rejected project-external dist targets and `project_root` itself before any package directory deletion can happen;
- refreshed the ignored `dist/` package from the current Release build produced after the typed Harmony Task 4 refactor;
- verified the packaged DLL hash and manifest hash match `bin/Release/netstandard2.1/PsychologHan.dll`.

No extractor scripts, source/extracted CSVs, approved translation CSVs, or Steam game directory files were modified.

## Changed tracked files

- `scripts/validate_localization.py`
- `tests/test_validate_localization.py`
- `.superpowers/sdd/psychologhan-basic-localization/task-5-report.md`

Ignored build/package outputs refreshed but not committed:

- `bin/Release/netstandard2.1/PsychologHan.dll`
- `dist/BepInEx/plugins/PsychologHan/`

## Validator/package behavior after fix

Required CLI remains:

```powershell
python scripts/validate_localization.py --project-root . --translations resources/work/approved-translations --profile localization/project-profile.json --dist dist
```

`--dist` handling now resolves relative paths against `project_root` and only accepts the exact resolved path `project_root/dist`. Any other target returns exit code 1 before `_create_dist_package(...)` can remove the existing plugin package directory.

Accepted package output remains:

```text
dist/BepInEx/plugins/PsychologHan/PsychologHan.dll
dist/BepInEx/plugins/PsychologHan/package-manifest.json
dist/BepInEx/plugins/PsychologHan/localization/character_name.csv
dist/BepInEx/plugins/PsychologHan/localization/client_info.csv
dist/BepInEx/plugins/PsychologHan/localization/ending.csv
dist/BepInEx/plugins/PsychologHan/localization/item.csv
dist/BepInEx/plugins/PsychologHan/localization/ui.csv
```

No dialogue or choice CSVs are packaged because they remain fallback categories rather than approved translated categories.

## Tests updated

`tests/test_validate_localization.py` now additionally covers:

- project-external `--dist` is rejected and an existing external package directory is not deleted;
- `--dist` equal to the project root is rejected;
- package manifest plugin SHA-256 matches the packaged DLL bytes.

## TDD notes for this fix round

New safety-boundary tests were added before changing production code.

Command:

```powershell
python -m unittest tests.test_validate_localization.ValidateLocalizationTests.test_main_rejects_dist_outside_project_without_deleting_existing_package tests.test_validate_localization.ValidateLocalizationTests.test_main_rejects_project_root_as_dist -v
```

Initial result before the validator fix:

```text
FAILED (failures=2)
AssertionError: 0 != 1
```

After adding `_resolve_dist_dir(...)` and checking it from `main(...)`, the same focused tests passed:

```text
Ran 2 tests in 0.049s

OK
```

The full validator test file also passed:

```text
Ran 6 tests in 0.308s

OK
```

## Verification commands and outputs

### Release build against the real target Managed DLLs

Sandboxed command:

```powershell
dotnet build PsychologHan.csproj -c Release -v minimal
```

Sandbox result:

```text
error MSB4184: Access to the path 'C:\Users\LiuZhuoHeng\AppData\Local\Microsoft SDKs' is denied.
```

Escalated retry of the same build command:

```text
PsychologHan -> D:\projects\PsychologHan\bin\Release\netstandard2.1\PsychologHan.dll

已成功生成。
    0 个警告
    0 个错误
```

The existing ignored `Directory.Build.props` was present for local machine paths and has deployment disabled.

### Full Python test suite

Command:

```powershell
python -m unittest discover -s tests -v
```

Result:

```text
Ran 36 tests in 2.087s

OK
```

### Validator without package output

Command:

```powershell
python scripts/validate_localization.py --project-root . --translations resources/work/approved-translations --profile localization/project-profile.json
```

Result:

```text
validation ok
```

### Validator with package output

Command:

```powershell
python scripts/validate_localization.py --project-root . --translations resources/work/approved-translations --profile localization/project-profile.json --dist dist
```

Result:

```text
validation ok; package created at D:/projects/PsychologHan/dist/BepInEx/plugins/PsychologHan
```

### Package hash verification

Observed hashes:

```text
bin/Release/netstandard2.1/PsychologHan.dll:
a5833628adefe43bfcf098c5fce315cf465970deb2509a006cba67c728de41cc

dist/BepInEx/plugins/PsychologHan/PsychologHan.dll:
a5833628adefe43bfcf098c5fce315cf465970deb2509a006cba67c728de41cc

dist/BepInEx/plugins/PsychologHan/package-manifest.json files.plugin.sha256:
a5833628adefe43bfcf098c5fce315cf465970deb2509a006cba67c728de41cc
```

`HashesMatch` result:

```text
True
```

Package allowlist observed:

```text
localization/character_name.csv
localization/client_info.csv
localization/ending.csv
localization/item.csv
localization/ui.csv
package-manifest.json
PsychologHan.dll
```

## Commit scope

Commit only Task 5 tracked files:

- `scripts/validate_localization.py`
- `tests/test_validate_localization.py`
- `.superpowers/sdd/psychologhan-basic-localization/task-5-report.md`

Do not commit ignored `dist/`, `bin/`, `obj/`, `resources/`, `.skill-build/`, `.npm-cache/`, or local `Directory.Build.props`.

## Post-release TMP font fix

The first runtime check showed Chinese text rendered as tofu because the game's TMP font assets do not contain CJK glyphs. The release package now includes an optional plugin-local runtime fallback:

```text
fonts/NotoSansSC-VF.ttf
```

`FontFallbackManager.cs` creates a dynamic TMP font asset through the verified target-version API and registers it in `TMP_Settings.fallbackFontAssets`. It does not patch text setters or modify the original game font assets. If the file is missing or creation fails, the plugin keeps the original behavior and logs a warning.

Final verification after the font fix:

```text
39 Python tests: OK
Release target-DLL build: 0 warnings, 0 errors
validator --dist dist: validation ok
```

The final package contains `fonts/NotoSansSC-VF.ttf`; its manifest SHA-256 is `763146584cf0710223441356b4395e279021b0806c196614377a7a0174ae074a`. The plugin DLL hash is recorded and matched against the Release build by the validator.
