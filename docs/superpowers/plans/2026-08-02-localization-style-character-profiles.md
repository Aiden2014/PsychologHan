# Localization Style Guide and Character Profiles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the personal `localizing-unity-mono-games` skill with scaffolded, evidence-driven translation-style and character-profile contracts without embedding Psycholog-specific professional-domain policies.

**Architecture:** Copy the installed personal skill into an ignored staging directory, add contract tests first, then add two reusable Markdown templates and tighten Phase 3 guidance plus project structure validation. Run all tests and a fresh-context forward test against staging before copying only the verified changed files back to the personal skill directory.

**Tech Stack:** Markdown skill/reference assets, Python 3 standard library, `unittest`, Codex `quick_validate.py`, personal skill directory under `C:\Users\LiuZhuoHeng\.codex\skills`.

## Global Constraints

- Do not modify `D:\projects\PsychologHan\localization\translation-guide.md` or its current character profiles in this implementation.
- Do not add psychological-counseling, police/law-enforcement, Psycholog-specific, or other concrete professional-domain policies to generic templates.
- Represent project-specific expertise only through a neutral project-domain-policy extension point.
- Distinguish `Observed`, `Inferred`, and `Unknown/Conflicting`; attach confidence and source keys to inferences.
- Do not invent a full personality for low-evidence background characters.
- Do not overwrite existing project guidance during retrofit.
- Do not edit the installed personal skill until the staged copy passes focused and full verification.
- Do not commit ignored staging artifacts or unrelated dirty-worktree files.

---

### Task 1: Add RED contract tests for scaffold and validation behavior

**Files:**
- Stage copy: `artifacts/skill-style-character-profiles/localizing-unity-mono-games/`
- Modify in stage: `scripts/test_skill_scripts.py`
- Later modify in stage: `scripts/validate_project.py`
- Later create in stage: `assets/project-template/localization/translation-guide.md`
- Later create in stage: `assets/project-template/localization/characters/CHARACTER.md.example`

**Interfaces:**
- Consumes: existing `SCAFFOLD`, `VALIDATE`, `run_script`, and `SkillScriptTests` helpers.
- Produces: contract tests for template contents, structural validation, and generic-domain isolation.

- [ ] **Step 1: Create a clean ignored staging copy**

Verify that the exact target does not exist, create it under `artifacts/`, and copy the current personal skill recursively. Do not use `.skill-build/`, because it is pre-existing user-owned staging data.

```powershell
Test-Path 'D:\projects\PsychologHan\artifacts\skill-style-character-profiles'
New-Item -ItemType Directory -Path 'D:\projects\PsychologHan\artifacts\skill-style-character-profiles'
Copy-Item -Recurse -Path 'C:\Users\LiuZhuoHeng\.codex\skills\localizing-unity-mono-games' -Destination 'D:\projects\PsychologHan\artifacts\skill-style-character-profiles'
```

Expected: the initial `Test-Path` result is `False`; the staged skill contains the same files as the installed skill.

- [ ] **Step 2: Add failing scaffold/template contract tests**

Add these methods to `SkillScriptTests` before changing production assets:

```python
def test_scaffold_includes_translation_style_and_character_profile_templates(self) -> None:
    """New projects must receive reusable style and evidence-profile contracts."""
    with tempfile.TemporaryDirectory() as temporary_directory:
        project = Path(temporary_directory) / "style-project"
        result = run_script(SCAFFOLD, "--name", "Style Project", "--output", str(project))

        self.assertEqual(result.returncode, 0, result.stderr)
        guide_path = project / "localization" / "translation-guide.md"
        character_path = (
            project
            / "localization"
            / "characters"
            / "CHARACTER.md.example"
        )
        self.assertTrue(guide_path.is_file())
        self.assertTrue(character_path.is_file())

        guide = guide_path.read_text(encoding="utf-8")
        for contract in (
            "Global register and narrative distance",
            "Pronouns, honorifics, and forms of address",
            "Slang, profanity, and colloquial language",
            "Project domain policies",
            "Few-shot examples",
            "Source key",
            "Rejected translation",
        ):
            self.assertIn(contract, guide)

        profile = character_path.read_text(encoding="utf-8")
        for contract in (
            "Evidence coverage",
            "Observed",
            "Inferred",
            "Unknown/Conflicting",
            "Motivations, fears, values, and contradictions",
            "Relationships and forms of address",
            "Character arc and route-stage changes",
            "Language fingerprint",
            "Frequent words and recurring phrases",
            "Confidence",
            "Source key",
            "Few-shot examples",
            "Counterexamples",
        ):
            self.assertIn(contract, profile)

def test_generic_style_templates_do_not_embed_specific_professional_domains(self) -> None:
    """A reusable skill must expose an extension point without shipping game-domain policy."""
    template_root = SCRIPTS.parent / "assets" / "project-template" / "localization"
    content = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            template_root / "translation-guide.md",
            template_root / "characters" / "CHARACTER.md.example",
        )
    ).casefold()

    for forbidden in (
        "psycholog",
        "psychological counseling",
        "therapy terminology",
        "police terminology",
        "law-enforcement terminology",
        "心理咨询",
        "警务",
    ):
        self.assertNotIn(forbidden, content)
```

