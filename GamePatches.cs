using System;
using System.Globalization;
using System.Reflection;
using HarmonyLib;

namespace PsychologHan;

internal static class GamePatches
{
    private const string DialogueCategory = "dialogue";
    private const string ChoiceCategory = "choice";
    private const string CharacterNameCategory = "character_name";
    private const string ItemCategory = "item";
    private const string ClientInfoCategory = "client_info";
    private const string EndingCategory = "ending";

    public static void Apply(Harmony harmony)
    {
        if (harmony == null)
        {
            return;
        }

        int patchedCount = 0;
        Type gameManagerType = AccessTools.TypeByName("GameManager");
        if (gameManagerType == null)
        {
            Plugin.Logger.LogWarning("GameManager type was not found; dialogue, choice, and client info localization patches were skipped.");
        }
        else
        {
            patchedCount += PatchPrefix(harmony, gameManagerType, "addMe", new[] { typeof(int), typeof(string), typeof(int), typeof(Action) }, nameof(AddMePrefix));
            patchedCount += PatchPrefix(harmony, gameManagerType, "addSpeaker", new[] { typeof(int), typeof(string), typeof(string), typeof(int), typeof(Action), typeof(string) }, nameof(AddSpeakerPrefix));
            patchedCount += PatchPrefix(harmony, gameManagerType, "addOpt", new[] { typeof(int), typeof(long), typeof(string), typeof(int) }, nameof(AddOptPrefix));
            patchedCount += PatchPostfix(harmony, gameManagerType, "updateClientsSection", Type.EmptyTypes, nameof(UpdateClientsSectionPostfix));
        }

        Type deathRunesType = AccessTools.TypeByName("DeathRunes");
        if (deathRunesType == null)
        {
            Plugin.Logger.LogWarning("DeathRunes type was not found; ending rune localization patch was skipped.");
        }
        else
        {
            patchedCount += PatchPostfix(harmony, deathRunesType, "setRunes", Type.EmptyTypes, nameof(DeathRunesSetRunesPostfix));
        }

        Plugin.Logger.LogInfo("Applied " + patchedCount.ToString(CultureInfo.InvariantCulture) + " PsychologHan localization patch(es).");
    }

    private static int PatchPrefix(Harmony harmony, Type targetType, string methodName, Type[] argumentTypes, string prefixName)
    {
        MethodInfo target = AccessTools.Method(targetType, methodName, argumentTypes);
        if (target == null)
        {
            Plugin.Logger.LogWarning(targetType.FullName + "." + methodName + " signature was not found; patch skipped.");
            return 0;
        }

        harmony.Patch(target, prefix: new HarmonyMethod(typeof(GamePatches), prefixName));
        return 1;
    }

    private static int PatchPostfix(Harmony harmony, Type targetType, string methodName, Type[] argumentTypes, string postfixName)
    {
        MethodInfo target = AccessTools.Method(targetType, methodName, argumentTypes);
        if (target == null)
        {
            Plugin.Logger.LogWarning(targetType.FullName + "." + methodName + " signature was not found; patch skipped.");
            return 0;
        }

        harmony.Patch(target, postfix: new HarmonyMethod(typeof(GamePatches), postfixName));
        return 1;
    }

    private static void AddMePrefix(int id, ref string text)
    {
        string dialogueKey = DialogueKey(id, "ME");
        text = TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory, dialogueKey, text, ItemCategory);
    }

    private static void AddSpeakerPrefix(int id, ref string speakerName, ref string text)
    {
        string originalSpeakerName = speakerName;
        string dialogueKey = DialogueKey(id, originalSpeakerName);
        text = TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory, dialogueKey, text, ItemCategory);

        if (!string.Equals(originalSpeakerName, "(ME)", StringComparison.Ordinal))
        {
            speakerName = TranslateDirectOrOriginal(CharacterNameCategory, originalSpeakerName, originalSpeakerName);
        }
    }

    private static void AddOptPrefix(int fromId, long id, ref string text)
    {
        string choiceKey = ChoiceKey(fromId, id);
        text = TranslateRuntimeKeyOrOriginal(ChoiceCategory, choiceKey, text);
    }

    private static void UpdateClientsSectionPostfix(object __instance)
    {
        string suffix;
        if (!TryGetClientSuffix(GetStringField(__instance, "clientCurrentlyChosen"), out suffix))
        {
            return;
        }

        TranslateTextComponentField(__instance, "trustComment", ClientInfoCategory, "trustComment" + suffix);
        TranslateTextComponentField(__instance, "treatmentComment", ClientInfoCategory, "treatmentComment" + suffix);
    }

    private static void DeathRunesSetRunesPostfix(object __instance)
    {
        TranslateTextComponentField(__instance, "runeVera", EndingCategory, "runeVera");
        TranslateTextComponentField(__instance, "runeJaden", EndingCategory, "runeJaden");
        TranslateTextComponentField(__instance, "runeJoe", EndingCategory, "runeJoe");
        TranslateTextComponentField(__instance, "runeDeborah", EndingCategory, "runeDeborah");
        TranslateTextComponentField(__instance, "runeAshley", EndingCategory, "runeAshley");
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

    private static void TranslateTextComponentField(object instance, string fieldName, string category, string key)
    {
        object textComponent = GetFieldValue(instance, fieldName);
        string original = GetText(textComponent);
        if (original == null)
        {
            return;
        }

        string translated = TranslateWithCategoryOriginalFallback(category, key, original);
        if (!string.Equals(translated, original, StringComparison.Ordinal))
        {
            SetText(textComponent, translated);
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

    private static string GetStringField(object instance, string fieldName)
    {
        object value = GetFieldValue(instance, fieldName);
        return value as string;
    }

    private static object GetFieldValue(object instance, string fieldName)
    {
        if (instance == null || string.IsNullOrEmpty(fieldName))
        {
            return null;
        }

        FieldInfo field = AccessTools.Field(instance.GetType(), fieldName);
        return field == null ? null : field.GetValue(instance);
    }

    private static string GetText(object textComponent)
    {
        if (textComponent == null)
        {
            return null;
        }

        PropertyInfo textProperty = AccessTools.Property(textComponent.GetType(), "text");
        return textProperty == null ? null : textProperty.GetValue(textComponent, null) as string;
    }

    private static void SetText(object textComponent, string text)
    {
        if (textComponent == null)
        {
            return;
        }

        PropertyInfo textProperty = AccessTools.Property(textComponent.GetType(), "text");
        if (textProperty != null && textProperty.CanWrite)
        {
            textProperty.SetValue(textComponent, text, null);
        }
    }
}
