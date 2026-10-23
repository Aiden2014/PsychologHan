"""Run the real C# lookup against temporary CSVs; no Unity/game install needed."""

import csv
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
DRIFT = [
    ("dialogue", "88106|||ME", "\u2019", "\u009d"),
    ("dialogue", "88110|||ME", "\u2019", "\u009d"),
    ("dialogue", "88111|||ME", "\u2019", "\u009d"),
    ("dialogue", "26581|||RAYMOND", "\u2026", "?"),
    ("dialogue", "26616|||RAYMOND", "\u2019", "?"),
    ("choice", "26585|||26585", "\u2019", "?"),
    ("choice", "26600|||26602", "\u2019", "?"),
]


class UpdatedGameTextTests(unittest.TestCase):
    def test_verified_punctuation_changes_preserve_translation_and_lookup_guards(self):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("PowerShell 7 is required to compile the actual C# lookup")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = {"dialogue": [], "choice": [], "ui": []}
            cases = []
            for index, (category, prefix, old, new) in enumerate(DRIFT):
                original = "First? A" + old + "B\nLast."
                current = original.replace(old, new).replace("\n", "\r\n")
                translated = "译文" + str(index)
                key = prefix + "|||runtime"
                # Cover both exact keys and extracted source-line aliases.
                csv_key = key if index == 0 else prefix + "|||123"
                rows[category].append((csv_key, original, translated))
                cases.extend([
                    dict(category=category, key=key, original=current, expected=translated),
                    dict(category=category, key=key, original=original, expected=translated),
                    dict(category=category, key=key, original="Changed " + current,
                         expected="Changed " + current),
                ])
            # Same punctuation elsewhere must not become a global fuzzy match.
            for category, prefix in [("dialogue", "99999|||ME"), ("ui", "88106|||ME")]:
                rows[category].append((prefix + "|||123", "A’s B", "不应命中"))
                cases.append(dict(category=category, key=prefix + "|||runtime",
                                  original="A\u009ds B", expected="A\u009ds B"))
            # Both candidates match after the known conversion: keep original.
            rows["dialogue"].extend([
                ("88110|||ME|||201", "Ambiguous’s", "甲"),
                ("88110|||ME|||202", "Ambiguous’s", "乙"),
            ])
            cases.append(dict(category="dialogue", key="88110|||ME|||runtime",
                              original="Ambiguous\u009ds", expected="Ambiguous\u009ds"))
            for category, entries in rows.items():
                with (root / (category + ".csv")).open("w", encoding="utf-8", newline="") as handle:
                    csv.writer(handle).writerows(entries)
            (root / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
            (root / "Logging.cs").write_text(
                "namespace BepInEx.Logging { public sealed class ManualLogSource "
                "{ public void LogDebug(object value) {} } }", encoding="utf-8"
            )
            runner = root / "run.ps1"
            runner.write_text(r'''
param([string] $Project, [string] $Root)
$ErrorActionPreference = 'Stop'
Add-Type -Path @((Join-Path $Project 'TranslationManager.cs'),
    (Join-Path $Project 'MissingTextTracker.cs'), (Join-Path $Root 'Logging.cs'))
$tracker = [PsychologHan.MissingTextTracker]::new($null, $null)
$manager = [PsychologHan.TranslationManager]::Load($Root, $tracker)
$cases = Get-Content -LiteralPath (Join-Path $Root 'cases.json') -Raw | ConvertFrom-Json
$results = @(foreach ($case in $cases) {
    $manager.TranslateRuntimeOrOriginal($case.category, $case.key, $case.original)
})
ConvertTo-Json -InputObject $results | Set-Content -LiteralPath (Join-Path $Root 'results.json') -Encoding utf8
''', encoding="utf-8")
            result = subprocess.run(
                [pwsh, "-NoProfile", "-File", str(runner), "-Project", str(PROJECT),
                 "-Root", str(root)], capture_output=True, text=True,
                encoding="utf-8", errors="replace",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            results = json.loads((root / "results.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(len(results), len(cases))
            for case, actual in zip(cases, results):
                with self.subTest(key=case["key"], original=case["original"]):
                    self.assertEqual(actual, case["expected"])


if __name__ == "__main__":
    unittest.main()
