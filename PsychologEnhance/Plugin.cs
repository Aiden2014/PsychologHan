using System;
using System.IO;
using System.Security.Cryptography;
using BepInEx;
using BepInEx.Logging;
using HarmonyLib;

namespace PsychologEnhance;

[BepInPlugin(PluginGuid, PluginName, PluginVersion)]
public sealed class Plugin : BaseUnityPlugin
{
    private const string PluginGuid = "com.aiden.psychologenhance";
    private const string PluginName = "PsychologEnhance";
    private const string PluginVersion = "1.0.0";
    private const string SupportedAssemblyCSharpSha256 = "B0078981C2A42C8123D53E1CACFDA9F222B415565A3241175EA18E0B7DCF5F91";

    private Harmony harmony;
    private static ManualLogSource log;
    private static bool runtimeFailureLogged;

    private void Awake()
    {
        log = base.Logger;
        runtimeFailureLogged = false;

        try
        {
            if (!IsSupportedGameBuild())
            {
                return;
            }

            harmony = new Harmony(PluginGuid);
            harmony.PatchAll();
            Logger.LogInfo("PsychologEnhance loaded: corrected the Ashley score segment so a perfect run reaches 100.");
        }
        catch (Exception exception)
        {
            if (harmony != null)
            {
                harmony.UnpatchSelf();
            }

            harmony = null;
            Logger.LogError("PsychologEnhance could not patch this Psycholog build; the original score calculation remains active.\n" + exception);
        }
    }

    private void OnDestroy()
    {
        if (harmony != null)
        {
            harmony.UnpatchSelf();
            harmony = null;
        }

        log = null;
    }

    private bool IsSupportedGameBuild()
    {
        try
        {
            string assemblyPath = typeof(GameScore).Assembly.Location;
            using FileStream stream = File.OpenRead(assemblyPath);
            using SHA256 sha256 = SHA256.Create();
            string actualHash = BitConverter.ToString(sha256.ComputeHash(stream)).Replace("-", string.Empty);

            if (string.Equals(actualHash, SupportedAssemblyCSharpSha256, StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }

            Logger.LogWarning(
                "PsychologEnhance supports Assembly-CSharp SHA-256 " + SupportedAssemblyCSharpSha256
                + ", but the loaded game build is " + actualHash + ". The original score calculation remains active.");
            return false;
        }
        catch (Exception exception)
        {
            Logger.LogError("PsychologEnhance could not verify the game build; the original score calculation remains active.\n" + exception);
            return false;
        }
    }

    internal static void LogRuntimeFailure(Exception exception)
    {
        if (runtimeFailureLogged)
        {
            return;
        }

        runtimeFailureLogged = true;
        log?.LogError("PsychologEnhance score calculation failed at runtime; falling back to the original game method.\n" + exception);
    }
}

[HarmonyPatch(typeof(GameScore), "calculateAndDisplayGameScore")]
internal static class GameScorePatch
{
    [HarmonyPrefix]
    private static bool Prefix(GameScore __instance)
    {
        if (__instance == null || __instance.gM == null || __instance.gM.gS == null || __instance.textObject == null)
        {
            return true;
        }

        try
        {
            int score = GameScoreCalculator.Calculate(__instance.gM.gS);
            __instance.textObject.text = score.ToString();

            if (score == 100 && __instance.gM.steamIntegration != null)
            {
                __instance.gM.steamIntegration.UnlockAchievement("P30");
            }

            return false;
        }
        catch (Exception exception)
        {
            Plugin.LogRuntimeFailure(exception);
            return true;
        }
    }
}

internal static class GameScoreCalculator
{
    public static int Calculate(GameState state)
    {
        float score = 0f;

        if (!state.killedVera)
        {
            score += 14f;
            score += 2f / 9f * Clamp(state.treatmentVera, 27f, 54f) - 6f;
        }

        if (!state.killedJoe)
        {
            score += 14f;
            score += Clamp(state.treatmentJoe, 20f, 26f) - 20f;
        }

        if (!state.killedJaden)
        {
            score += 14f;
            score += 0.375f * Clamp(state.treatmentJaden, 64f, 80f) - 24f;
        }

        if (!state.killedDeborah)
        {
            score += 14f;
            score += 0.6f * Clamp(state.treatmentDeborah, 10f, 20f) - 6f;
        }

        if (!state.ashleyDied)
        {
            score += 14f;
            score += 2f / 9f * Clamp(state.treatmentAshley, 27f, 54f) - 6f;
        }

        return (int)score;
    }

    private static float Clamp(float value, float minimum, float maximum)
    {
        if (value < minimum)
        {
            return minimum;
        }

        return value > maximum ? maximum : value;
    }
}
