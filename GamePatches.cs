using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using HarmonyLib;
using TMPro;
using UnityEngine;

namespace PsychologHan;

internal static class GamePatches
{
    private const string DialogueCategory = "dialogue";
    private const string CharacterNameCategory = "character_name";
    private const string ItemCategory = "item";
    private const string ClientInfoCategory = "client_info";
    private const string EndingCategory = "ending";
    private const int DynamicHomeworkNodeId = 15700;
    private const string DynamicHomeworkItemKey = "15700|||5290";
    private const string DynamicHomeworkExpression = "((gS.homeworkFloor == 3) ? \"third\" : \"fifth\")";
    private const int DynamicJoshNodeId = 19340;
    private const string DynamicJoshSpeaker = "JOSH";
    private const int DynamicDeborahNodeId = 2820;
    private const string DynamicDeborahPlaceholder = "[DECIDE DYNAMICALLY]";
    private const float ChineseDialogueSpeedMultiplier = 1.25f;
    private static readonly Dictionary<global::GameManager, ChineseDialogueSession> activeChineseDialogues =
        new Dictionary<global::GameManager, ChineseDialogueSession>();

    private sealed class ChineseDialogueSession
    {
        public ChineseDialogueSession(TextMeshProUGUI textObject, string textLine)
        {
            TextObject = textObject;
            TextLine = textLine;
        }

        public TextMeshProUGUI TextObject { get; }

        public string TextLine { get; }

        public Coroutine Coroutine { get; set; }
    }

    [HarmonyPatch(
        typeof(global::GameManager),
        nameof(global::GameManager.slowPrint),
        new Type[] { typeof(TextMeshProUGUI), typeof(string), typeof(float), typeof(float) })]
    private static class ChineseDialogueTypingPatch
    {
        [HarmonyPrefix]
        private static bool Prefix(
            global::GameManager __instance,
            TextMeshProUGUI textObject,
            string textLine,
            float lettersPerSecond,
            float delay)
        {
            if (!ShouldUseChineseTyping(__instance, textObject, textLine) || lettersPerSecond <= 0f)
            {
                return true;
            }

            CancelActiveChineseDialogue(__instance);
            float charactersPerSecond = lettersPerSecond * ChineseDialogueSpeedMultiplier;
            ChineseDialogueSession session = new ChineseDialogueSession(textObject, textLine);
            activeChineseDialogues[__instance] = session;
            session.Coroutine = __instance.StartCoroutine(PrintChineseDialogue(
                __instance,
                session,
                charactersPerSecond,
                delay));
            return false;
        }
    }

    [HarmonyPatch(typeof(global::HurryUp), nameof(global::HurryUp.OnClick))]
    private static class HurryUpPatch
    {
        [HarmonyPrefix]
        private static bool Prefix(global::HurryUp __instance)
        {
            if (__instance == null || __instance.gM == null)
            {
                return true;
            }

            return !CompleteActiveChineseDialogue(__instance.gM);
        }
    }

    private static bool ShouldUseChineseTyping(
        global::GameManager gameManager,
        TextMeshProUGUI textObject,
        string textLine)
    {
        return gameManager != null &&
            textObject != null &&
            (textObject == gameManager.meText || textObject == gameManager.speakerText) &&
            ContainsChineseCharacter(textLine);
    }

    private static bool ContainsChineseCharacter(string text)
    {
        if (string.IsNullOrEmpty(text))
        {
            return false;
        }

        for (int index = 0; index < text.Length; index++)
        {
            char character = text[index];
            if ((character >= '\u3400' && character <= '\u4DBF') ||
                (character >= '\u4E00' && character <= '\u9FFF') ||
                (character >= '\uF900' && character <= '\uFAFF'))
            {
                return true;
            }
        }

        return false;
    }

