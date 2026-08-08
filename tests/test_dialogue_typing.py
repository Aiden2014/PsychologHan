from pathlib import Path
import unittest


PROJECT = Path(__file__).resolve().parents[1]


class DialogueTypingTests(unittest.TestCase):
    def test_original_dialogue_renderer_is_word_based(self):
        source = (PROJECT / "resources" / "Assembly-CSharp-decompiled" / "GameManager.cs").read_text(
            encoding="utf-8-sig"
        )
        start = source.index("public IEnumerator printText(")
        end = source.index("public void slowPrint(", start)
        renderer = source[start:end]

        self.assertIn("textLine.Split(' ')", renderer)
        self.assertIn("string.Join(\" \", words, 0, i)", renderer)

    def test_patch_targets_only_dialogue_slow_print(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn(
            "nameof(global::GameManager.slowPrint),\n        new Type[] { typeof(TextMeshProUGUI), typeof(string), typeof(float), typeof(float) }",
            patches,
        )
        self.assertIn("textObject == gameManager.meText || textObject == gameManager.speakerText", patches)
        self.assertIn("ContainsChineseCharacter(textLine)", patches)
        self.assertIn("PrintChineseDialogue(", patches)
        self.assertIn("return false;", patches)

    def test_chinese_dialogue_is_character_based_and_slightly_faster(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("private const float ChineseDialogueSpeedMultiplier = 1.25f;", patches)
        self.assertIn("float charactersPerSecond = lettersPerSecond * ChineseDialogueSpeedMultiplier;", patches)
        self.assertIn("for (int index = 0; index <= session.TextLine.Length; index++)", patches)
        self.assertIn("session.TextObject.text = session.TextLine.Substring(0, index);", patches)
        self.assertIn("preventInteractionDuringPrintText.SetActive(value: true)", patches)
        self.assertIn("preventInteractionDuringPrintText.SetActive(value: false)", patches)

    def test_english_dialogue_falls_back_to_original_renderer(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        prefix_start = patches.index("private static bool Prefix(")
        prefix_end = patches.index("    }\n\n    private static bool ShouldUseChineseTyping", prefix_start)
        prefix = patches[prefix_start:prefix_end]

        self.assertIn("return true;", prefix)
        self.assertIn("lettersPerSecond <= 0f", prefix)

    def test_hurry_up_click_completes_the_active_chinese_dialogue_directly(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn(
            '[HarmonyPatch(typeof(global::HurryUp), nameof(global::HurryUp.OnClick))]',
            patches,
        )
        self.assertIn("CompleteActiveChineseDialogue", patches)
        self.assertIn("StopCoroutine", patches)
        self.assertIn("activeChineseDialogues", patches)

        click_start = patches.index("private static bool CompleteActiveChineseDialogue")
        click_end = patches.index("private static void CancelActiveChineseDialogue", click_start)
        click_handler = patches[click_start:click_end]
        self.assertLess(
            click_handler.index("session.TextObject.text = session.TextLine"),
            click_handler.index("FinishChineseDialogue(gameManager, session)"),
        )

    def test_new_situation_cancels_the_previous_chinese_coroutine(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        update_prefix_start = patches.index("private static class DynamicSitItemPatch")
        update_prefix_end = patches.index("    }\n\n    [HarmonyPatch", update_prefix_start)
        update_prefix = patches[update_prefix_start:update_prefix_end]

        self.assertIn("CancelActiveChineseDialogue(__instance);", update_prefix)

    def test_skip_button_is_the_verified_original_click_surface(self):
        hurry_up = (PROJECT / "resources" / "Assembly-CSharp-decompiled" / "HurryUp.cs").read_text(
            encoding="utf-8-sig"
        )
        button = (PROJECT / "resources" / "MonoBehaviour" / "Button-level1-36325.json").read_text(
            encoding="utf-8-sig"
        )

        self.assertIn("gM.hurryUp = true;", hurry_up)
        self.assertIn('"m_TargetAssemblyTypeName": "HurryUp, Assembly-CSharp"', button)
        self.assertIn('"m_MethodName": "OnClick"', button)

    def test_skip_click_cannot_advance_to_the_next_option_in_the_same_frame(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn(
            '[HarmonyPatch(typeof(global::OptionItem), nameof(global::OptionItem.toDoWhenClicked))]',
            patches,
        )
        self.assertIn("skipInputConsumedAtFrame", patches)
        self.assertIn("Time.frameCount", patches)
        self.assertIn("ConsumeSkipInputGuard", patches)


if __name__ == "__main__":
    unittest.main()
