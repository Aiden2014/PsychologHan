using System;
using System.Collections.Generic;
using HarmonyLib;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using System.Globalization;

namespace PsychologHan;

internal static class UiPatches
{
    private const string UiCategory = "ui";
    private const string HandwrittenSizeTag = "<size=80%>";

    // These locators are reviewed against the level1 AssetStudio export and the
    // runtime SceneScan hierarchy. The runtime object does not expose Unity's
    // serialized PathID, so the approved hierarchy path supplies the stable-key
    // bridge for duplicate UI originals.
    private static readonly Dictionary<string, string> ApprovedUiKeysByHierarchyPath =
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/Ashley/Continue1/Text (TMP)",
                "level1|||32831|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/Ashley/Continue2/Text (TMP)",
                "level1|||31950|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/Ashley/Continue3/Text (TMP)",
                "level1|||31499|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/DeborahCarpenterRoad/AToHub/Text (TMP)",
                "level1|||33304|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/DeborahCarpenterRoad/BToHub/Text (TMP)",
                "level1|||34192|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/DeborahCarpenterRoad/CToHub/Text (TMP)",
                "level1|||35034|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/Killer/HideoutFacade/Text (TMP)",
                "level1|||33364|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/AllPacButtons/Killer/SuspectSittingInSofa/Text (TMP)",
                "level1|||33772|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/Imagery/Cutscenes/DifficultySetting/ReturnToTitleButton/Text (TMP)",
                "level1|||31612|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/Imagery/Cutscenes/GameResult/ReturnToTitleButton/Text (TMP)",
                "level1|||34132|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/Imagery/Cutscenes/NextDay1415/ToDay",
                "level1|||31494|||TextMeshProUGUI|||TextMeshProUGUI"
            },
            {
                "Canvas/InGame/MainGameScreen/CursorResponseLayer/Stage/LayerForZooming/Imagery/Cutscenes/NextDay1518/FromDay",
                "level1|||32867|||TextMeshProUGUI|||TextMeshProUGUI"
            }
        };

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
        TranslateScreen(gameManager.inGame);
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

    internal static void TranslateScreen(GameObject screen)
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

    internal static void TranslateClientWeeklyPlanner(GameObject notesSection)
    {
        if (notesSection == null)
        {
            return;
        }

        TranslateScreen(notesSection);
        TextMeshProUGUI[] texts = notesSection.GetComponentsInChildren<TextMeshProUGUI>(includeInactive: true);
        for (int index = 0; index < texts.Length; index++)
        {
            TranslateHandwrittenPlannerText(texts[index]);
        }
    }

    private static void TranslateHandwrittenPlannerText(TextMeshProUGUI textComponent)
    {
        if (textComponent == null ||
            GetHierarchyPath(textComponent).IndexOf("/NotesHandwritten/", System.StringComparison.Ordinal) < 0)
        {
            return;
        }

        string translated = ReplacePlannerNameFragments(textComponent.name, textComponent.text);
        if (!string.Equals(textComponent.text, translated, System.StringComparison.Ordinal))
        {
            textComponent.text = translated;
        }

        if (Plugin.Fonts != null)
        {
            Plugin.Fonts.TryApplyMapping(textComponent);
        }

        if (textComponent.font != null && !string.IsNullOrEmpty(textComponent.font.name) &&
            textComponent.font.name.StartsWith("PsychologHan JasonHandwriting1", System.StringComparison.OrdinalIgnoreCase))
        {
            textComponent.color = new Color(0f, 0f, 0f, textComponent.color.a);
            ApplyHandwrittenSize(textComponent);
        }
    }

    private static void ApplyHandwrittenSize(TextMeshProUGUI textComponent)
    {
        if (string.IsNullOrEmpty(textComponent.text) ||
            textComponent.text.IndexOf("<size=", System.StringComparison.OrdinalIgnoreCase) >= 0)
        {
            return;
        }

        textComponent.text = HandwrittenSizeTag + textComponent.text + "</size>";
    }

    private static string ReplacePlannerNameFragments(string componentName, string value)
    {
        if (componentName == "AshleyText2" && value == "Ashl")
        {
            return "阿什";
        }

        if (componentName == "AshleyText2_ey" && value == "ey")
        {
            return "莉";
        }

        if (componentName == "AshleyText3" && value == "As")
        {
            return "阿";
        }

        if (componentName == "AshleyText3_hley" && value == "hley")
        {
            return "什莉";
        }

        if (componentName == "Deborah2" && value == "bora")
        {
            return "";
        }

        if (componentName == "Deborah2 (1)" && value == "De")
        {
            return "";
        }

        if (componentName == "Deborah2 (2)" && value == "h")
        {
            return "黛博拉";
        }

        if (componentName == "Deborah3" && value == "Debo")
        {
            return "黛博";
        }

        if (componentName == "Deborah3 (1)" && value == "rah")
        {
            return "拉";
        }

        if (componentName == "JoeText2" && value != null && value.EndsWith("Jo", System.StringComparison.Ordinal))
        {
            return value.Substring(0, value.Length - 2) + "乔";
        }

        if (componentName == "JoeText2_e" && value == "e")
        {
            return string.Empty;
        }

        if (componentName == "JoeText3" && value == "J oe")
        {
            return "乔";
        }

        return ReplacePlannerNames(value);
    }

    private static string ReplacePlannerNames(string value)
    {
        return value
            .Replace("Ashley", "阿什莉")
            .Replace("Deborah", "黛博拉")
            .Replace("Jaden", "杰登")
            .Replace("Joe", "乔")
            .Replace("Vera", "薇拉");
    }

    private static string GetHierarchyPath(TextMeshProUGUI textComponent)
    {
        string path = textComponent.name;
        Transform current = textComponent.transform.parent;
        while (current != null)
        {
            path = current.name + "/" + path;
            current = current.parent;
        }

        return path;
    }

    private static void TranslateText(TextMeshProUGUI textComponent)
    {
        if (textComponent == null)
        {
            return;
        }

        string original = textComponent.text;

        if (Plugin.Translations == null)
        {
            return;
        }

        if (Plugin.Fonts != null)
        {
            Plugin.Fonts.TryApplyMapping(textComponent);
        }

        string approvedKey;
        if (ApprovedUiKeysByHierarchyPath.TryGetValue(GetHierarchyPath(textComponent), out approvedKey))
        {
            string keyTranslated;
            if (Plugin.Translations.TryTranslate(UiCategory, approvedKey, original, out keyTranslated) &&
                !string.Equals(original, keyTranslated, System.StringComparison.Ordinal))
            {
                textComponent.text = keyTranslated;
            }

            // A reviewed locator is authoritative. Do not fall back to another
            // translation for the same original when the key's source changed.
            return;
        }

        string translated = null;
        bool matched = !string.IsNullOrEmpty(original) &&
            Plugin.Translations.TryTranslateByOriginal(UiCategory, original, out translated);

        if (!matched || string.Equals(original, translated, System.StringComparison.Ordinal))
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
