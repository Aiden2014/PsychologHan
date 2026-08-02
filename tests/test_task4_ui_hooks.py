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

    def test_main_menu_hook_scans_the_whole_menu_subtree(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("TranslateScreen(gameManager.mainMenuScreen);", patches)

    def test_game_manager_start_hook_scans_the_in_game_ui_subtree(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("TranslateScreen(gameManager.inGame);", patches)

    def test_ui_hook_is_not_a_global_tmp_setter(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertNotIn("TMP_Text.text", patches)
        self.assertNotIn("Resources.FindObjectsOfTypeAll", patches)
        self.assertNotIn("Update()", patches)

    def test_dialogue_font_mapping_targets_the_verified_dialogue_components(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("ApplyFontMappings(__instance.meText);", patches)
        self.assertIn("ApplyFontMappings(__instance.speakerText);", patches)

    def test_client_details_refresh_scans_the_verified_details_section(self):
        game_patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("UiPatches.TranslateScreen(__instance.detailsSection);", game_patches)

    def test_client_details_debug_instrumentation_is_removed_after_validation(self):
        game_patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")
        ui_patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertNotIn("DEBUG-CLIENTDETAILS", game_patches)
        self.assertNotIn("DEBUG-CLIENTDETAILS", ui_patches)

    def test_approved_menu_labels_are_present(self):
        translations = (PROJECT / "resources" / "work" / "approved-translations" / "ui.csv").read_text(encoding="utf-8-sig")

        self.assertIn("New game,新游戏", translations)
        self.assertIn("Settings, 设置", translations)
        self.assertIn("Continue,继续", translations)

    def test_translation_manager_normalizes_multiline_ui_newlines(self):
        manager = (PROJECT / "TranslationManager.cs").read_text(encoding="utf-8-sig")

        self.assertIn("NormalizeNewlines", manager)
        self.assertIn("normalizedOriginalsByCategory", manager)
