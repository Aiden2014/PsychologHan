using System;
using System.Globalization;
using HarmonyLib;
using TMPro;

namespace PsychologHan;

internal static class GamePatches
{
    private const string DialogueCategory = "dialogue";
    private const string ChoiceCategory = "choice";
    private const string CharacterNameCategory = "character_name";
    private const string ItemCategory = "item";
    private const string ClientInfoCategory = "client_info";
    private const string EndingCategory = "ending";

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
            text = TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory, dialogueKey, text, ItemCategory);

            if (!string.Equals(originalSpeakerName, "(ME)", StringComparison.Ordinal))
            {
                speakerName = TranslateDirectOrOriginal(CharacterNameCategory, originalSpeakerName, originalSpeakerName);
            }
        }
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.addOpt), new Type[] { typeof(int), typeof(long), typeof(string), typeof(int) })]
    private static class AddOptPatch
    {
        [HarmonyPrefix]
        private static void Prefix(int fromId, long id, ref string text)
        {
            string choiceKey = ChoiceKey(fromId, id);
            text = TranslateRuntimeKeyOrOriginal(ChoiceCategory, choiceKey, text);
        }
    }

    [HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateClientsSection))]
    private static class UpdateClientsSectionPatch
    {
        [HarmonyPostfix]
        private static void Postfix(global::GameManager __instance)
        {
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

    private static string ChoiceKey(int fromId, long optionId)
    {
        string from = fromId == 0 ? "None" : fromId.ToString(CultureInfo.InvariantCulture);
        string option = optionId.ToString(CultureInfo.InvariantCulture);
        return from + "|||" + option + "|||" + option;
    }

    private static string TranslateDirectOrOriginal(string category, string key, string original)
    {
        if (Plugin.Translations == null)
        {
            return original;
        }

        return Plugin.Translations.TranslateOrOriginal(category, key, original);
    }

    private static string TranslateRuntimeKeyOrOriginal(string category, string runtimeKey, string original)
    {
        if (Plugin.Translations == null)
        {
            return original;
        }

        return Plugin.Translations.TranslateRuntimeOrOriginal(category, runtimeKey, original);
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

    private static void TranslateTextComponent(TextMeshProUGUI textComponent, string category, string key)
    {
        if (textComponent == null)
        {
            return;
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
