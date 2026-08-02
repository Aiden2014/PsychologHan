using System;
using System.Collections.Generic;
using System.IO;
using BepInEx.Logging;
using TMPro;
using UnityEngine;
using UnityEngine.TextCore;
using UnityEngine.TextCore.LowLevel;

namespace PsychologHan;

internal sealed class FontFallbackManager
{
    internal const string FontDirectoryName = "fonts";
    internal const string FontFileName = "NotoSansSC-VF.ttf";

    private readonly ManualLogSource logger;
    private Font sourceFont;
    private TMP_FontAsset fontAsset;
    private bool registered;

    internal FontFallbackManager(ManualLogSource logger)
    {
        this.logger = logger;
    }

    internal bool TryInstall(string pluginDirectory)
    {
        string fontPath = Path.Combine(pluginDirectory, FontDirectoryName, FontFileName);
        if (!File.Exists(fontPath))
        {
            return false;
        }

        try
        {
            if (fontAsset == null)
            {
                sourceFont = new Font(fontPath);
                if (sourceFont == null)
                {
                    return false;
                }

                sourceFont.name = "PsychologHan Noto Sans SC";
                fontAsset = TMP_FontAsset.CreateFontAsset(
                    sourceFont,
                    90,
                    9,
                    GlyphRenderMode.SDFAA,
                    2048,
                    2048,
                    AtlasPopulationMode.Dynamic,
                    true);
                if (fontAsset == null)
                {
                    return false;
                }

                fontAsset.name = "PsychologHan Noto Sans SC Dynamic";
            }

            List<TMP_FontAsset> fallbackFontAssets = TMP_Settings.fallbackFontAssets;
            if (fallbackFontAssets == null)
            {
                return false;
            }

            if (!fallbackFontAssets.Contains(fontAsset))
            {
                fallbackFontAssets.Add(fontAsset);
            }

            registered = true;
            logger.LogInfo("Installed Noto Sans SC as the plugin-local TMP fallback font. Chinese glyphs will be generated dynamically as needed.");
            return true;
        }
        catch (Exception exception)
        {
            logger.LogWarning("Could not install the plugin-local TMP fallback font; original font behavior will be preserved. " + exception.GetType().Name + ": " + exception.Message);
            return false;
        }
    }

    internal void Uninstall()
    {
        try
        {
            if (registered && fontAsset != null && TMP_Settings.fallbackFontAssets != null)
            {
                TMP_Settings.fallbackFontAssets.Remove(fontAsset);
            }
        }
        catch (Exception exception)
        {
            logger.LogDebug("Could not remove the TMP fallback font during plugin teardown: " + exception.Message);
        }

        registered = false;

        if (fontAsset != null)
        {
            UnityEngine.Object.Destroy(fontAsset);
            fontAsset = null;
        }

        if (sourceFont != null)
        {
            UnityEngine.Object.Destroy(sourceFont);
            sourceFont = null;
        }
    }
}
