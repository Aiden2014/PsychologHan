# Task 4 Report: Narrow runtime localization patch

## Status

Implemented the narrow BepInEx/Harmony runtime patch in the requested plugin files. The patch loads approved CSV translations from a plugin-local `localization` directory, preserves original text on every miss or malformed row, and keeps missing/malformed diagnostics deduplicated behind the default-disabled `Audit:DevelopmentDiagnostics` config.

## Changed files

- `Plugin.cs`
- `TranslationManager.cs`
- `GamePatches.cs`
- `MissingTextTracker.cs`
- `Directory.Build.props.example`
- `.superpowers/sdd/psychologhan-basic-localization/task-4-report.md`

No extractor code, extraction CSVs, approved generated CSVs under `resources/work`, Steam game directory files, font/image files, or unrelated tracked files were modified.

## Runtime/deployment contract

Approved generated translations remain ignored under:

```text
resources/work/approved-translations/
```

At runtime the plugin only reads CSVs from a plugin-local sibling directory:

```text
BepInEx/plugins/PsychologHan/localization/
```

Copy `resources/work/approved-translations/*.csv` into that plugin-local `localization/` directory when deploying. `Directory.Build.props.example` documents this contract and includes an opt-in `PsychologHanDeployToGame=true` target for local deployment; it defaults to `false` and does not write to the Steam game directory unless a developer explicitly enables it.

## Implemented seams

- `GameManager.addMe(int id, string text, int toId, Action customFuncIn = null)`
  - Harmony prefix translates `ref string text`.
  - Runtime dialogue key mapping: `id|||ME|||id`.
  - If no dialogue key is available, applies the approved `item` category as an exact-original fallback only.

- `GameManager.addSpeaker(int id, string speakerName, string text, int toId, Action customFuncIn = null, string imageName = "")`
  - Harmony prefix translates `ref string text`.
  - Runtime dialogue key mapping: `id|||speaker|||id`.
  - If no dialogue key is available, applies the approved `item` category as an exact-original fallback only.
  - Speaker display names are translated through `character_name` by exact key/original. The sentinel `(ME)` is preserved because the game uses it to hide the speaker caption.

- `GameManager.addOpt(int fromId, long id, string text, int toId)`
  - Harmony prefix translates `ref string text`.
  - Runtime choice key mapping: `from|||option|||option`, using `None` for `fromId == 0`.

- `GameManager.updateClientsSection()`
  - Harmony postfix translates the currently assigned `trustComment` and `treatmentComment` text fields for the selected client.
  - Uses known `client_info` keys such as `trustCommentVera` and `treatmentCommentVera`, then the narrow approved-original `client_info` fallback.

- `DeathRunes.setRunes()` (non-public)
  - Harmony postfix translates the five rune text fields through approved `ending` mappings.
  - Uses base keys such as `runeVera` when the original matches, then the narrow approved-original `ending` fallback for branch-specific ending texts.

## UI scope

`ui.csv` is loaded into the approved dictionary if deployed, but no UI patch is applied in Task 4. I did not add a global TMP/Text setter patch or per-frame scan. The plugin logs a UI extension seam because the current verified references do not provide a safe, stable, non-global UI refresh hook.

## Build/test commands and output

### Baseline build without local props

Command:

```powershell
dotnet build D:\projects\PsychologHan\PsychologHan.csproj --no-restore -v:minimal
```

Sandboxed output:

```text
C:\Program Files\dotnet\sdk\10.0.302\Microsoft.Common.CurrentVersion.targets(93,5): error MSB4184: 无法计算表达式“[Microsoft.Build.Utilities.ToolLocationHelper]::GetPlatformSDKLocation(Windows, 7.0)”。Access to the path 'C:\Users\LiuZhuoHeng\AppData\Local\Microsoft SDKs' is denied. [D:\projects\PsychologHan\PsychologHan.csproj]
```

Escalated output:

```text
D:\projects\PsychologHan\obj\Debug\netstandard2.1\.NETStandard,Version=v2.1.AssemblyAttributes.cs(4,12): error CS0579: “global::System.Runtime.Versioning.TargetFrameworkAttribute”特性重复 [D:\projects\PsychologHan\PsychologHan.csproj]
D:\projects\PsychologHan\resources\Assembly-CSharp-decompiled\AC\ActionTimeline.cs(4,19): error CS0234: 命名空间“UnityEngine”中不存在类型或命名空间名“Playables”(是否缺少程序集引用?) [D:\projects\PsychologHan\PsychologHan.csproj]
...
0 warnings, 418 errors
```

Cause: default SDK compile globs include ignored `resources/` and `.skill-build/` C# files when those folders are physically present. `Directory.Build.props.example` now documents the required local exclusion.

### Scoped plugin build with temporary ignored local props

