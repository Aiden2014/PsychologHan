# PsychologEnhance

This is a small BepInEx 5 Mono child plugin for the current Psycholog build.

The verified `Assembly-CSharp.dll` SHA-256 is `B0078981C2A42C8123D53E1CACFDA9F222B415565A3241175EA18E0B7DCF5F91`. A different build is left unpatched.

`GameScore.calculateAndDisplayGameScore()` gives Ashley `treatmentAshley / 13` after the 14-point survival bonus. With the existing 27–54 clamp, that segment tops out at `18.15` instead of the same `20`-point maximum used by Vera. A regular Harmony prefix replaces the score method with the same source calculation, changing only Ashley to the intended mapping `2 / 9 * treatmentAshley - 6`.

Build with:

```powershell
dotnet build PsychologEnhance\PsychologEnhance.csproj -c Release
```

Deploy `PsychologEnhance\bin\Release\netstandard2.1\PsychologEnhance.dll` under `BepInEx\plugins\PsychologEnhance\` in the same Psycholog installation used for the build. Do not compile the child source into `PsychologHan.dll`; loading the same patch from both plugin classes registers it twice.