- [ ] **Step 3: Add a failing structural-validator test**

```python
def test_validate_requires_style_guide_and_character_directory(self) -> None:
    """Phase 3 inputs must be structurally present without requiring an example forever."""
    with tempfile.TemporaryDirectory() as temporary_directory:
        project = Path(temporary_directory) / "profile-project"
        scaffold = run_script(SCAFFOLD, "--name", "Profiles", "--output", str(project))
        self.assertEqual(scaffold.returncode, 0, scaffold.stderr)

        guide = project / "localization" / "translation-guide.md"
        guide.unlink()
        missing_guide = run_script(VALIDATE, str(project))
        self.assertNotEqual(missing_guide.returncode, 0)
        self.assertIn("localization/translation-guide.md", missing_guide.stderr)

        guide.write_text("# Translation Guide\n", encoding="utf-8")
        characters = project / "localization" / "characters"
        shutil.rmtree(characters)
        missing_characters = run_script(VALIDATE, str(project))
        self.assertNotEqual(missing_characters.returncode, 0)
        self.assertIn("localization/characters", missing_characters.stderr)
```

- [ ] **Step 4: Run the three tests and verify RED**

Run:

```powershell
python -m unittest `
  scripts.test_skill_scripts.SkillScriptTests.test_scaffold_includes_translation_style_and_character_profile_templates `
  scripts.test_skill_scripts.SkillScriptTests.test_generic_style_templates_do_not_embed_specific_professional_domains `
  scripts.test_skill_scripts.SkillScriptTests.test_validate_requires_style_guide_and_character_directory `
  -v
```

Expected: FAIL because both templates are absent and the validator does not require the new structure. A missing-module or interpreter error is not an acceptable RED result.

---

### Task 2: Implement reusable templates and structural validation

**Files:**
- Create in stage: `assets/project-template/localization/translation-guide.md`
- Create in stage: `assets/project-template/localization/characters/CHARACTER.md.example`
- Modify in stage: `scripts/validate_project.py`
- Test in stage: `scripts/test_skill_scripts.py`

**Interfaces:**
- Consumes: recursive `copy_template(project: Path) -> None` behavior; no scaffold code change is needed.
- Produces: a scaffolded global translation contract, a per-character evidence-profile template, and validation requirements for `localization/translation-guide.md` plus `localization/characters/`.

- [ ] **Step 1: Create the global translation-guide template**

Write this complete reusable seed:

```markdown
# Translation Guide

Replace instructional text with decisions supported by the game's source material. Obtain human approval before bulk translation.

## Locale and audience

- Target locale:
- Intended audience and rating constraints:
- Translation objective:

## Global register and narrative distance

- Default register and formality:
- Narrative distance and point of view:
- Literalness versus naturalization:
- Tone features that must survive translation:

## Pronouns, honorifics, and forms of address

- Default pronoun policy:
- Honorific policy:
- Relationship-dependent forms of address:
- Rules for changes across routes or story stages:

## Slang, profanity, and colloquial language

- Slang and colloquial register:
- Profanity strength and repetition:
- Offensive language and content-rating constraints:
- Contractions, fragments, and internet language:

## Humor and cultural references

- Humor, irony, and sarcasm:
- Puns and wordplay:
- Cultural references and adaptation limits:

## Punctuation, numbers, and emphasis

- Quotes, ellipses, dashes, and repeated punctuation:
- Capitalization or typographic emphasis:
- Numbers, dates, times, units, and currencies:

## Text-type constraints

- Dialogue:
- Choices:
- UI and buttons:
- System and tutorial text:
- Line breaks, width, and length limits:

## Protected syntax

- Placeholders and variables:
- TMP/UGUI rich-text tags:
- Escapes and meaningful newlines:
- Text that must remain untranslated:

## Names and glossary priority

- Canonical naming policy:
- Glossary precedence and permitted variants:
- Conflict-resolution rule:

## Project domain policies

List project-authored domain-policy files or sections here. Keep concrete domain terminology in the project, not in the reusable skill template.

## Escalation and human decisions

- Ambiguities requiring human review:
- Route conflicts:
- Content or style exceptions:
- Decision owner and recording location:

## Few-shot examples

Use only human-reviewed project text. Do not promote an unreviewed machine translation to a style precedent.

| Source key | Context | Original | Approved translation | Why this is canonical |
|---|---|---|---|---|

## Counterexamples

| Source key | Original | Rejected translation | Corrected translation | Why it was rejected |
|---|---|---|---|---|
```

- [ ] **Step 2: Create the character-profile template**

```markdown
# Character Profile: CHARACTER_ID

Build this profile from the complete available source corpus for this character. Keep facts, inferences, and unknowns separate.

## Identity and role

- Canonical ID:
- Display name and aliases:
- Narrative role:
- Routes, chapters, and story stages:

## Evidence coverage

- Source files/modules:
- Analyzed lines:
- Covered routes/stages:
- Known gaps:

## Relationships and forms of address

| Other character | Relationship | Address used by this character | Address used toward this character | Story stage | Source key |
|---|---|---|---|---|---|

## Overall character assessment

### Observed

Record only facts, actions, and experiences directly supported by source text.

| Statement | Source key | Route/stage |
|---|---|---|

### Inferred

Cover personality, values, coping patterns, and decision tendencies. Do not infer a stable trait from one isolated line.

| Inference | Confidence (`high`/`medium`/`low`) | Evidence and source key | Alternative interpretation |
|---|---|---|---|

### Unknown/Conflicting

| Question or conflict | Conflicting evidence and source keys | Required follow-up |
|---|---|---|

## Motivations, fears, values, and contradictions

| Dimension | Assessment | Evidence status | Confidence | Source key |
|---|---|---|---|---|

## Character arc and route-stage changes

| Route/stage | Behavioral change | Speech change | Evidence status | Source key |
|---|---|---|---|---|

## Language fingerprint

- Typical sentence length and complexity:
- Pauses, hesitation, repetition, correction, and emphasis:
- Formality, politeness, slang, profanity, and euphemism:
- Recurring speech acts such as avoidance, questioning, reassurance, or commands:
- Changes by emotion, relationship, route, or story stage:

### Frequent words and recurring phrases

Record observed frequency or mark it as human-confirmed. Never use model-invented lines as evidence.

| Word or phrase | Count | Context/function | Source keys |
|---|---:|---|---|

## Chinese translation contract

- Target register and rhythm:
- Pronouns, honorifics, and forms of address:
- Preferred wording and allowed variants:
- Forbidden wording:
- Traits that must remain visible:
- Features that may be naturalized:
- Line-length and layout constraints:

## Few-shot examples

Use only human-reviewed translations.

| Source key | Route/stage | Original | Approved translation | Character feature demonstrated |
|---|---|---|---|---|

## Counterexamples

| Source key | Original | Rejected translation | Corrected translation | Why it is out of character |
|---|---|---|---|---|

## Human review

- Reviewer:
- Review date:
- Unresolved decisions:
```

- [ ] **Step 3: Require the guide and character directory structurally**

Change `validate_project.py` constants to:

```python
REQUIRED_DIRECTORIES = (
    "resources",
    "localization",
    "localization/characters",
    "reports",
    "artifacts",
)
REQUIRED_FILES = (
    ".gitignore",
    "README.md",
    "localization/README.md",
    "localization/project-profile.json",
    "localization/translation-guide.md",
)
```

Do not require `CHARACTER.md.example`; an existing project with real character profiles remains structurally valid without retaining the example.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run the three tests from Task 1.

Expected: all three PASS. Confirm a newly scaffolded project also passes `validate_project.py` through the existing scaffold test.

---

### Task 3: Strengthen Phase 3 evidence and translation guidance

