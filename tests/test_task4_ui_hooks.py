from pathlib import Path
import unittest


PROJECT = Path(__file__).resolve().parents[1]


class Task4UiHookTests(unittest.TestCase):
    def test_ui_hooks_target_verified_menu_refresh_points(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn('[HarmonyPatch(typeof(global::GameManager), "Start")]', patches)
        self.assertIn("nameof(global::GameManager.updateMainMenu)", patches)
        self.assertIn('[HarmonyPatch(typeof(global::SettingsButton), "onClick")]', patches)
        self.assertIn('[HarmonyPatch(typeof(global::LoadGameButton), "onClick")]', patches)
        self.assertIn("TryTranslateByOriginal", patches)

    def test_ui_hook_is_not_a_global_tmp_setter(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertNotIn("TMP_Text.text", patches)
        self.assertNotIn("Resources.FindObjectsOfTypeAll", patches)
        self.assertNotIn("Update()", patches)

    def test_approved_menu_labels_are_present(self):
        translations = (PROJECT / "resources" / "work" / "approved-translations" / "ui.csv").read_text(encoding="utf-8-sig")

        self.assertIn("New game,新游戏", translations)
        self.assertIn("Settings, 设置", translations)
        self.assertIn("Continue,继续", translations)
