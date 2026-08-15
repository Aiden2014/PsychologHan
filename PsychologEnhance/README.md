# PsychologEnhance

This is a small BepInEx 5 Mono child plugin for the current Psycholog build.

`GameScore.calculateAndDisplayGameScore()` gives Ashley `treatmentAshley / 13` after the 14-point survival bonus. With the existing 27–54 clamp, that segment tops out at `18.15` instead of the same `20`-point maximum used by Vera. The Harmony transpiler changes only that Ashley IL segment to the intended mapping `2 / 9 * treatmentAshley - 6`; the game's original display, rounding, other patient segments, and P30 unlock check remain in control.

Build with:

```powershell
dotnet build PsychologEnhance\PsychologEnhance.csproj -c Release
```

Deploy `bin\Release\netstandard2.1\PsychologEnhance.dll` under `BepInEx\plugins\PsychologEnhance\` in the same Psycholog installation used for the build. The project references the local game assemblies and does not copy them into the plugin output.