    private static IEnumerator PrintChineseDialogue(
        global::GameManager gameManager,
        ChineseDialogueSession session,
        float charactersPerSecond,
        float delay)
    {
        yield return new WaitForSeconds(delay);

        float timeBetweenCharacters = 1f / charactersPerSecond;
        if (gameManager.preventInteractionDuringPrintText != null)
        {
            gameManager.preventInteractionDuringPrintText.SetActive(value: true);
        }

        if (gameManager.pulsingMarker != null)
        {
            gameManager.pulsingMarker.SetActive(value: false);
        }

        for (int index = 0; index <= session.TextLine.Length; index++)
        {
            session.TextObject.text = session.TextLine.Substring(0, index);
            if (gameManager.hurryUp)
            {
                timeBetweenCharacters = 0.001f;
            }

            yield return new WaitForSeconds(timeBetweenCharacters);
        }

        FinishChineseDialogue(gameManager, session);
    }

    private static bool CompleteActiveChineseDialogue(global::GameManager gameManager)
    {
        ChineseDialogueSession session;
        if (!activeChineseDialogues.TryGetValue(gameManager, out session) || session == null)
        {
            return false;
        }

        if (session.Coroutine != null)
        {
            gameManager.StopCoroutine(session.Coroutine);
        }

        session.TextObject.text = session.TextLine;
        FinishChineseDialogue(gameManager, session);
        return true;
    }

    private static void CancelActiveChineseDialogue(global::GameManager gameManager)
    {
        if (gameManager == null)
        {
            return;
        }

        ChineseDialogueSession session;
        if (!activeChineseDialogues.TryGetValue(gameManager, out session) || session == null)
        {
            return;
        }

        if (session.Coroutine != null)
        {
            gameManager.StopCoroutine(session.Coroutine);
        }

        activeChineseDialogues.Remove(gameManager);
        gameManager.hurryUp = false;
        if (gameManager.preventInteractionDuringPrintText != null)
        {
            gameManager.preventInteractionDuringPrintText.SetActive(value: false);
        }
    }

