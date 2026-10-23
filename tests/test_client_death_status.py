"""Exercise the actual display policy without Unity or installed game files."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class ClientDeathStatusTests(unittest.TestCase):
    def test_legacy_deaths_are_visible_only_after_story_disclosure(self):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("PowerShell 7 is required for the C# regression harness")
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Fixture.cs").write_text('''
using System;
public class GameState {
    public bool notifiedDeathVera, notifiedDeathJaden, notifiedDeathJoe;
    public bool notifiedDeathAshley, notifiedDeathDeborah;
    public bool ashleyDied, killedAshley, deborahDied, killedDeborah;
    public int timeCode;
}
public static class Fixture {
    static void Check(GameState state, string client, bool expected) {
        if (PsychologHan.ClientDeathStatus.IsKnownDead(state, client) != expected)
            throw new Exception("Incorrect death display for " + client);
    }
    public static void Run() {
        Check(null, "Ashley", false);
        var state = new GameState { ashleyDied = true, timeCode = 2110 };
        Check(state, "Ashley", false); // death decided, police have not told us
        state.notifiedDeathAshley = true;
        Check(state, "Ashley", true); // the actual notification wins immediately
        state.notifiedDeathAshley = false;
        state.timeCode = 2130;
        Check(state, "Ashley", true); // old save, after the police conversation
        state.ashleyDied = false;
        Check(state, "Ashley", false); // surviving route at the same time
        state.killedAshley = true;
        Check(state, "Ashley", true); // legacy field before game migration
        state.timeCode = 2110;
        Check(state, "Ashley", false);
        state.timeCode = 2240;
        state.deborahDied = true;
        Check(state, "Deborah", true); // 42115 sets death at the disclosure itself
        state.deborahDied = false;
        state.killedDeborah = true;
        Check(state, "Deborah", true);
        state.killedDeborah = false;
        Check(state, "Deborah", false);
        state.notifiedDeathDeborah = true;
        Check(state, "Deborah", true);
        foreach (var client in new[] { "Vera", "Jaden", "Joe" }) {
            Check(state, client, false); // unrelated clients keep notification rule
            typeof(GameState).GetField("notifiedDeath" + client).SetValue(state, true);
            Check(state, client, true);
        }
        Check(state, "Unknown", false);
        if (state.notifiedDeathAshley || state.ashleyDied || state.deborahDied)
            throw new Exception("Display policy mutated story/save state");
    }
}
''', encoding="utf-8")
            runner = root / "run.ps1"
            runner.write_text('''param([string] $Project, [string] $Root)
$ErrorActionPreference = 'Stop'
Add-Type -Path @((Join-Path $Project 'ClientDeathStatus.cs'), (Join-Path $Root 'Fixture.cs'))
[Fixture]::Run()
''', encoding="utf-8")
            result = subprocess.run(
                [pwsh, "-NoProfile", "-File", str(runner), "-Project", str(project),
                 "-Root", str(root)], capture_output=True, text=True,
                encoding="utf-8", errors="replace",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
