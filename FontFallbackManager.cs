using System;
using System.Collections.Generic;
using System.IO;
using BepInEx.Logging;
using TMPro;
using UnityEngine;
using UnityEngine.TextCore.LowLevel;

namespace PsychologHan;

internal sealed class FontFallbackManager
{
    internal const string FontDirectoryName = "fonts";
    internal const string FontFileName = "南西油墨宋.ttf";

    private const string AdlerFamilyName = "Adler";
    private const string TypewriterStandardAssetName = "Typewriter_standard";
    private const string TypewriterMappedFontFileName = "朝華打字機.ttf";
    private const string GochiHandAssetName = "GochiHand-Regular";
    private const string GochiHandMappedFontFileName = "JasonHandwriting1-Regular.ttf";

    private readonly ManualLogSource logger;
    private readonly Dictionary<string, Font> mappedSourceFonts = new Dictionary<string, Font>(StringComparer.Ordinal);
    private readonly Dictionary<string, TMP_FontAsset> mappedFontAssets = new Dictionary<string, TMP_FontAsset>(StringComparer.Ordinal);
    private readonly Dictionary<TMP_Text, TMP_FontAsset> originalFontByComponent = new Dictionary<TMP_Text, TMP_FontAsset>();
    private readonly Dictionary<TMP_Text, Material> originalMaterialByComponent = new Dictionary<TMP_Text, Material>();
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
                fontAsset = CreateFontAsset(fontPath, "PsychologHan 南西油墨宋", out sourceFont);
                if (fontAsset == null)
                {
                    return false;
                }
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

            mappedFontAssets[AdlerFamilyName] = fontAsset;
            logger.LogInfo("Installed TMP font mapping Adler -> " + fontPath + " (shared with the global fallback).");
            TryInstallMappedFont(pluginDirectory, TypewriterStandardAssetName, TypewriterMappedFontFileName, "朝華打字機");
            TryInstallMappedFont(pluginDirectory, GochiHandAssetName, GochiHandMappedFontFileName, "JasonHandwriting1");

