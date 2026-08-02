from pathlib import Path
import json
import unittest


PROJECT = Path(__file__).resolve().parents[1]


class FontFallbackContractTests(unittest.TestCase):
    def test_plugin_owns_a_targeted_runtime_tmp_fallback_lifecycle(self):
        plugin = (PROJECT / "Plugin.cs").read_text(encoding="utf-8-sig")
        manager = (PROJECT / "FontFallbackManager.cs").read_text(encoding="utf-8-sig")

        self.assertIn("FontFallbackManager", plugin)
        self.assertIn("new Font(fontPath)", manager)
        self.assertIn("TMP_FontAsset.CreateFontAsset", manager)
        self.assertIn("TMP_Settings.fallbackFontAssets", manager)
        self.assertIn("Object.Destroy", manager)

    def test_font_is_plugin_local_and_not_a_global_text_hook(self):
        manager = (PROJECT / "FontFallbackManager.cs").read_text(encoding="utf-8-sig")

        self.assertIn('Path.Combine(pluginDirectory, FontDirectoryName, FontFileName)', manager)
        self.assertNotIn("TMP_Text.text", manager)
        self.assertNotIn("SetText", manager)
        self.assertNotIn("Update()", manager)

    def test_profile_declares_the_verified_runtime_font_contract(self):
        profile = json.loads((PROJECT / "localization" / "project-profile.json").read_text(encoding="utf-8"))
        fonts = profile["fonts"]

        self.assertEqual(fonts["strategy"], "runtime-ttf")
        self.assertEqual(fonts["plugin_relative_path"], "fonts/汇文明朝体汇文明朝体.ttf")
        self.assertIn("CreateFontAsset", fonts["runtime_api_evidence"]["tmp_create_font_asset"])


if __name__ == "__main__":
    unittest.main()
