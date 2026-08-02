from pathlib import Path
import unittest


PROJECT = Path(__file__).resolve().parents[1]


class SceneScannerTests(unittest.TestCase):
    def test_plugin_exposes_a_configurable_scan_hotkey(self):
        plugin = (PROJECT / "Plugin.cs").read_text(encoding="utf-8-sig")

        self.assertIn("ConfigEntry<KeyboardShortcut>", plugin)
        self.assertIn("ScanCurrentSceneHotkey", plugin)
        self.assertIn("scanCurrentSceneHotkey.Value.IsDown()", plugin)
        self.assertIn("SceneTextScanner.LogCurrentScene", plugin)

    def test_scanner_only_reads_current_scene_tmp_components(self):
        scanner = (PROJECT / "SceneTextScanner.cs").read_text(encoding="utf-8-sig")

        self.assertIn("SceneManager.GetActiveScene()", scanner)
        self.assertIn("FindObjectsOfType<TMP_Text>(true)", scanner)
        self.assertIn("GetHierarchyPath", scanner)
        self.assertNotIn("Resources.FindObjectsOfTypeAll", scanner)
        self.assertNotIn(".text =", scanner)


if __name__ == "__main__":
    unittest.main()