For verification only, I temporarily created a git-ignored `Directory.Build.props` containing the same `DefaultItemExcludes` rule shown in `Directory.Build.props.example`, ran the build, then removed the temporary file before committing.

Command:

```powershell
dotnet build D:\projects\PsychologHan\PsychologHan.csproj --no-restore -v:minimal
```

Output:

```text
PsychologHan -> D:\projects\PsychologHan\bin\Debug\netstandard2.1\PsychologHan.dll

已成功生成。
    0 个警告
    0 个错误

已用时间 00:00:00.85
```

### Existing Python tests

Command:

```powershell
python -m unittest tests.test_extract_game_text tests.test_translation_workspace
```

Output:

```text
......................
----------------------------------------------------------------------
Ran 22 tests in 1.511s

OK
```

### Static seam checks

Command:

```powershell
rg -n 'public void addMe|public void addSpeaker|public void addOpt|public void updateClientsSection|private void setRunes' resources/Assembly-CSharp-decompiled/GameManager.cs resources/Assembly-CSharp-decompiled/DeathRunes.cs
```

Output:

```text
resources/Assembly-CSharp-decompiled/DeathRunes.cs:30:	private void setRunes()
resources/Assembly-CSharp-decompiled/GameManager.cs:1134:	public void addMe(int id, string text, int toId, Action customFuncIn = null)
resources/Assembly-CSharp-decompiled/GameManager.cs:1141:	public void addSpeaker(int id, string speakerName, string text, int toId, Action customFuncIn = null, string imageName = "")
resources/Assembly-CSharp-decompiled/GameManager.cs:1616:	public void addOpt(int fromId, long id, string text, int toId)
resources/Assembly-CSharp-decompiled/GameManager.cs:1896:	public void updateClientsSection()
```

Command:

```powershell
rg -n "HarmonyPatch\(|TMP_Text|TextMeshPro|\.text\s*=|Update\(|Resources\.Load|resources/work|SteamLibrary|BepInEx\\plugins" Plugin.cs TranslationManager.cs GamePatches.cs MissingTextTracker.cs Directory.Build.props.example
```

Output:

```text
Directory.Build.props.example:9:    - Copy approved CSVs from ignored resources/work/approved-translations/ into
Directory.Build.props.example:11:    - The plugin never reads resources/work at runtime and preserves original text
Directory.Build.props.example:16:    <PsychologHanGamePath>D:\SteamLibrary\steamapps\common\Psycholog</PsychologHanGamePath>
Directory.Build.props.example:18:    <PsychologHanPluginDeployDir>$(PsychologHanGamePath)\BepInEx\plugins\PsychologHan</PsychologHanPluginDeployDir>
```

This confirms the plugin code does not introduce a global TMP/Text setter patch, frame scanner, resource loader, or direct runtime dependency on `resources/work`.

## TDD note

No new repo test files were added because the Task 4 file list was explicit and narrow. I used compile checks, existing tests, static seam checks, and a code review pass instead. The scoped plugin build initially failed at baseline because local ignored reference folders were included in SDK compile globs, then passed after applying the documented local props exclusion.

## Concerns / follow-ups

- Normal local builds need `Directory.Build.props.example` copied to `Directory.Build.props` (or equivalent MSBuild exclusions) when ignored `resources/` and `.skill-build/` folders exist in the checkout.
- Current approved runtime translations include `character_name`, `item`, `client_info`, `ending`, and `ui`; there are no approved `dialogue.csv` or `choice.csv` files under `resources/work/approved-translations/` yet, so dialogue/choice patches will safely preserve original text until plugin-local approved files are deployed.
- UI integration remains an explicit extension seam pending a verified stable refresh hook.

## Review fix round 1

### Status

Implemented runtime-aware dialogue/choice alias lookup. Exact key lookup still wins first. If an exact key does not match, `TranslationManager.TryTranslateRuntimeKey` now compares only the first two `|||` segments within the same category, requires the runtime original to equal the candidate original, and accepts only one matching candidate. Zero matches preserve the original through the normal miss path; multiple matches preserve the original and record a deduplicated ambiguous-alias diagnostic.

`GamePatches` now uses the runtime-aware lookup for:

- `AddMePrefix`
- `AddSpeakerPrefix`
- `AddOptPrefix`

The UI extension-seam log is now unconditional: it is emitted even when `ui.csv` is absent or malformed, and explicitly states that missing/malformed UI resources preserve original UI text.

### Additional changed file

- `tests/test_task4_runtime_aliases.py`

### Focused red/green test

Initial red run after adding the focused test:

```powershell
python -m unittest tests.test_task4_runtime_aliases
```

Output:

