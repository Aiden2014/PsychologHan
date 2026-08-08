# Unity Mono Localization Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a personal `localizing-unity-mono-games` Codex skill that drives a complete Unity Mono Chinese-localization workflow.

**Architecture:** Keep the core SKILL.md as a short decision pipeline. Put detailed extraction, Paratranz, patch, QA/image, and TMP guidance in one-level references; put deterministic project scaffolding, validation, character collection, and Unity batchmode invocation in Python scripts; include small BepInEx and Unity Editor templates as assets.

**Tech Stack:** Markdown skill instructions, Python 3 standard library, C# BepInEx 5/Harmony templates, Unity Editor batchmode, TextMeshPro, ILSpy CLI, AssetStudio CLI.

## Global Constraints

- Target Unity Mono only; defer IL2CPP.
- Default deployment is BepInEx 5 Mono Windows x64 from official GitHub Releases; use x86 only for verified 32-bit games.
- Prefer Python extraction from ILSpy code and AssetStudio JSON; runtime dumping is a later gap-filling step.
- Ignore all `resources/` and `dist/`; track `localization/` by default.
- Default TMP path is Unity Editor CLI-built AssetBundle; runtime TTF is capability-gated and experimental; manual Unity is fallback.
- Human playthrough validation remains required for runtime gaps, story coverage, images, fonts, and layout.

---

### Task 1: Initialize the skill and encode baseline failures

**Files:**
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/SKILL.md`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/agents/openai.yaml`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/references/`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/scripts/`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/`

**Interfaces:**
- Consumes: approved design and three no-skill baseline scenarios.
- Produces: a valid skill skeleton named `localizing-unity-mono-games`.

- [ ] **Step 1: Record the baseline gaps**

  Treat these as required corrections: baseline extraction suggested committing game-text snapshots; baseline runtime did not define a hotkey-to-AssetStudio image correlation contract; baseline TMP preferred runtime TTF over the approved bundle-first strategy; none bound all decisions into one reusable per-game profile.

- [ ] **Step 2: Initialize with skill-creator**

  Run `init_skill.py localizing-unity-mono-games --path D:/projects/PsychologHan/.skill-build --resources scripts,references,assets` with deterministic interface values.

- [ ] **Step 3: Verify the skeleton fails completeness checks**

  Run `quick_validate.py D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games` and grep for template markers. Expected: structural validation may pass, but template-marker scan fails until implementation.

### Task 2: Add and test deterministic helper scripts

**Files:**
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/scripts/scaffold_project.py`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/scripts/collect_font_characters.py`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/scripts/build_tmp_font_bundle.py`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/scripts/validate_project.py`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/scripts/test_skill_scripts.py`

**Interfaces:**
- `scaffold_project.py --name NAME --output DIR` creates the documented project layout without overwriting existing files.
- `collect_font_characters.py INPUT... --output FILE` emits deterministic unique non-whitespace characters from CSV/JSON/JSONL/TXT/MD.
- `build_tmp_font_bundle.py --unity UNITY --project PROJECT --font FONT --output DIR ...` validates inputs, writes a JSON request, and invokes Unity batchmode `BuildTmpFontBundle.Build`.
- `validate_project.py PROJECT` checks required tracked files and `.gitignore` rules, returning nonzero on hard failures.

- [ ] **Step 1: Write failing unittest cases**

  Cover scaffolded folders and `.gitignore`, no-overwrite behavior, deterministic character collection, dry-run Unity command construction, and invalid-project diagnostics.

- [ ] **Step 2: Run tests and confirm failure**

  Run `python D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/scripts/test_skill_scripts.py -v`. Expected: imports/files do not yet exist.

- [ ] **Step 3: Implement the four scripts with only the Python standard library**

  Provide `--help`, UTF-8 handling, actionable errors, deterministic output, and no automatic download or game-directory mutation.

- [ ] **Step 4: Run tests and help smoke tests**

  Expect all unittests to pass and every script's `--help` to exit 0.

### Task 3: Add reusable BepInEx and TMP builder assets

