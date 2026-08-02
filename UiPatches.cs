using HarmonyLib;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

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

    private static void TranslateMainMenu(global::GameManager gameManager)
    {
        if (gameManager == null)
        {
            return;
        }

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
        string translated;
        if (string.IsNullOrEmpty(original) ||
            !Plugin.Translations.TryTranslateByOriginal(UiCategory, original, out translated) ||
            string.Equals(original, translated, System.StringComparison.Ordinal))
        {
            return;
        }

        textComponent.text = translated;
    }
}