            registered = true;
            logger.LogInfo(
                "Installed the configured Chinese TMP fallback font from " + fontPath +
                ". Font mappings: Adler/global fallback -> 南西油墨宋, Typewriter_standard -> 朝華打字機, GochiHand-Regular -> JasonHandwriting1.");
            return true;
        }
        catch (Exception exception)
        {
            logger.LogWarning("Could not install the configured TMP fonts; original font behavior will be preserved. " + exception.GetType().Name + ": " + exception.Message);
            return false;
        }
    }

    internal bool TryApplyMapping(TMP_Text textComponent)
    {
        if (!registered || textComponent == null || textComponent.font == null)
        {
            return false;
        }

        string mappingKey = GetMappingKey(textComponent.font);
        TMP_FontAsset mappedFontAsset;
        if (mappingKey == null || !mappedFontAssets.TryGetValue(mappingKey, out mappedFontAsset) || mappedFontAsset == null)
        {
            return false;
        }

        if (!originalFontByComponent.ContainsKey(textComponent))
        {
            originalFontByComponent.Add(textComponent, textComponent.font);
            originalMaterialByComponent.Add(textComponent, textComponent.fontSharedMaterial);
        }

        bool changed = false;
        if (textComponent.font != mappedFontAsset)
        {
            textComponent.font = mappedFontAsset;
            changed = true;
        }

        if (mappedFontAsset.material != null && textComponent.fontSharedMaterial != mappedFontAsset.material)
        {
            textComponent.fontSharedMaterial = mappedFontAsset.material;
            changed = true;
        }

        return changed;
    }

    private void TryInstallMappedFont(string pluginDirectory, string mappingKey, string fileName, string displayName)
    {
        if (mappedFontAssets.ContainsKey(mappingKey))
        {
            return;
        }

        string path = ResolveFontPath(pluginDirectory, fileName);
        if (path == null)
        {
            logger.LogWarning("Configured mapped TMP font is missing: " + fileName + ". The original font will be preserved for " + mappingKey + ".");
            return;
        }

        Font mappedSourceFont;
        TMP_FontAsset mappedFontAsset = CreateFontAsset(path, "PsychologHan " + displayName, out mappedSourceFont);
        if (mappedFontAsset == null)
        {
            logger.LogWarning("Could not create mapped TMP font " + displayName + "; the original font will be preserved for " + mappingKey + ".");
            return;
        }

        mappedSourceFonts.Add(mappingKey, mappedSourceFont);
        mappedFontAssets.Add(mappingKey, mappedFontAsset);
        logger.LogInfo("Installed TMP font mapping " + mappingKey + " -> " + path + ".");
    }

    private static TMP_FontAsset CreateFontAsset(string fontPath, string assetName, out Font createdFont)
    {
        createdFont = new Font(fontPath);
        if (createdFont == null)
        {
            return null;
        }

        TMP_FontAsset createdAsset = TMP_FontAsset.CreateFontAsset(
            createdFont,
            90,
            9,
            GlyphRenderMode.SDFAA,
            2048,
            2048,
            AtlasPopulationMode.Dynamic,
            true);
        if (createdAsset == null)
        {
            UnityEngine.Object.Destroy(createdFont);
            createdFont = null;
            return null;
        }

        createdAsset.name = assetName + " Dynamic";
        return createdAsset;
    }

    private static string GetMappingKey(TMP_FontAsset originalFont)
    {
        if (originalFont == null)
        {
            return null;
        }

        if (!string.IsNullOrEmpty(originalFont.name) &&
            originalFont.name.StartsWith(TypewriterStandardAssetName, StringComparison.OrdinalIgnoreCase))
        {
            return TypewriterStandardAssetName;
        }

        if (!string.IsNullOrEmpty(originalFont.name) &&
            originalFont.name.StartsWith(GochiHandAssetName, StringComparison.OrdinalIgnoreCase))
        {
            return GochiHandAssetName;
        }

        if (string.Equals(originalFont.faceInfo.familyName, AdlerFamilyName, StringComparison.OrdinalIgnoreCase))
        {
            return AdlerFamilyName;
        }

        return null;
    }

    internal static string ResolveFontPath(string pluginDirectory)
    {
        string pluginLocalPath = Path.Combine(pluginDirectory, FontDirectoryName, FontFileName);
        string resolved = ResolveFontPath(pluginDirectory, FontFileName);
        return resolved ?? (File.Exists(pluginLocalPath) ? pluginLocalPath : null);
    }

    private static string ResolveFontPath(string pluginDirectory, string fileName)
    {
        string pluginLocalPath = Path.Combine(pluginDirectory, FontDirectoryName, fileName);
        string pluginsDirectory = Directory.GetParent(pluginDirectory)?.FullName;
        string sharedPath = pluginsDirectory == null
            ? null
            : Path.Combine(pluginsDirectory, FontDirectoryName, fileName);

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

        foreach (KeyValuePair<TMP_Text, TMP_FontAsset> originalFont in originalFontByComponent)
        {
            TMP_Text textComponent = originalFont.Key;
            if (textComponent != null && textComponent.font != null && mappedFontAssets.ContainsValue(textComponent.font))
            {
                textComponent.font = originalFont.Value;
            }
        }

        originalFontByComponent.Clear();

        foreach (KeyValuePair<TMP_Text, Material> originalMaterial in originalMaterialByComponent)
        {
            TMP_Text textComponent = originalMaterial.Key;
            if (textComponent != null && textComponent.font != null)
            {
                textComponent.fontSharedMaterial = originalMaterial.Value;
            }
        }

        originalMaterialByComponent.Clear();

        foreach (TMP_FontAsset mappedFontAsset in mappedFontAssets.Values)
        {
            if (mappedFontAsset != null && mappedFontAsset != fontAsset)
            {
                UnityEngine.Object.Destroy(mappedFontAsset);
            }
        }

        foreach (Font mappedSourceFont in mappedSourceFonts.Values)
        {
            if (mappedSourceFont != null)
            {
                UnityEngine.Object.Destroy(mappedSourceFont);
            }
        }

        mappedFontAssets.Clear();
        mappedSourceFonts.Clear();

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
