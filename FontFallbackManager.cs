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
    internal const string FontFileName = "汇文明朝体汇文明朝体.ttf";

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
        string fontPath = ResolveFontPath(pluginDirectory);
        if (fontPath == null)
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

                sourceFont.name = "PsychologHan 汇文明朝体";
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

                fontAsset.name = "PsychologHan 汇文明朝体 Dynamic";
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
            logger.LogInfo("Installed the configured Chinese TMP fallback font from " + fontPath + ". Chinese glyphs will be generated dynamically as needed.");
            return true;
        }
        catch (Exception exception)
        {
            logger.LogWarning("Could not install the configured TMP fallback font; original font behavior will be preserved. " + exception.GetType().Name + ": " + exception.Message);
            return false;
        }
    }

    internal static string ResolveFontPath(string pluginDirectory)
    {
        string pluginLocalPath = Path.Combine(pluginDirectory, FontDirectoryName, FontFileName);
        string pluginsDirectory = Directory.GetParent(pluginDirectory)?.FullName;
        string sharedPath = pluginsDirectory == null
            ? null
            : Path.Combine(pluginsDirectory, FontDirectoryName, FontFileName);

        if (sharedPath != null && File.Exists(sharedPath))
        {
            return sharedPath;
        }

        return File.Exists(pluginLocalPath) ? pluginLocalPath : null;
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
