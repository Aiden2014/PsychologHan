using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using System.IO;

namespace PsychologHan;

[BepInPlugin(MyPluginInfo.PLUGIN_GUID, MyPluginInfo.PLUGIN_NAME, MyPluginInfo.PLUGIN_VERSION)]
public class Plugin : BaseUnityPlugin
{
    internal static new ManualLogSource Logger;
    internal static TranslationManager Translations;
    internal static MissingTextTracker MissingText;

    private const string LocalizationDirectoryName = "localization";

    private ConfigEntry<bool> developmentDiagnostics;
    private Harmony harmony;

    private void Awake()
    {
        Logger = base.Logger;
        developmentDiagnostics = Config.Bind(
            "Audit",
            "DevelopmentDiagnostics",
            false,
            "When true, logs deduplicated missing/malformed localization diagnostics. Default false preserves original text silently.");

        MissingText = new MissingTextTracker(Logger, () => developmentDiagnostics.Value);

        string pluginDirectory = GetPluginDirectory();
        string localizationDirectory = Path.Combine(pluginDirectory, LocalizationDirectoryName);
        Translations = TranslationManager.Load(localizationDirectory, MissingText);

        harmony = new Harmony(MyPluginInfo.PLUGIN_GUID);
        Logger.LogInfo("PsychologHan localization guard: supports GameManager.addMe(int,string,int,Action), addSpeaker(int,string,string,int,Action,string), addOpt(int,long,string,int), updateClientsSection(), and DeathRunes.setRunes(). Missing signatures are skipped safely.");
        GamePatches.Apply(harmony);

        Logger.LogInfo($"Plugin {MyPluginInfo.PLUGIN_GUID} loaded. Localization directory: {localizationDirectory}. Loaded {Translations.EntryCount} translations from {Translations.FileCount} file(s).");
        if (Translations.HasCategory("ui"))
        {
            Logger.LogInfo("ui.csv was loaded, but Task 4 leaves UI integration as an extension seam because no stable non-global UI refresh hook is verified in the current references.");
        }
    }

    private void OnDestroy()
    {
        if (harmony != null)
        {
            harmony.UnpatchSelf();
            harmony = null;
        }
    }

    private string GetPluginDirectory()
    {
        if (Info != null && !string.IsNullOrEmpty(Info.Location))
        {
            string directory = Path.GetDirectoryName(Info.Location);
            if (!string.IsNullOrEmpty(directory))
            {
                return directory;
            }
        }

        return Path.Combine(Paths.PluginPath, MyPluginInfo.PLUGIN_GUID);
    }
}
