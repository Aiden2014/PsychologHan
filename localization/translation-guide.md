# Translation Guide

Psycholog is a Chinese localization project built from managed code evidence and exported Unity assets.

## Source boundary

- Keep copied game corpus, extracted CSVs, and generated exports under ignored `resources/` paths.
- Keep only reviewable coordination files in `localization/`.
- Use `resources/Assembly-CSharp-decompiled` and the exported resource type directories as the evidence base.

## Approved translation categories

- `dialogue`
- `choice`
- `item`
- `character_name`
- `client_info`
- `ending`
- `ui`
- `image`

## CSV contract

- UTF-8 encoding.
- Three columns only: `key`, `original`, `translation`.
- Preserve the original text whenever a lookup fails.
- Do not invent a second master copy beside `resources/work/entries.jsonl`.

## Style rules

- Keep speaker identity stable across dialogue, choices, and UI labels.
- Prefer natural Chinese, but do not smooth away tense, uncertainty, or character voice.
- Preserve punctuation and line breaks when they carry meaning.
- Treat proper names as fixed glossary entries unless the story context clearly changes them.

## Runtime and image policy

- Use BepInEx 5 stable Mono x64.
- Patch a verified localization or data seam first.
- Fall back to the original text or asset on every failure.
- Build TMP fonts with the bundle-first strategy.
- Replace images only after human-confirmed correlation.

## QA gate

Do not treat automated checks as enough on their own.

- Confirm menus and settings.
- Confirm save and load.
- Confirm the critical story and choice branches.
- Confirm failure routes and endings.
- Confirm original behavior with the plugin disabled.
- Ship only when P0 and P1 findings are both zero and a human signs off.

