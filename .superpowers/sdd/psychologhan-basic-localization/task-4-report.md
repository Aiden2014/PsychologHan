# Task 4 Report: Typed Harmony runtime localization patch redesign

## Status

Task 4 urgent redesign implemented. The rejected reflection/manual patch-registration structure has been replaced with typed Harmony annotation patch classes compiled directly against the target game's Unity 2021 Mono Managed assemblies.

Task 5 remains paused.

## Changed files

- `Plugin.cs`
- `GamePatches.cs`
- `PsychologHan.csproj`
- `Directory.Build.props.example`
- `tests/test_task4_structure.py`
- `.superpowers/sdd/psychologhan-basic-localization/task-4-report.md`

No extractor code, extracted CSVs, `resources/work` generated translations, Steam game directory files, fonts/images, or unrelated tracked files were modified.

## Redesign implemented

- `Plugin` now creates Harmony once, calls `harmony.PatchAll()`, and keeps `harmony.UnpatchSelf()` on teardown.
- `GamePatches` now uses typed annotation patches:
  - `[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addMe), ...)]` + `[HarmonyPrefix]`
  - `[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addSpeaker), ...)]` + `[HarmonyPrefix]`
  - `[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addOpt), ...)]` + `[HarmonyPrefix]`
  - `[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateClientsSection))]` + `[HarmonyPostfix]`
  - `[HarmonyPatch(typeof(global::DeathRunes), "setRunes")]` + `[HarmonyPostfix]`
- Production patch code no longer contains:
  - `AccessTools.TypeByName`
  - manual `harmony.Patch(...)`
  - `object __instance`
  - `GetFieldValue`
  - `GetText`
  - `SetText`
- `GameManager __instance` and `DeathRunes __instance` are typed and access the confirmed public fields directly:
  - `clientCurrentlyChosen`
  - `trustComment`
  - `treatmentComment`
  - `runeVera`
  - `runeJaden`
  - `runeJoe`
  - `runeDeborah`
  - `runeAshley`
- `PsychologHan.csproj` now uses direct `<Reference>` entries through `$(GamePath)\Psycholog_Data\Managed\...` with `<Private>false</Private>` for:
  - `Assembly-CSharp.dll`
  - `UnityEngine.dll`
  - `UnityEngine.CoreModule.dll`
  - `UnityEngine.UI.dll`
  - `UnityEngine.UIModule.dll`
  - `Unity.TextMeshPro.dll`
  - `UnityEngine.TextRenderingModule.dll`
- `UnityEngine.Modules` 5.6 NuGet was removed.
- `UnityEngine.TextCoreModule.dll` is not referenced.
- Tracked `PsychologHan.csproj` no longer hardcodes the local Steam path. The ignored local `Directory.Build.props` provides `GamePath`; `Directory.Build.props.example` bridges `PsychologHanGamePath` to `GamePath`.

## Preserved behavior

- Exact stable key lookup remains first.
- Dialogue/choice runtime alias lookup remains category-scoped and original-text-checked.
- Original English text remains the fallback on every miss/malformed resource.
- Missing/ambiguous diagnostics remain deduplicated and default-disabled.
- The patch remains narrow: no global TMP/Text setter hook and no per-frame UI scan.

## Verification

### Structural regression

Command:

```powershell
python -m unittest tests.test_task4_structure
```

Output:

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

### Full Python tests

Command:

```powershell
python -m unittest discover -s tests
```

Output:

```text
validation ok; package created at C:/Users/LiuZhuoHeng/AppData/Local/Temp/psycholog-validate-localization-y4s3660l/project/dist/BepInEx/plugins/PsychologHan
..................................
----------------------------------------------------------------------
Ran 34 tests in 1.778s

OK
```

### Real target DLL compile

Command:

```powershell
dotnet build PsychologHan.csproj -c Release -v minimal
```

Output:

```text
  正在确定要还原的项目…
  所有项目均是最新的，无法还原。
  PsychologHan -> D:\projects\PsychologHan\bin\Release\netstandard2.1\PsychologHan.dll

已成功生成。
    0 个警告
    0 个错误

已用时间 00:00:01.15
```

### Static forbidden-token check

Command:

```powershell
rg -n "TypeByName|harmony\.Patch\(|GetFieldValue|GetText|SetText|UnityEngine\.Modules|TextCoreModule|AccessTools" Plugin.cs GamePatches.cs PsychologHan.csproj Directory.Build.props.example tests
```

Output only showed the forbidden strings inside `tests/test_task4_structure.py`, where they are regression-test assertions.

## Local build configuration

The current ignored local `Directory.Build.props` exists and contains the machine-local `GamePath` plus SDK compile exclusions for ignored generated folders:

```xml
<Project>
  <PropertyGroup>
    <GamePath>D:\SteamLibrary\steamapps\common\Psycholog</GamePath>
    <DefaultItemExcludes>$(DefaultItemExcludes);$(MSBuildProjectDirectory)\resources\**;$(MSBuildProjectDirectory)\.skill-build\**</DefaultItemExcludes>
  </PropertyGroup>
</Project>
```

This file is intentionally not committed.

## Remaining concern

This report covers compile/static verification only. Runtime BepInEx smoke testing in the game install is still a later release gate and was not performed during this urgent Task 4 redesign.
