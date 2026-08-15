using System;
using System.Collections.Generic;
using System.Reflection.Emit;
using BepInEx;
using HarmonyLib;

namespace PsychologEnhance;

[BepInPlugin(PluginGuid, PluginName, PluginVersion)]
public sealed class Plugin : BaseUnityPlugin
{
    private const string PluginGuid = "com.aiden.psychologenhance";
    private const string PluginName = "PsychologEnhance";
    private const string PluginVersion = "1.0.0";

    private Harmony harmony;

    private void Awake()
    {
        try
        {
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
        if (harmony == null)
        {
            return;
        }

        harmony.UnpatchSelf();
        harmony = null;
    }
}

[HarmonyPatch(typeof(GameScore), "calculateAndDisplayGameScore")]
internal static class GameScorePatch
{
    [HarmonyTranspiler]
    private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
    {
        List<CodeInstruction> code = new List<CodeInstruction>(instructions);

        for (int index = 0; index < code.Count; index++)
        {
            if (!IsAshleyCoefficient(code[index]))
            {
                continue;
            }

            if (index + 3 >= code.Count || code[index + 2].opcode != OpCodes.Mul || code[index + 3].opcode != OpCodes.Add)
            {
                throw new InvalidOperationException("The Ashley score instructions have an unexpected shape.");
            }

            // Current IL: score + (1 / 13 * clampedAshley). Replace only this segment.
            code[index].operand = 2f / 9f;
            code.Insert(index + 3, new CodeInstruction(OpCodes.Ldc_R4, 6f));
            code.Insert(index + 4, new CodeInstruction(OpCodes.Sub));
            return code;
        }

        throw new InvalidOperationException("The Ashley score coefficient was not found.");
    }

    private static bool IsAshleyCoefficient(CodeInstruction instruction)
    {
        return instruction.opcode == OpCodes.Ldc_R4
            && instruction.operand is float value
            && Math.Abs(value - (1f / 13f)) < 0.0001f;
    }
}
