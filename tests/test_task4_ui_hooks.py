from pathlib import Path
import csv
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

    def test_save_game_info_hook_updates_existing_entries_safely(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("foreach (var cur in new Dictionary<int, string>(__result))", patches)
        self.assertIn("__result[cur.Key] =", patches)
        self.assertNotIn("__result.Add(cur.Key", patches)

    def test_main_menu_hook_scans_the_whole_menu_subtree(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("TranslateScreen(gameManager.mainMenuScreen);", patches)

    def test_game_manager_start_hook_scans_the_in_game_ui_subtree(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("TranslateScreen(gameManager.inGame);", patches)

    def test_session_title_hook_translates_serialized_title_fields(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn(
            '[HarmonyPatch(typeof(global::ClientSessionTitle), nameof(global::ClientSessionTitle.playCutscene))]',
            patches,
        )
        self.assertIn("SessionTitleOwnerPathIds", patches)
        self.assertIn('{ "VeraSession1Title", "37906" }', patches)
        self.assertIn('"level1|||" + ownerPathId + "|||ClientSessionTitle|||" + fieldName', patches)
        self.assertIn("TryTranslate(UiCategory, key, original", patches)
        self.assertIn("__instance.sessionNumberTextStr = __state.SessionNumberText;", patches)

    def test_progress_bar_heading_hook_translates_runtime_titles(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")
        translations = PROJECT / "resources" / "work" / "approved-translations" / "ui.csv"

        self.assertIn(
            '[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.animateUIBar))]',
            patches,
        )
        self.assertIn("ProgressBarHeadingKeyPrefix", patches)
        self.assertIn("TryTranslateProgressBarHeading(heading, out translated)", patches)

        with translations.open(encoding="utf-8-sig", newline="") as handle:
            rows = {
                row[0]: row
                for row in csv.reader(handle)
                if row and row[0] in {
                    "GameManager.cs|||changeProgressionMetric|||heading|||TRUST",
                    "GameManager.cs|||changeProgressionMetric|||heading|||TREATMENT",
                }
            }

        self.assertEqual(rows["GameManager.cs|||changeProgressionMetric|||heading|||TRUST"][2], "信任")
        self.assertEqual(rows["GameManager.cs|||changeProgressionMetric|||heading|||TREATMENT"][2], "治疗")

    def test_verified_duplicate_ui_originals_use_stable_key_locators(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("ApprovedUiKeysByHierarchyPath", patches)
        self.assertIn("TryTranslateApprovedUiText(UiCategory, approvedKey, original", patches)
        self.assertIn(
            "Continue1/Text (TMP)\",\n                \"level1|||32831|||TextMeshProUGUI|||TextMeshProUGUI",
            patches,
        )
        self.assertIn(
            "Continue2/Text (TMP)\",\n                \"level1|||31950|||TextMeshProUGUI|||TextMeshProUGUI",
            patches,
        )
        self.assertIn(
            "Continue3/Text (TMP)\",\n                \"level1|||31499|||TextMeshProUGUI|||TextMeshProUGUI",
            patches,
        )
        self.assertIn("A reviewed locator is authoritative", patches)

    def test_joe_intro_session_labels_use_stable_key_locators(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")
        translations = PROJECT / "resources" / "work" / "approved-translations" / "ui.csv"

        expected = {
            "Canvas/InGame/ClientsSection/WeeklyPlannerSection/WeeklyPlannerSection/WeeklyPlannerStage/WeeklyPlanner/NotesHandwritten/JoeText1": "31168",
            "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/Imagery/Cutscenes/HubForDevelopment/WeeklyPlanner/NotesHandwritten/JoeText1": "31476",
        }
        for path, path_id in expected.items():
            key = f"level1|||{path_id}|||TextMeshProUGUI|||TextMeshProUGUI"
            self.assertIn(path, patches)
            self.assertIn(key, patches)

        with translations.open(encoding="utf-8-sig", newline="") as handle:
            rows = {row[0]: row for row in csv.reader(handle) if row and row[0] in {
                "level1|||31168|||TextMeshProUGUI|||TextMeshProUGUI",
                "level1|||31476|||TextMeshProUGUI|||TextMeshProUGUI",
            }}

        self.assertEqual(len(rows), 2)
        for row in rows.values():
            self.assertEqual(row[1].replace("\r\n", "\n"), "      Joe\nintro session")
            self.assertEqual(row[2].replace("\r\n", "\n"), "      乔\n初次会谈")

    def test_stable_ui_keys_tolerate_unity_line_padding(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")
        runtime_text = '      Joe \nintro session'
        translations = PROJECT / "resources" / "work" / "approved-translations" / "ui.csv"

        with translations.open(encoding="utf-8-sig", newline="") as handle:
            row = next(
                row for row in csv.reader(handle)
                if row and row[0] == "level1|||31168|||TextMeshProUGUI|||TextMeshProUGUI"
            )

        self.assertNotEqual(runtime_text, row[1].replace("\r\n", "\n"))
        self.assertIn("TryTranslateApprovedUiText(UiCategory, approvedKey, original", patches)
        self.assertIn("TrimLineBreakPadding", patches)

    def test_next_day_headers_use_context_specific_stable_key_locators(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")
        cutscene_root = (
            "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/"
            "Imagery/Cutscenes/"
        )
        expected = {
            cutscene_root + "NextDay1415/ToDay": "31494",
            cutscene_root + "NextDay1518/FromDay": "32867",
        }

        for path, path_id in expected.items():
            key = f"level1|||{path_id}|||TextMeshProUGUI|||TextMeshProUGUI"
            self.assertIn(
                f'"{path}",\n                "{key}"',
                patches,
            )

        self.assertEqual(set(expected.values()), {"31494", "32867"})

    def test_intersection_buttons_use_context_specific_stable_key_locators(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        expected_locators = {
            "AToHub": "33304",
            "BToHub": "34192",
            "CToHub": "35034",
        }
        for button_name, path_id in expected_locators.items():
            self.assertIn(
                f"DeborahCarpenterRoad/{button_name}/Text (TMP)",
                patches,
            )
            self.assertIn(
                f"level1|||{path_id}|||TextMeshProUGUI|||TextMeshProUGUI",
                patches,
            )

    def test_hideout_facade_uses_the_multiline_ui_key(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn(
            "Killer/HideoutFacade/Text (TMP)",
            patches,
        )
        self.assertIn(
            "level1|||33364|||TextMeshProUGUI|||TextMeshProUGUI",
            patches,
        )

        translations = PROJECT / "resources" / "work" / "approved-translations" / "ui.csv"
        with translations.open(encoding="utf-8-sig", newline="") as handle:
            row = next(row for row in csv.reader(handle) if row and row[0] == "level1|||33364|||TextMeshProUGUI|||TextMeshProUGUI")

        self.assertEqual(row[1], "SUSPECT'S \nHIDEOUT")
        self.assertEqual(row[2], "嫌疑人的\n藏身处")

    def test_suspect_sofa_label_uses_a_chinese_translation_and_stable_key(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")
        translations = PROJECT / "resources" / "work" / "approved-translations" / "ui.csv"

        self.assertIn("Killer/SuspectSittingInSofa/Text (TMP)", patches)
        self.assertIn("level1|||33772|||TextMeshProUGUI|||TextMeshProUGUI", patches)

        with translations.open(encoding="utf-8-sig", newline="") as handle:
            row = next(row for row in csv.reader(handle) if row and row[0] == "level1|||33772|||TextMeshProUGUI|||TextMeshProUGUI")

        self.assertEqual(row[1], "SUSPECT")
        self.assertEqual(row[2], "嫌疑人")

    def test_exit_to_main_menu_buttons_use_context_specific_stable_keys(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")
        translations = PROJECT / "resources" / "work" / "approved-translations" / "ui.csv"

        expected = {
            "DifficultySetting/ReturnToTitleButton": ("31612", "退出至主菜单"),
            "GameResult/ReturnToTitleButton": ("34132", "退出到主菜单"),
        }
        for path, (path_id, translation) in expected.items():
            self.assertIn(path + "/Text (TMP)", patches)
            self.assertIn(
                f"level1|||{path_id}|||TextMeshProUGUI|||TextMeshProUGUI",
                patches,
            )

            with translations.open(encoding="utf-8-sig", newline="") as handle:
                row = next(
                    row for row in csv.reader(handle)
                    if row and row[0] == f"level1|||{path_id}|||TextMeshProUGUI|||TextMeshProUGUI"
                )
            self.assertEqual(row[1], "EXIT TO MAIN MENU")
            self.assertEqual(row[2], translation)

    def test_ui_hook_is_not_a_global_tmp_setter(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertNotIn("TMP_Text.text", patches)
        self.assertNotIn("Resources.FindObjectsOfTypeAll", patches)
        self.assertNotIn("Update()", patches)

    def test_dialogue_font_mapping_targets_the_verified_dialogue_components(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("ApplyFontMappings(__instance.meText);", patches)
        self.assertIn("ApplyFontMappings(__instance.speakerText);", patches)
        self.assertNotIn("ApplyFontMappings(__instance.storyScreen);", patches)

    def test_screen_refreshes_reuse_cached_tmp_components(self):
        patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("ScreenTextCaches", patches)
        self.assertIn("GetScreenTexts(screen)", patches)
        self.assertIn("GetScreenTexts(notesSection)", patches)

    def test_client_refresh_does_not_rescan_the_entire_in_game_root(self):
        game_patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")
        client_refresh_start = game_patches.index("private static class UpdateClientsSectionPatch")
        client_refresh_end = game_patches.index("    [HarmonyPatch", client_refresh_start + 20)
        client_refresh = game_patches[client_refresh_start:client_refresh_end]

        self.assertNotIn("UiPatches.TranslateScreen(__instance.inGame);", client_refresh)

    def test_client_details_refresh_scans_the_verified_details_section(self):
        game_patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("UiPatches.TranslateScreen(__instance.detailsSection);", game_patches)

    def test_weekly_planner_refresh_scans_notes_and_handwritten_components(self):
        game_patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")
        ui_patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("UiPatches.TranslateClientWeeklyPlanner(__instance.notesSection);", game_patches)
        self.assertIn("NotesHandwritten/", ui_patches)
        self.assertIn("AshleyText2", ui_patches)
        self.assertIn("new Color(0f, 0f, 0f, textComponent.color.a)", ui_patches)
        self.assertIn("<size=80%>", ui_patches)

    def test_weekly_planner_morning_translation_is_not_ambiguous(self):
        translations = PROJECT / "resources" / "work" / "approved-translations" / "ui.csv"
        values = set()
        with translations.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                if len(row) == 3 and row[1] == "Morning":
                    values.add(row[2])

        self.assertEqual(values, {"上午"})

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
        self.assertIn("if (!OriginalsMatch(entry.Original, original))", manager)
        self.assertIn("RuntimeOriginalsMatch(category, runtimeKey, candidate.Original, original)", manager)
        self.assertIn("normalizedOriginalsByCategory", manager)
        fallback = manager[manager.index("public bool TryTranslateByOriginal"):manager.index("private void LoadCsv")]
        self.assertLess(
            fallback.index("ambiguousNormalizedOriginals.Contains(normalizedOriginal)"),
            fallback.index("originals.TryGetValue(original"),
        )
