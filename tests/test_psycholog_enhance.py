from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENHANCE_SOURCE = PROJECT_ROOT / "PsychologEnhance" / "Plugin.cs"
MAIN_PROJECT = PROJECT_ROOT / "PsychologHan.csproj"


class PsychologEnhanceTests(unittest.TestCase):
    def test_score_fix_is_a_narrow_ashley_transpiler(self):
        source = ENHANCE_SOURCE.read_text(encoding="utf-8")

        self.assertIn('[HarmonyPatch(typeof(GameScore), "calculateAndDisplayGameScore")]', source)
        self.assertIn("[HarmonyTranspiler]", source)
        self.assertIn("Math.Abs(value - (1f / 13f))", source)
        self.assertIn("code[index].operand = 2f / 9f", source)
        self.assertIn("new CodeInstruction(OpCodes.Ldc_R4, 6f)", source)
        self.assertIn("new CodeInstruction(OpCodes.Sub)", source)
        self.assertNotIn("[HarmonyPostfix]", source)

    def test_main_project_keeps_child_plugin_out_of_localization_dll(self):
        project = MAIN_PROJECT.read_text(encoding="utf-8")

        self.assertIn('<Compile Remove="PsychologEnhance\\**" />', project)
        self.assertIn('<EmbeddedResource Remove="PsychologEnhance\\**" />', project)
        self.assertIn('<None Remove="PsychologEnhance\\**" />', project)


if __name__ == "__main__":
    unittest.main()
