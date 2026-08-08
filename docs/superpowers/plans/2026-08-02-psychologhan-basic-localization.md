# PsychologHan Basic Localization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing PsychologHan extraction output into a reviewable basic Chinese translation workspace and a safe BepInEx patch with English fallback.

**Architecture:** Keep `scripts/extract_game_text.py` and `resources/extracted/` as generated source evidence. Add a separate translation-workspace adapter that creates ignored JSONL/CSV work data and validates approved translations, then let a narrow Harmony patch translate verified `GameManager` data-entry methods plus a small approved UI text set.

**Tech Stack:** Python 3 standard library, UTF-8 CSV/JSONL, C# netstandard2.1, BepInEx 5 Mono x64, HarmonyX, Unity 2021 Mono runtime.

## Global Constraints

- Never write to `D:\SteamLibrary\steamapps\common\Psycholog`.
- Never overwrite `scripts/extract_game_text.py` or generated extraction evidence.
- Keep `resources/`, `dist/`, `bin/`, `obj/`, `reports/`, and `artifacts/` ignored.
- Use stable context-specific keys; do not use translated text as a lookup key.
- On every missing/invalid lookup, return the original game text and record only development diagnostics.
- Do not patch every `Text.text` or `TMP_Text.text` assignment.

### Task 1: Retrofit Phase 1 project metadata

**Files:**
- Create: `localization/project-profile.json`
- Create: `localization/README.md`
- Create: `localization/translation-guide.md`
- Create: `localization/glossary.csv`
- Create: `localization/characters/*.md`
- Create: `localization/story/README.md`
- Modify: `.gitignore` only if required by validator

- [ ] Record verified Unity/Mono/x64 facts, relative source paths, extractor command, fallback behavior, font/image policy, and QA gates.
- [ ] Run `validate_project.py` and fix only structural/ignore-policy issues.
- [ ] Confirm `git status` shows no `resources/` or machine-local data.

### Task 2: Build and validate the translation work layer

**Files:**
- Create: `scripts/translation_workspace.py`
- Create: `tests/test_translation_workspace.py`
- Create: `resources/work/entries.jsonl` via the tool

- [ ] Write tests for three-column parsing, stable key preservation, placeholder/newline extraction, unknown/duplicate/original-change rejection, and English fallback.
- [ ] Implement `export_entries(project_root, output_dir)` and `validate_import(entries, translated_csvs)` using only the standard library.
- [ ] Run the new tests and the existing extractor tests.
- [ ] Generate a source manifest and category review CSVs under ignored `resources/work/`.

### Task 3: Add reviewed basic translations

**Files:**
- Create: `resources/work/approved-translations/*.csv`
- Create: `resources/work/source-manifest.sha256` via the tool
- Create: `resources/work/translation-version.json`

- [ ] Translate the small stable categories with preserved keys and formatting: character names, UI labels, items, client info, and endings.
- [ ] Leave dialogue and choice rows empty unless a reviewed entry is explicitly supplied; runtime must fall back to English.
- [ ] Validate every approved CSV with the import validator.

### Task 4: Implement the narrow runtime patch

**Files:**
- Modify: `Plugin.cs`
- Create: `TranslationManager.cs`
- Create: `GamePatches.cs`
- Create: `MissingTextTracker.cs`
- Create: `Directory.Build.props.example`

- [ ] Load UTF-8 approved CSVs from `BepInEx/plugins/PsychologHan/localization` and support BOM/no-BOM.
- [ ] Patch the verified `GameManager.addMe`, `addSpeaker`, and `addOpt` methods with stable node/option keys.
- [ ] Apply only approved exact UI mappings during verified refresh points.
- [ ] Keep misses original and rate-limited; disable audit output by default.
- [ ] Add compatibility logging for Unity/game build and fail closed if resources are missing.

### Task 5: Build and verify the package

**Files:**
- Create: `scripts/validate_localization.py`
- Create: `dist/` contents only if build succeeds
- Create: `resources/runtime-audit/` only for ignored logs

- [ ] Run Python tests and the localization validator.
- [ ] Restore/build Release with local game/BepInEx references; do not copy game DLLs into the package.
- [ ] Inspect package contents and confirm only plugin DLL, approved translations, config example, and version/hash manifest are included.
- [ ] Report manual BepInEx bootstrap and playthrough checks as pending until run in the user’s game copy.