    private static void FinishChineseDialogue(
        global::GameManager gameManager,
        ChineseDialogueSession session)
    {
        ChineseDialogueSession activeSession;
        if (activeChineseDialogues.TryGetValue(gameManager, out activeSession) &&
            object.ReferenceEquals(activeSession, session))
        {
            activeChineseDialogues.Remove(gameManager);
        }

        gameManager.hurryUp = false;
        if (gameManager.gS != null && gameManager.sitItems != null)
        {
            global::SitItem currentSitItem;
            if (gameManager.sitItems.TryGetValue(gameManager.gS.currentSitItem, out currentSitItem) &&
                currentSitItem != null &&
                (currentSitItem.sitType == "me" || currentSitItem.sitType == "speaker") &&
                gameManager.pulsingMarker != null)
            {
                gameManager.pulsingMarker.SetActive(value: true);
            }
        }

        if (gameManager.preventInteractionDuringPrintText != null)
        {
            gameManager.preventInteractionDuringPrintText.SetActive(value: false);
        }
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addMe), new Type[] { typeof(int), typeof(string), typeof(int), typeof(Action) })]
    private static class AddMePatch
    {
        [HarmonyPrefix]
        private static void Prefix(int id, ref string text)
        {
            string dialogueKey = DialogueKey(id, "ME");
            text = TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory, dialogueKey, text, ItemCategory);
        }
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addSpeaker), new Type[] { typeof(int), typeof(string), typeof(string), typeof(int), typeof(Action), typeof(string) })]
    private static class AddSpeakerPatch
    {
        [HarmonyPrefix]
        private static void Prefix(int id, ref string speakerName, ref string text)
        {
            string originalSpeakerName = speakerName;
            string dialogueKey = DialogueKey(id, originalSpeakerName);
            if (!IsDynamicPlaceholder(id, text))
            {
                text = TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory, dialogueKey, text, ItemCategory);
            }

            if (!string.Equals(originalSpeakerName, "(ME)", StringComparison.Ordinal))
            {
                speakerName = TranslateDirectOrOriginal(CharacterNameCategory, originalSpeakerName, originalSpeakerName);
            }
        }
    }

    private static bool IsDynamicPlaceholder(int nodeId, string text)
    {
        return (nodeId == DynamicHomeworkNodeId &&
                string.Equals(text, "[DYNAMICALLY]", StringComparison.Ordinal)) ||
            (nodeId == DynamicDeborahNodeId &&
                string.Equals(text, DynamicDeborahPlaceholder, StringComparison.Ordinal));
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateSituationView))]
    private static class DynamicSitItemPatch
    {
        [HarmonyPrefix]
        private static void Prefix(global::GameManager __instance)
        {
            CancelActiveChineseDialogue(__instance);
            TranslateDynamicHomeworkText(__instance);
            TranslateDynamicJoshText(__instance);
            TranslateDynamicDeborahText(__instance);
        }
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateClientsSection))]
    private static class UpdateClientsSectionPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::GameManager __instance)
        {
            if (__instance == null)
            {
                return;
            }

            if (string.Equals(__instance.currentlyDisplayedClientInfoType, "details", StringComparison.Ordinal))
            {
                if (__instance.detailsSection != null)
                {
                    UiPatches.TranslateScreen(__instance.detailsSection);
                }
            }

            UiPatches.TranslateScreen(__instance.inGame);
            UiPatches.TranslateClientWeeklyPlanner(__instance.notesSection);

            string suffix;
            if (!TryGetClientSuffix(__instance.clientCurrentlyChosen, out suffix))
            {
                return;
            }

            TranslateTextComponent(__instance.trustComment, ClientInfoCategory, "trustComment" + suffix);
            TranslateTextComponent(__instance.treatmentComment, ClientInfoCategory, "treatmentComment" + suffix);
        }
    }

    [HarmonyPatch(typeof(global::DeathRunes), "setRunes")]
    private static class DeathRunesSetRunesPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::DeathRunes __instance)
        {
            TranslateTextComponent(__instance.runeVera, EndingCategory, "runeVera");
            TranslateTextComponent(__instance.runeJaden, EndingCategory, "runeJaden");
            TranslateTextComponent(__instance.runeJoe, EndingCategory, "runeJoe");
            TranslateTextComponent(__instance.runeDeborah, EndingCategory, "runeDeborah");
            TranslateTextComponent(__instance.runeAshley, EndingCategory, "runeAshley");
        }
    }

    private static string DialogueKey(int nodeId, string speaker)
    {
        string node = nodeId.ToString(CultureInfo.InvariantCulture);
        return node + "|||" + speaker + "|||" + node;
    }

    private static string TranslateDirectOrOriginal(string category, string key, string original)
    {
        if (Plugin.Translations == null)
        {
            return original;
        }

        return Plugin.Translations.TranslateOrOriginal(category, key, original);
    }

    private static string TranslateWithCategoryOriginalFallback(string category, string key, string original)
    {
        if (Plugin.Translations == null)
        {
            return original;
        }

        string translated;
        if (Plugin.Translations.TryTranslate(category, key, original, out translated))
        {
            return translated;
        }

        if (Plugin.Translations.TryTranslateByOriginal(category, original, out translated))
        {
            return translated;
        }

        return Plugin.Translations.TranslateOrOriginal(category, key, original);
    }

    private static string TranslateRuntimeKeyWithOptionalOriginalFallback(string category, string key, string original, string fallbackCategory)
    {
        if (Plugin.Translations == null)
        {
            return original;
        }

        string translated;
        if (Plugin.Translations.TryTranslateRuntimeKey(category, key, original, out translated))
        {
            return translated;
        }

        if (Plugin.Translations.TryTranslateByOriginal(fallbackCategory, original, out translated))
        {
            return translated;
        }

        return Plugin.Translations.TranslateRuntimeOrOriginal(category, key, original);
    }

    private static void TranslateDynamicHomeworkText(global::GameManager gameManager)
    {
        if (gameManager == null || Plugin.Translations == null || gameManager.gS == null ||
            gameManager.sitItems == null || gameManager.gS.currentSitItem != DynamicHomeworkNodeId)
        {
            return;
        }

        global::SitItem sitItem;
        if (!gameManager.sitItems.TryGetValue(DynamicHomeworkNodeId, out sitItem) ||
            sitItem == null || !string.Equals(sitItem.sitType, "speaker", StringComparison.Ordinal))
        {
            return;
        }

        string originalFloor = gameManager.gS.homeworkFloor == 3 ? "third" : "fifth";
        string translatedFloor = gameManager.gS.homeworkFloor == 3 ? "第三" : "第五";
        string translated;
        if (Plugin.Translations.TryTranslateDynamicTemplate(
                ItemCategory,
                DynamicHomeworkItemKey,
                sitItem.text,
                DynamicHomeworkExpression,
                originalFloor,
                translatedFloor,
                out translated) &&
            !string.Equals(sitItem.text, translated, StringComparison.Ordinal))
        {
            sitItem.text = translated;
        }
    }

    private static void TranslateDynamicJoshText(global::GameManager gameManager)
    {
        if (gameManager == null || Plugin.Translations == null || gameManager.gS == null ||
            gameManager.sitItems == null || gameManager.gS.currentSitItem != DynamicJoshNodeId)
        {
            return;
        }

        global::SitItem sitItem;
        if (!gameManager.sitItems.TryGetValue(DynamicJoshNodeId, out sitItem) ||
            sitItem == null || !string.Equals(sitItem.sitType, "speaker", StringComparison.Ordinal))
        {
            return;
        }

        string translated;
        string runtimeKey = DialogueKey(DynamicJoshNodeId, DynamicJoshSpeaker);
        if ((Plugin.Translations.TryTranslateByOriginal(ItemCategory, sitItem.text, out translated) ||
             Plugin.Translations.TryTranslateRuntimeKey(DialogueCategory, runtimeKey, sitItem.text, out translated)) &&
            !string.Equals(sitItem.text, translated, StringComparison.Ordinal))
        {
            sitItem.text = translated;
        }
    }

    private static void TranslateDynamicDeborahText(global::GameManager gameManager)
    {
        if (gameManager == null || Plugin.Translations == null || gameManager.gS == null ||
            gameManager.sitItems == null || gameManager.gS.currentSitItem != DynamicDeborahNodeId)
        {
            return;
        }

        global::SitItem sitItem;
        if (!gameManager.sitItems.TryGetValue(DynamicDeborahNodeId, out sitItem) ||
            sitItem == null || !string.Equals(sitItem.sitType, "speaker", StringComparison.Ordinal))
        {
            return;
        }

        string translated;
        if (Plugin.Translations.TryTranslateByOriginal(ItemCategory, sitItem.text, out translated) &&
            !string.Equals(sitItem.text, translated, StringComparison.Ordinal))
        {
            sitItem.text = translated;
        }
    }

    private static void TranslateTextComponent(TextMeshProUGUI textComponent, string category, string key)
    {
        if (textComponent == null)
        {
            return;
        }

        if (Plugin.Fonts != null)
        {
            Plugin.Fonts.TryApplyMapping(textComponent);
        }

        string original = textComponent.text;
        string translated = TranslateWithCategoryOriginalFallback(category, key, original);
        if (!string.Equals(translated, original, StringComparison.Ordinal))
        {
            textComponent.text = translated;
        }
    }

    private static bool TryGetClientSuffix(string client, out string suffix)
    {
        suffix = null;
        if (string.IsNullOrEmpty(client))
        {
            return false;
        }

        switch (client.ToLowerInvariant())
        {
            case "vera":
                suffix = "Vera";
                return true;
            case "joe":
                suffix = "Joe";
                return true;
            case "jaden":
                suffix = "Jaden";
                return true;
            case "deborah":
                suffix = "Deborah";
                return true;
            case "ashley":
                suffix = "Ashley";
                return true;
            default:
                return false;
        }
    }
}