**Files:**
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/project-template/.gitignore`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/project-template/Directory.Build.props.example`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/project-template/Plugin.cs`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/project-template/TranslationManager.cs`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/project-template/MissingTextTracker.cs`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/project-template/ImageAudit.cs`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/project-template/project-profile.json`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/tmp-font-builder/Assets/Editor/BuildTmpFontBundle.cs`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/assets/tmp-font-builder/Packages/manifest.json`

**Interfaces:**
- Project assets are copied by `scaffold_project.py` and deliberately contain extension seams instead of game-specific Harmony targets.
- Unity Editor method reads the JSON request written by `build_tmp_font_bundle.py`, imports the font, creates a TMP FontAsset, builds a Windows AssetBundle, and writes a machine-readable result.

- [ ] **Step 1: Extend tests to assert asset/template contracts**

  Assert the ignored/tracked directories, `AuditMode`, structured missing-text fields, image component coverage, `BuildTmpFontBundle.Build`, and AssetBundle build call.

- [ ] **Step 2: Run the extended test and confirm failure**

- [ ] **Step 3: Add minimal adaptable templates**

  Keep game-specific patch points as explicit adapter methods and fail safely to original text/assets.

- [ ] **Step 4: Run the extended tests**

### Task 4: Write progressive-disclosure references and core SKILL.md

**Files:**
- Modify: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/SKILL.md`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/references/project-layout.md`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/references/extraction-and-story-flow.md`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/references/paratranz-and-profiles.md`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/references/bepinex-mono-patch.md`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/references/runtime-qa-and-images.md`
- Create: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/references/tmp-fonts.md`

**Interfaces:**
- SKILL.md routes each phase to exactly one relevant reference and enforces release gates.
- References contain commands, schemas, decision tables, common mistakes, and the PsychologHan acceptance example.

- [ ] **Step 1: Write the references**

  Include every approved requirement from the design, direct AssetStudio CLI syntax discovered from the installed executable, BepInEx deployment guidance, and explicit manual QA responsibilities.

- [ ] **Step 2: Replace template SKILL.md**

  Use a third-person `Use when...` description, imperative body, concise pipeline, hard rules, quick-reference decision table, and direct links to every reference/script/asset.

- [ ] **Step 3: Regenerate `agents/openai.yaml`**

  Use `generate_openai_yaml.py` with display name, short description, and default prompt derived from the completed skill.

- [ ] **Step 4: Run structural and placeholder checks**

  Run `quick_validate.py`; grep for `TODO`, `TBD`, placeholder prose, broken relative links, and a SKILL.md length over 500 lines.

### Task 5: Forward-test, validate, and deploy the personal skill

**Files:**
- Copy: `D:/projects/PsychologHan/.skill-build/localizing-unity-mono-games/` to `C:/Users/LiuZhuoHeng/.codex/skills/localizing-unity-mono-games/`

**Interfaces:**
- Consumes: completed staged skill.
- Produces: discoverable personal skill that passes the same validation at its deployed path.

- [ ] **Step 1: Re-run the three baseline prompts with the skill artifact available**

  Verify all outputs prefer Python static extraction, keep game data under ignored `resources/`, reconstruct story flow with confidence and runtime confirmation, use BepInEx 5 Mono deployment, require human gap validation, define image hotkey correlation, and choose bundle-first TMP strategy.

- [ ] **Step 2: Run PsychologHan fixture checks**

  Confirm the skill recognizes `resources/Assembly-CSharp-decompiled`, exported JSON assets, `scripts/extract_game_text.py`, `story*` flow extraction, existing `.gitignore`, and the Mono csproj as valid evidence without copying game content into the skill.

- [ ] **Step 3: Run all final validations**

  Run Python tests, script help smoke tests, `quick_validate.py`, JSON parsing, YAML generation, and relative-link checks.

- [ ] **Step 4: Deploy with approval**

  Copy the staged folder into the personal skill directory, replacing only the same skill folder if it was created by this task.

- [ ] **Step 5: Validate the deployed copy**

  Run `quick_validate.py` and the script tests from the final personal path. Expected: all pass.
