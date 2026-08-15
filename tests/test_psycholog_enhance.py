from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENHANCE_SOURCE = PROJECT_ROOT / "PsychologEnhance" / "Plugin.cs"
MAIN_PROJECT = PROJECT_ROOT / "PsychologHan.csproj"


class PsychologEnhanceTests(unittest.TestCase):
    def test_corrected_ashley_segment_restores_the_100_point_maximum(self):
        first_four_maximum = 4 * 20
        original_ashley_maximum = 14 + 54 / 13
        corrected_ashley_maximum = 14 + 2 / 9 * 54 - 6

        self.assertEqual(int(first_four_maximum + original_ashley_maximum), 98)
        self.assertEqual(int(first_four_maximum + corrected_ashley_maximum), 100)

    def test_score_fix_uses_a_regular_prefix(self):
        source = ENHANCE_SOURCE.read_text(encoding="utf-8")

        self.assertIn('[HarmonyPatch(typeof(GameScore), "calculateAndDisplayGameScore")]', source)
        self.assertIn("[HarmonyPrefix]", source)
        self.assertIn("private static bool Prefix(GameScore __instance)", source)
        self.assertIn("2f / 9f * Clamp(state.treatmentAshley, 27f, 54f) - 6f", source)
        self.assertNotIn("HarmonyTranspiler", source)

    def test_prefix_is_limited_to_the_verified_game_build(self):
        source = ENHANCE_SOURCE.read_text(encoding="utf-8")

        self.assertIn("if (!IsSupportedGameBuild())", source)
        self.assertIn(
            "B0078981C2A42C8123D53E1CACFDA9F222B415565A3241175EA18E0B7DCF5F91",
            source,
        )

    def test_main_project_keeps_child_plugin_out_of_localization_dll(self):
        project = MAIN_PROJECT.read_text(encoding="utf-8")

        self.assertIn('<Compile Remove="PsychologEnhance\\**" />', project)
        self.assertNotIn('<Compile Include="PsychologEnhance\\Plugin.cs" />', project)
        self.assertIn('<EmbeddedResource Remove="PsychologEnhance\\**" />', project)
        self.assertIn('<None Remove="PsychologEnhance\\**" />', project)


if __name__ == "__main__":
    unittest.main()