**Files:**
- Modify in stage: `SKILL.md`
- Modify in stage: `references/paratranz-and-profiles.md`
- Modify in stage: `scripts/test_skill_scripts.py`

**Interfaces:**
- Consumes: the two template paths created in Task 2 and the existing Phase 3 gate.
- Produces: mandatory pre-translation evidence workflow, project-specific-domain isolation, and safe retrofit instructions.

- [ ] **Step 1: Add a failing guidance contract test**

```python
def test_phase_three_requires_evidence_driven_style_and_character_profiles(self) -> None:
    """Bulk translation must be grounded in reviewed global and per-character contracts."""
    skill_root = SCRIPTS.parent
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    guidance = (skill_root / "references" / "paratranz-and-profiles.md").read_text(
        encoding="utf-8"
    )

    for contract in (
        "review the translation guide and major character profiles before bulk dialogue translation",
        "project-specific domain policies",
        "do not overwrite existing human-authored profiles",
    ):
        self.assertIn(contract, skill + guidance)

    for contract in (
        "Observed",
        "Inferred",
        "Unknown/Conflicting",
        "confidence",
        "source key",
        "complete available source corpus",
        "frequent words and recurring phrases",
        "human-reviewed few-shot examples",
        "low-evidence background characters",
    ):
        self.assertIn(contract, guidance)
```

- [ ] **Step 2: Run the new test and verify RED**

Run:

```powershell
python -m unittest scripts.test_skill_scripts.SkillScriptTests.test_phase_three_requires_evidence_driven_style_and_character_profiles -v
```

Expected: FAIL because the current Phase 3 reference lacks the complete evidence and retrofit contract.

- [ ] **Step 3: Add the concise hard rule and asset links to `SKILL.md`**

Add this hard rule after the `entries.jsonl` rule:

```markdown
- Build and obtain human review for the translation guide and major character profiles before bulk dialogue translation. Keep concrete professional terminology in project-specific domain policies, separate facts from inferences with source evidence, and do not overwrite existing human-authored profiles during retrofit.
```

Extend the bundled-assets bullet with direct links to:

```markdown
[translation style guide](assets/project-template/localization/translation-guide.md) and [character evidence profile](assets/project-template/localization/characters/CHARACTER.md.example)
```

- [ ] **Step 4: Replace the shallow Phase 3 profile paragraph with the evidence workflow**

Replace the current `## Translation guide, glossary, and characters` section in `references/paratranz-and-profiles.md` with this exact generic guidance:

````markdown
## Translation guide, glossary, and characters

### Build the global style contract

Keep translator-facing guidance in `localization/translation-guide.md`. Before bulk dialogue translation, define and obtain human review for:

- target locale, audience, global register, narrative distance, and naturalization limits;
- pronouns, honorifics, forms of address, and relationship- or route-dependent changes;
- slang, profanity, offensive language, colloquial fragments, humor, irony, puns, and cultural references;
- punctuation, ellipses, emphasis, numbers, dates, units, meaningful newlines, and per-text-type length limits;
- placeholders, TMP/UGUI tags, escapes, untranslated content, glossary priority, and escalation rules;
- human-reviewed few-shot examples and counterexamples with source keys, context, and reasons.

Keep concrete professional terminology in project-specific domain policies authored under the project's `localization/` tree. The reusable skill defines only this extension point and supplies no game- or profession-specific policy.

Use a stable glossary schema:

```csv
source,translation,domain,note,allowed_variants,forbidden_translations
Inventory,物品栏,ui,Primary menu label,背包,库存
```

### Build evidence-driven character profiles

Maintain one file per character under `localization/characters/`. Group the complete available source corpus by stable speaker ID before profiling. Record source modules, analyzed-line count, route/stage coverage, and known gaps.

Separate the assessment into:

- `Observed`: identity, actions, experiences, and behaviors directly supported by source text;
- `Inferred`: personality, motivations, fears, values, contradictions, coping patterns, and decision tendencies derived from multiple pieces of evidence;
- `Unknown/Conflicting`: unanswered questions or route evidence that supports incompatible readings.

Give every inference `high`, `medium`, or `low` confidence and at least one source key. Record relationships, forms of address, character arc and route-stage changes, and a language fingerprint covering sentence length, syntax, pauses, hesitation, repetition, emphasis, formality, slang, profanity, euphemism, and common speech acts.

