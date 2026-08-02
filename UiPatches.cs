using HarmonyLib;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using System.Globalization;

namespace PsychologHan;

internal static class UiPatches
{
    private const string UiCategory = "ui";

    [HarmonyPatch(typeof(global::GameManager), "Start")]
    private static class GameManagerStartPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::GameManager __instance)
        {
            TranslateMainMenu(__instance);
        }
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateMainMenu))]
    private static class UpdateMainMenuPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::GameManager __instance)
        {
            TranslateMainMenu(__instance);
        }
    }

    [HarmonyPatch(typeof(global::SettingsButton), "onClick")]
    private static class SettingsButtonPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::SettingsButton __instance)
        {
            TranslateScreen(__instance.settingsScreen);
        }
    }

    [HarmonyPatch(typeof(global::LoadGameButton), "onClick")]
    private static class LoadGameButtonPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::LoadGameButton __instance)
        {
            TranslateScreen(__instance.loadGameScreen);
        }
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateSituationView))]
    private static class UpdateSituationViewPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::GameManager __instance)
        {
            TranslateChoiceButtons(__instance);
            if (__instance == null)
            {
                return;
            }

            ApplyFontMappings(__instance.meText);
            ApplyFontMappings(__instance.speakerText);
            ApplyFontMappings(__instance.storyScreen);
        }
    }

    private static void TranslateChoiceButtons(global::GameManager gameManager)
    {
        if (gameManager == null || Plugin.Translations == null || gameManager.gS == null ||
            gameManager.optionButtonTexts == null || gameManager.sitItems == null || gameManager.optionItems == null)
        {
            return;
        }

        global::SitItem sitItem;
        if (!gameManager.sitItems.TryGetValue(gameManager.gS.currentSitItem, out sitItem) ||
            sitItem == null || sitItem.optionItems == null)
        {
            return;
        }

        for (int index = 0; index < sitItem.optionItems.Count && index < gameManager.optionButtonTexts.Count; index++)
        {
            long optionId = sitItem.optionItems[index];
            global::OptionItem optionItem;
            if (!gameManager.optionItems.TryGetValue(optionId, out optionItem) || optionItem == null)
            {
                continue;
            }

            TextMeshProUGUI textComponent = gameManager.optionButtonTexts[index];
            if (textComponent == null)
            {
                continue;
            }

            string original = optionItem.text;
            string choiceKey = ChoiceKey(gameManager.gS.currentSitItem, optionId);
            string translated = Plugin.Translations.TranslateRuntimeOrOriginal("choice", choiceKey, original);
            if (!string.Equals(textComponent.text, translated, System.StringComparison.Ordinal))
            {
                textComponent.text = translated;
            }

            if (Plugin.Fonts != null)
            {
                Plugin.Fonts.TryApplyMapping(textComponent);
            }
        }
    }

    private static string ChoiceKey(int fromId, long optionId)
    {
        string from = fromId == 0 ? "None" : fromId.ToString(CultureInfo.InvariantCulture);
        string option = optionId.ToString(CultureInfo.InvariantCulture);
        return from + "|||" + option + "|||" + option;
    }

    private static void TranslateMainMenu(global::GameManager gameManager)
    {
        if (gameManager == null)
        {
            return;
        }

        // The main menu has visible label objects (for example ContinueText)
        // alongside the button's own Text (TMP) child. Scan the verified menu
        // root so both representations are translated, including inactive UI.
        TranslateScreen(gameManager.mainMenuScreen);
        TranslateText(gameManager.continueButtonText);
        TranslateText(gameManager.newGameButtonText);
        TranslateText(gameManager.loadButtonText);
        TranslateButton(gameManager.settingsButton);
        TranslateButton(gameManager.quitButton);
    }

    private static void TranslateButton(Button button)
    {
        if (button == null)
        {
            return;
        }

        TranslateScreen(button.gameObject);
    }

    private static void TranslateScreen(GameObject screen)
    {
        if (screen == null)
        {
            return;
        }

        TextMeshProUGUI[] texts = screen.GetComponentsInChildren<TextMeshProUGUI>(includeInactive: true);
        for (int index = 0; index < texts.Length; index++)
        {
            TranslateText(texts[index]);
        }
    }

    private static void TranslateText(TextMeshProUGUI textComponent)
    {
        if (textComponent == null || Plugin.Translations == null)
        {
            return;
        }

        string original = textComponent.text;
        if (Plugin.Fonts != null)
        {
            Plugin.Fonts.TryApplyMapping(textComponent);
        }

        string translated;
        if (string.IsNullOrEmpty(original) ||
            !Plugin.Translations.TryTranslateByOriginal(UiCategory, original, out translated) ||
            string.Equals(original, translated, System.StringComparison.Ordinal))
        {
            return;
        }

        textComponent.text = translated;
    }

    private static void ApplyFontMappings(GameObject screen)
    {
        if (screen == null || Plugin.Fonts == null)
        {
            return;
        }

        TextMeshProUGUI[] texts = screen.GetComponentsInChildren<TextMeshProUGUI>(includeInactive: true);
        for (int index = 0; index < texts.Length; index++)
        {
            Plugin.Fonts.TryApplyMapping(texts[index]);
        }
    }

    private static void ApplyFontMappings(TextMeshProUGUI textComponent)
    {
        if (textComponent != null && Plugin.Fonts != null)
        {
            Plugin.Fonts.TryApplyMapping(textComponent);
        }
    }
}
