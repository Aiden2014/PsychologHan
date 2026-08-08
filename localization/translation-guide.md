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

## Naming and consistency decisions (2026-08-04)

Human-reviewed decisions that apply to all approved CSV files:

- The protagonist is always addressed as 医生 ("Doc"). 治疗师 is reserved for the profession (心理治疗师); as an address it is replaced by 医生.
- Police ranks: Detective Jackson is 杰克逊侦探; Sergeant Tanaka is 田中警官. Avoid 警佐/警长/警探/探长.
- Names are unified to the glossary: 杰登 (not 杰顿), 埃杰顿 (not 埃哲顿), 艾米莉 (not 艾米丽), 雷蒙德 (not 雷蒙), 乔 (not 约瑟夫), 香农, 乔什, 薇拉·米尔斯, 阿什莉·泰勒, 黛博拉·史密斯, 杰登·汤普森, 乔·埃杰顿.
- Proper nouns are fully localized: streets (华盛顿街, 门罗街, 卡彭特路, 枫树路, 长角街, 雪松大道), neighborhoods (河畔郊区, 雪松高地), the hospital (圣乔治医院), and JW大楼. CBT is translated 认知行为疗法; DSM is translated 精神障碍诊断与统计手册 (DSM-5 kept as DSM-5).
- Steam and the game title PSYCHOLOG remain as-is.
- Level-1 scene development labels (e.g. "Vera death message at office", "Deborah: mall/session") are internal scene titles and are intentionally left in English.
- Character profiles under localization/characters/ are the authoritative per-character voice contract; review them before polishing dialogue.

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