```text
FAIL: test_csharp_uses_runtime_alias_lookup_for_dialogue_and_choice_prefixes
AssertionError: 'TryTranslateRuntimeKey' not found in '...TranslationManager.cs...'

Ran 4 tests in 0.002s
FAILED (failures=1)
```

Green run after implementation:

```powershell
python -m unittest tests.test_task4_runtime_aliases
```

Output:

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

The focused test covers:

- Extracted dialogue key example `14100|||ME|||2190` matching runtime key `14100|||ME|||14100` when the original matches.
- Extracted choice key example `14104|||14104|||2200` matching runtime key `14104|||14104|||14104` when the original matches.
- Ambiguous first-two-segment alias candidates preserving the original.
- Static integration checks that the C# runtime alias methods exist and are used by dialogue/choice patches.

### Scoped plugin build

For verification only, I temporarily created a git-ignored `Directory.Build.props` with the documented `DefaultItemExcludes`, ran the build, then removed the temporary file.

Command:

```powershell
dotnet build D:\projects\PsychologHan\PsychologHan.csproj --no-restore -v:minimal
```

Output:

```text
PsychologHan -> D:\projects\PsychologHan\bin\Debug\netstandard2.1\PsychologHan.dll

已成功生成。
    0 个警告
    0 个错误

已用时间 00:00:01.58
```

### Full Python tests

Command:

```powershell
python -m unittest tests.test_extract_game_text tests.test_translation_workspace tests.test_task4_runtime_aliases
```

Output:

```text
..........................
----------------------------------------------------------------------
Ran 26 tests in 1.488s

OK
```

### Static checks

Command:

```powershell
rg -n "TryTranslateRuntimeKey|FirstTwoSegmentPrefix|RecordAmbiguousAlias|TranslateRuntimeKeyWithOptionalOriginalFallback|TranslateRuntimeKeyOrOriginal|UI localization extension seam" TranslationManager.cs GamePatches.cs MissingTextTracker.cs Plugin.cs
```

Output:

```text
GamePatches.cs:80:        text = TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory, dialogueKey, text, ItemCategory);
GamePatches.cs:87:        text = TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory, dialogueKey, text, ItemCategory);
GamePatches.cs:98:        text = TranslateRuntimeKeyOrOriginal(ChoiceCategory, choiceKey, text);
GamePatches.cs:145:    private static string TranslateRuntimeKeyOrOriginal(string category, string runtimeKey, string original)
GamePatches.cs:176:    private static string TranslateRuntimeKeyWithOptionalOriginalFallback(string category, string key, string original, string fallbackCategory)
GamePatches.cs:184:        if (Plugin.Translations.TryTranslateRuntimeKey(category, key, original, out translated))
TranslationManager.cs:107:        if (TryTranslateRuntimeKey(category, runtimeKey, original, out translated))
TranslationManager.cs:159:    public bool TryTranslateRuntimeKey(string category, string runtimeKey, string original, out string translated)
TranslationManager.cs:175:        string aliasPrefix = FirstTwoSegmentPrefix(runtimeKey);
TranslationManager.cs:212:            diagnostics.RecordAmbiguousAlias(category, runtimeKey, original, matchedEntryCount);
TranslationManager.cs:342:        string aliasPrefix = FirstTwoSegmentPrefix(entry.Key);
TranslationManager.cs:447:    private static string FirstTwoSegmentPrefix(string key)
MissingTextTracker.cs:38:    public void RecordAmbiguousAlias(string category, string runtimeKey, string original, int candidateCount)
Plugin.cs:41:        Logger.LogInfo("UI localization extension seam: Task 4 loads ui.csv when present, but applies no UI patch because no stable non-global UI refresh hook is verified in the current references. Missing or malformed ui.csv preserves original UI text.");
```

Command:

```powershell
rg -n "HarmonyPatch\(|TMP_Text|TextMeshPro|\.text\s*=|Update\(|Resources\.Load|resources/work|SteamLibrary|BepInEx\\plugins" Plugin.cs TranslationManager.cs GamePatches.cs MissingTextTracker.cs Directory.Build.props.example
```

Output:

```text
Directory.Build.props.example:9:    - Copy approved CSVs from ignored resources/work/approved-translations/ into
Directory.Build.props.example:11:    - The plugin never reads resources/work at runtime and preserves original text
Directory.Build.props.example:16:    <PsychologHanGamePath>D:\SteamLibrary\steamapps\common\Psycholog</PsychologHanGamePath>
Directory.Build.props.example:18:    <PsychologHanPluginDeployDir>$(PsychologHanGamePath)\BepInEx\plugins\PsychologHan</PsychologHanPluginDeployDir>
```

Temporary local props removal check:

```powershell
Test-Path D:\projects\PsychologHan\Directory.Build.props
```

Output:

```text
False
```
