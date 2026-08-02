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
        self.assertIn("南西油墨宋.ttf", manager)
        self.assertIn("朝華打字機.ttf", manager)
        self.assertIn("JasonHandwriting1-Regular.ttf", manager)
        self.assertIn("faceInfo.familyName", manager)
        self.assertIn("Typewriter_standard", manager)
        self.assertIn("GochiHand-Regular", manager)
        self.assertIn("textComponent.font =", manager)
        self.assertIn("originalFontByComponent", manager)
        self.assertIn("originalFontByComponent.Clear()", manager)
        self.assertNotIn("TMP_Text.text", manager)
        self.assertNotIn("SetText", manager)
        self.assertNotIn("Update()", manager)

    def test_profile_declares_the_verified_runtime_font_contract(self):
        profile = json.loads((PROJECT / "localization" / "project-profile.json").read_text(encoding="utf-8"))
        fonts = profile["fonts"]

        self.assertEqual(fonts["strategy"], "runtime-ttf")
        self.assertEqual(fonts["source_font"], "resources/fonts/南西油墨宋.ttf")
        self.assertEqual(fonts["plugin_relative_path"], "fonts/南西油墨宋.ttf")
        self.assertEqual(
            fonts["mappings"],
            {
                "Adler": "fonts/南西油墨宋.ttf",
                "Typewriter_standard": "fonts/朝華打字機.ttf",
                "GochiHand-Regular": "fonts/JasonHandwriting1-Regular.ttf",
            },
        )
        self.assertIn("resources/fonts/JasonHandwriting1-Regular.ttf", fonts["mapping_source_fonts"])
        self.assertIn("CreateFontAsset", fonts["runtime_api_evidence"]["tmp_create_font_asset"])

    def test_global_fallback_uses_the_adler_mapped_font(self):
        manager = (PROJECT / "FontFallbackManager.cs").read_text(encoding="utf-8-sig")

        self.assertIn('internal const string FontFileName = "南西油墨宋.ttf";', manager)
        self.assertNotIn('internal const string FontFileName = "汇文明朝体汇文明朝体.ttf";', manager)

    def test_mapped_font_replaces_the_component_material_with_the_mapped_asset_material(self):
        manager = (PROJECT / "FontFallbackManager.cs").read_text(encoding="utf-8-sig")

        self.assertIn("textComponent.fontSharedMaterial = mappedFontAsset.material;", manager)


if __name__ == "__main__":
    unittest.main()