Compute reproducible surface evidence where possible: line counts, route coverage, frequent words and recurring phrases, sentence length, and punctuation or hesitation patterns. Observed frequency or human confirmation must support every claimed catchphrase; model-invented lines are never evidence.

Define a Chinese translation contract for register, rhythm, address, preferred and forbidden wording, preserved traits, permitted naturalization, and layout limits. Add only human-reviewed few-shot examples and counterexamples. When reviewed translations do not yet exist, mark examples as awaiting review rather than treating machine output as precedent.

Low-evidence background characters with only a few lines receive a minimal evidence profile. Do not fabricate a complete personality to fill the template. Review the translation guide and major character profiles before bulk dialogue translation; inferred personality is not ground truth.

### Retrofit existing projects safely

Preserve existing human-authored guidance and profiles. Add missing sections or create missing files without replacing reviewed decisions. When new routes or evidence contradict an earlier inference, retain the conflict and update confidence instead of silently rewriting it.
````

- [ ] **Step 5: Run the focused guidance test and all template tests**

Expected: all Phase 3, scaffold, structural, and domain-isolation tests PASS.

---

### Task 4: Full verification, forward test, and personal-skill deployment

**Files:**
- Verify staged tree: `artifacts/skill-style-character-profiles/localizing-unity-mono-games/`
- Deploy changed files to: `C:\Users\LiuZhuoHeng\.codex\skills\localizing-unity-mono-games\`

**Interfaces:**
- Consumes: the fully tested staged skill.
- Produces: a deployed personal skill with matching hashes and no changes to Psycholog project localization data.

- [ ] **Step 1: Run the full staged test suite**

Run:

```powershell
python -m unittest scripts.test_skill_scripts -v
```

Expected: all existing and new tests PASS with zero failures and errors.

- [ ] **Step 2: Run structural skill validation**

Run `skill-creator/scripts/quick_validate.py` against the staged skill using UTF-8 mode and an available PyYAML environment.

Expected: `Skill is valid!`

- [ ] **Step 3: Run a fresh-context forward test**

Dispatch a fresh agent with no conversation context:

```text
Use the skill at D:\projects\PsychologHan\artifacts\skill-style-character-profiles\localizing-unity-mono-games\SKILL.md. A fictional Unity Mono fantasy game has one protagonist with 900 lines, one rival with 500 lines across two routes, and six background characters with 1-3 lines each. Prepare the project for bulk Chinese dialogue translation. Describe the files and evidence you would create, what belongs in the global guide versus character profiles, and when translation may begin. Do not edit files.
```

Acceptance criteria:

- Creates a global style contract including register, address/honorific, slang/profanity, formatting, and reviewed few-shot examples.
- Builds full evidence profiles for major characters from all available lines.
- Distinguishes observed facts, inferences, conflicts, confidence, and source keys.
- Records recurring phrases and language features from evidence.
- Uses minimal profiles for 1-3-line background roles without inventing personalities.
- Treats domain policy as project-defined and introduces no Psycholog, counseling, police, or law-enforcement assumptions.
- Waits for human review before bulk translation.

- [ ] **Step 4: Compare staged changes against installed originals**

Confirm exactly these files differ or are new:

```text
SKILL.md
references/paratranz-and-profiles.md
scripts/validate_project.py
scripts/test_skill_scripts.py
assets/project-template/localization/translation-guide.md
assets/project-template/localization/characters/CHARACTER.md.example
```

Stop if any unrelated staged file differs.

- [ ] **Step 5: Deploy only the verified files**

Request filesystem approval, then copy the six files to the corresponding personal-skill paths. Create the destination `assets/project-template/localization/characters/` directory if missing. Do not overwrite any `D:\projects\PsychologHan\localization\` file.

- [ ] **Step 6: Re-run verification against the installed skill**

Run the full `unittest` suite and `quick_validate.py` from the installed personal skill. Hash each deployed file and compare it to the staged source.

Expected: all tests PASS, `Skill is valid!`, and all six hashes match.

- [ ] **Step 7: Remove only temporary artifacts created by this implementation**

Resolve and verify that the cleanup target is exactly inside:

```text
D:\projects\PsychologHan\artifacts\skill-style-character-profiles\
```

Remove that temporary staging directory. Do not remove `.skill-build/`, `.npm-cache/`, other `artifacts/` contents, or user files.
