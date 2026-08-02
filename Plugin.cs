using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using System.IO;
using UnityEngine;

namespace PsychologHan;

[BepInPlugin(MyPluginInfo.PLUGIN_GUID, MyPluginInfo.PLUGIN_NAME, MyPluginInfo.PLUGIN_VERSION)]
public class Plugin : BaseUnityPlugin
{
    internal static new ManualLogSource Logger;
    internal static TranslationManager Translations;
    internal static MissingTextTracker MissingText;
    internal static FontFallbackManager Fonts;

    private const string LocalizationDirectoryName = "localization";

    private ConfigEntry<bool> developmentDiagnostics;
    private ConfigEntry<KeyboardShortcut> scanCurrentSceneHotkey;
    private Harmony harmony;
    private FontFallbackManager fontFallback;

    private void Awake()
    {
        Logger = base.Logger;
        developmentDiagnostics = Config.Bind(
            "Audit",
            "DevelopmentDiagnostics",
            false,
            "When true, logs deduplicated missing/malformed localization diagnostics. Default false preserves original text silently.");
        scanCurrentSceneHotkey = Config.Bind(
            "Audit",
            "ScanCurrentSceneHotkey",
            new KeyboardShortcut(KeyCode.F8),
            "Prints all TMP text components in the active scene to the BepInEx log. Read-only diagnostic; default F8.");

        MissingText = new MissingTextTracker(Logger, () => developmentDiagnostics.Value);

        string pluginDirectory = GetPluginDirectory();
        string localizationDirectory = Path.Combine(pluginDirectory, LocalizationDirectoryName);
        Translations = TranslationManager.Load(localizationDirectory, MissingText);

        fontFallback = new FontFallbackManager(Logger);
        Fonts = fontFallback;
        string fontPath = FontFallbackManager.ResolveFontPath(pluginDirectory);
        if (fontPath != null)
        {
            if (!fontFallback.TryInstall(pluginDirectory))
            {
                Logger.LogWarning("TMP fallback font was present but could not be installed; Chinese text may display as tofu. Original font behavior is preserved.");
            }
        }
        else
        {
            Logger.LogWarning("No configured TMP fallback font found. Expected a sibling or plugin-local path ending in fonts\\" + FontFallbackManager.FontFileName + ". Chinese glyphs may display as tofu until the font file is deployed.");
        }

        harmony = new Harmony(MyPluginInfo.PLUGIN_GUID);
        Logger.LogInfo("PsychologHan localization guard: supports GameManager.addMe(int,string,int,Action), addSpeaker(int,string,string,int,Action,string), updateClientsSection(), updateSituationView(), and DeathRunes.setRunes(). Choice text is translated after OptionItem identity fields are initialized. Missing signatures are skipped safely.");
        harmony.PatchAll();

        Logger.LogInfo($"Plugin {MyPluginInfo.PLUGIN_GUID} loaded. Localization directory: {localizationDirectory}. Loaded {Translations.EntryCount} translations from {Translations.FileCount} file(s).");
        Logger.LogInfo("UI localization hooks enabled for GameManager main-menu refresh and the verified SettingsButton/LoadGameButton screen controllers. Other UI preserves original text when no approved ui.csv match exists.");
        Logger.LogInfo("Scene text scan diagnostic is bound to " + scanCurrentSceneHotkey.Value + ". Press it in-game to print active-scene TMP components.");
    }

    private void Update()
    {
        if (scanCurrentSceneHotkey != null && scanCurrentSceneHotkey.Value.IsDown())
        {
            SceneTextScanner.LogCurrentScene(Logger);
        }
    }

    private void OnDestroy()
    {
        if (fontFallback != null)
        {
            fontFallback.Uninstall();
            fontFallback = null;
        }

        Fonts = null;

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
