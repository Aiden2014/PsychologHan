# Repository Guidelines

## Project Structure

This repository is a BepInEx/Unity Mono localization plugin for Psycholog. C# runtime code lives at the root (`Plugin.cs`, `GamePatches.cs`, `TranslationManager.cs`, and related managers). Python extraction, workspace, merge, and validation tools are in `scripts/`; their `unittest` coverage is in `tests/`. Reviewable translation guidance and glossary data belong in `localization/`. Extracted game data and generated packages stay in ignored `resources/`, `dist/`, `bin/`, `obj/`, `reports/`, and `artifacts/` directories.

## Build, Test, and Development Commands

- `python scripts/extract_game_text.py --project-root . --output-dir resources/extracted` extracts source text and asset metadata.
- `python scripts/translation_workspace.py export --project-root . --output-dir resources/work` creates editable translation CSVs and `entries.jsonl`.
- `python -m unittest discover -s tests -v` runs the full Python test suite.
- `python scripts/validate_localization.py --project-root . --translations resources/work/approved-translations --profile localization/project-profile.json --dist dist` validates approved translations and builds the package.
- Copy `Directory.Build.props.example` to the ignored `Directory.Build.props`, set the local game path, then run `dotnet build PsychologHan.csproj -c Release`.

## Coding Style & Naming

Use four spaces, UTF-8, and clear typed code. Follow standard C# PascalCase for types/methods and camelCase for locals; keep Harmony patches narrow and fail-safe. Python modules/functions use `snake_case`, classes use `PascalCase`, and scripts should remain standard-library compatible. Translation CSVs must remain three-column UTF-8 files with stable keys and preserved placeholders/newlines.

## Testing Guidelines

Add focused `unittest` cases beside the affected behavior using `test_<behavior>` names. Tests should use temporary fixtures and avoid requiring the installed game. Run the full discovery command before submitting changes; runtime/package changes should also run the localization validator and a Release build when local game references are available.

## Commits and Pull Requests

Use imperative Conventional Commit-style subjects, such as `feat: add ...`, `fix: preserve ...`, or `refactor: ...`. Keep commits focused. Pull requests should explain the runtime or data impact, list validation commands and results, link the relevant issue/spec when applicable, and include screenshots or in-game verification notes for UI changes. Never commit machine-local paths, extracted game data, or generated packages.
