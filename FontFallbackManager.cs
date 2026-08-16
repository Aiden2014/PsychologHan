using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
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
    private const int GochiHandSamplingPointSize = 78;

    private readonly ManualLogSource logger;
    private readonly Dictionary<string, Font> mappedSourceFonts = new Dictionary<string, Font>(StringComparer.Ordinal);
    private readonly Dictionary<string, TMP_FontAsset> mappedFontAssets = new Dictionary<string, TMP_FontAsset>(StringComparer.Ordinal);
    private readonly Dictionary<TMP_Text, TMP_FontAsset> originalFontByComponent = new Dictionary<TMP_Text, TMP_FontAsset>();
    private readonly Dictionary<TMP_Text, Material> originalMaterialByComponent = new Dictionary<TMP_Text, Material>();
    private readonly Dictionary<TMP_Text, ITextPreprocessor> originalTextPreprocessorByComponent = new Dictionary<TMP_Text, ITextPreprocessor>();
    private readonly Dictionary<TMP_Text, bool> originalFontScopeByComponent = new Dictionary<TMP_Text, bool>();
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
                fontAsset = CreateFontAsset(fontPath, "PsychologHan 南西油墨宋", 90, out sourceFont);
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
            TryInstallMappedFont(pluginDirectory, TypewriterStandardAssetName, TypewriterMappedFontFileName, "朝華打字機", 90);
            TryInstallMappedFont(pluginDirectory, GochiHandAssetName, GochiHandMappedFontFileName, "JasonHandwriting1", GochiHandSamplingPointSize);

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

        bool isOriginalGameFontScope;
        if (!originalFontScopeByComponent.TryGetValue(textComponent, out isOriginalGameFontScope))
        {
            isOriginalGameFontScope = IsOriginalGameFontScope(textComponent);
            originalFontScopeByComponent[textComponent] = isOriginalGameFontScope;
        }

        if (isOriginalGameFontScope)
        {
            return TryRestoreOriginalMapping(textComponent);
        }

        TMP_FontAsset originalFont = textComponent.font;
        string mappingKey = GetMappingKey(originalFont);
        if (mappingKey == null)
        {
            TMP_FontAsset rememberedOriginalFont;
            if (originalFontByComponent.TryGetValue(textComponent, out rememberedOriginalFont))
            {
                originalFont = rememberedOriginalFont;
                mappingKey = GetMappingKey(originalFont);
            }
        }

        TMP_FontAsset mappedFontAsset;
        if (mappingKey == null || !mappedFontAssets.TryGetValue(mappingKey, out mappedFontAsset) || mappedFontAsset == null)
        {
            return false;
        }

        if (!originalFontByComponent.ContainsKey(textComponent))
        {
            originalFontByComponent.Add(textComponent, textComponent.font);
            originalMaterialByComponent.Add(textComponent, textComponent.fontSharedMaterial);
            originalTextPreprocessorByComponent.Add(textComponent, textComponent.textPreprocessor);
        }

        if (mappingKey == TypewriterStandardAssetName)
        {
            InstallTypewriterDigitFont(textComponent, originalFont);
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

    private static bool IsOriginalGameFontScope(TMP_Text textComponent)
    {
        if (IsSpeakerOriginalFontScope(textComponent) ||
            IsMeOriginalFontScope(textComponent) ||
            IsInGameMenuSpeakerLineScope(textComponent) ||
            IsPulsingMarkerSymbolScope(textComponent) ||
            IsClientCaptionOriginalFontScope(textComponent) ||
            IsAssessmentBarOriginalFontScope(textComponent))
        {
            return true;
        }

        Transform current = textComponent.transform;
        while (current != null)
        {
            if (current.GetComponent<global::MainMenuButton>() != null ||
                current.GetComponent<global::CloseClientSectionButton>() != null ||
                current.name == "MainMenuButton" ||
                current.name == "CloseClientSectionButton")
            {
                return true;
            }

            current = current.parent;
        }

        return false;
    }

    private static bool IsMeOriginalFontScope(TMP_Text textComponent)
    {
        if (textComponent == null || !IsSpeakerLineName(textComponent.name))
        {
            return false;
        }

        Transform current = textComponent.transform.parent;
        while (current != null)
        {
            if (current.name == "Me")
            {
                return true;
            }

            current = current.parent;
        }

        return false;
    }

    private static bool IsSpeakerOriginalFontScope(TMP_Text textComponent)
    {
        if (textComponent == null)
        {
            return false;
        }

        bool isSpeakerLine = IsSpeakerLineName(textComponent.name);
        bool insideCaptionRectangle = false;
        bool insideSpeakerCaption = false;
        Transform current = textComponent.transform;
        while (current != null)
        {
            if (current.name == "CaptionRectangle")
            {
                insideCaptionRectangle = true;
            }
            else if (current.name == "SpeakerCaption")
            {
                insideSpeakerCaption = true;
            }
            else if (current.name == "Speaker")
            {
                bool inCaptionRectangle = insideCaptionRectangle && insideSpeakerCaption;
                bool isDirectSpeakerLine = isSpeakerLine && textComponent.transform.parent == current;
                return inCaptionRectangle || isDirectSpeakerLine;
            }

            current = current.parent;
        }

        return false;
    }

    private static bool IsInGameMenuSpeakerLineScope(TMP_Text textComponent)
    {
        if (textComponent == null || !IsSpeakerLineName(textComponent.name))
        {
            return false;
        }

        Transform current = textComponent.transform.parent;
        while (current != null)
        {
            if (current.name == "InGameMenuButton")
            {
                return true;
            }

            current = current.parent;
        }

        return false;
    }

    private static bool IsSpeakerLineName(string componentName)
    {
        return !string.IsNullOrEmpty(componentName) &&
            componentName.StartsWith("SpeakerLine", StringComparison.Ordinal);
    }

    private static bool IsPulsingMarkerSymbolScope(TMP_Text textComponent)
    {
        if (textComponent == null || !IsPulsingMarkerSymbolName(textComponent.name))
        {
            return false;
        }

        Transform current = textComponent.transform.parent;
        while (current != null)
        {
            if (current.name == "PulsingMarker")
            {
                return true;
            }

            current = current.parent;
        }

        return false;
    }

    private static bool IsPulsingMarkerSymbolName(string componentName)
    {
        return componentName == "Symbol" ||
            componentName == "Symbol (1)" ||
            componentName == "Symbol (2)" ||
            componentName == "Symbol (3)";
    }

    private static bool IsClientCaptionOriginalFontScope(TMP_Text textComponent)
    {
        if (textComponent == null)
        {
            return false;
        }

        bool insideClientCaptionRectangle = false;
        bool insideClientCaptions = false;
        Transform current = textComponent.transform;
        while (current != null)
        {
            if (IsClientCaptionRectangleName(current.name))
            {
                insideClientCaptionRectangle = true;
            }
            else if (current.name == "ClientCaptions")
            {
                insideClientCaptions = true;
            }
            else if (current.name == "ClientsSection")
            {
                return insideClientCaptionRectangle && insideClientCaptions;
            }

            current = current.parent;
        }

        return false;
    }

    private static bool IsClientCaptionRectangleName(string componentName)
    {
        return componentName == "CaptionRectangle" ||
            componentName == "CaptionRectangleSelected";
    }

    private static bool IsAssessmentBarOriginalFontScope(TMP_Text textComponent)
    {
        if (textComponent == null)
        {
            return false;
        }

        bool insideProgressBar = false;
        bool insideHeading = false;
        Transform current = textComponent.transform;
        while (current != null)
        {
            if (current.name == "Heading")
            {
                insideHeading = true;
            }
            else if (current.name == "TrustProgressBar" ||
                current.name == "TreatmentProgressBar")
            {
                insideProgressBar = true;
            }
            else if (current.name == "AssessmentBars")
            {
                return insideProgressBar && !insideHeading;
            }

            current = current.parent;
        }

        return false;
    }
    private bool TryRestoreOriginalMapping(TMP_Text textComponent)
    {
        TMP_FontAsset originalFont;
        if (!originalFontByComponent.TryGetValue(textComponent, out originalFont))
        {
            return false;
        }

        bool changed = false;
        if (textComponent.font != originalFont)
        {
            textComponent.font = originalFont;
            changed = true;
        }

        Material originalMaterial;
        if (originalMaterialByComponent.TryGetValue(textComponent, out originalMaterial) &&
            textComponent.fontSharedMaterial != originalMaterial)
        {
            textComponent.fontSharedMaterial = originalMaterial;
            changed = true;
        }

        ITextPreprocessor originalPreprocessor;
        if (originalTextPreprocessorByComponent.TryGetValue(textComponent, out originalPreprocessor) &&
            textComponent.textPreprocessor is TypewriterDigitFontPreprocessor)
        {
            textComponent.textPreprocessor = originalPreprocessor;
            changed = true;
        }

        return changed;
    }

    private void InstallTypewriterDigitFont(TMP_Text textComponent, TMP_FontAsset originalFont)
    {
        if (textComponent == null || originalFont == null || !textComponent.richText || string.IsNullOrEmpty(originalFont.name))
        {
            return;
        }

        // TMP resolves the <font="..."> tag through the material reference
        // cache. The original asset is already a game-owned asset; registering
        // it here makes the explicit digit spans work even after the component
        // switches to the mapped Typewriter asset.
        MaterialReferenceManager.AddFontAsset(originalFont);
        if (originalFont.name.IndexOf('"') >= 0 || originalFont.name.IndexOf('<') >= 0 || originalFont.name.IndexOf('>') >= 0)
        {
            return;
        }

        ITextPreprocessor originalPreprocessor;
        if (!originalTextPreprocessorByComponent.TryGetValue(textComponent, out originalPreprocessor))
        {
            return;
        }

        if (!(textComponent.textPreprocessor is TypewriterDigitFontPreprocessor))
        {
            textComponent.textPreprocessor = new TypewriterDigitFontPreprocessor(originalFont.name, originalPreprocessor);
        }
    }

    private sealed class TypewriterDigitFontPreprocessor : ITextPreprocessor
    {
        private readonly string originalFontAssetName;
        private readonly ITextPreprocessor innerPreprocessor;

        internal TypewriterDigitFontPreprocessor(string originalFontAssetName, ITextPreprocessor innerPreprocessor)
        {
            this.originalFontAssetName = originalFontAssetName;
            this.innerPreprocessor = innerPreprocessor;
        }

        public string PreprocessText(string text)
        {
            if (innerPreprocessor != null)
            {
                text = innerPreprocessor.PreprocessText(text);
            }

            if (string.IsNullOrEmpty(text))
            {
                return text;
            }

            StringBuilder processedText = null;
            bool insideMarkup = false;
            for (int index = 0; index < text.Length; index++)
            {
                char character = text[index];
                if (character == '<')
                {
                    insideMarkup = true;
                }

                if (!insideMarkup &&
                    ((character >= '0' && character <= '9') || character == '%'))
                {
                    if (processedText == null)
                    {
                        processedText = new StringBuilder(text.Length + 32);
                        processedText.Append(text, 0, index);
                    }

                    processedText.Append("<font=\"");
                    processedText.Append(originalFontAssetName);
                    processedText.Append("\">");
                    processedText.Append(character);
                    processedText.Append("</font>");
                }
                else if (processedText != null)
                {
                    processedText.Append(character);
                }

                if (character == '>')
                {
                    insideMarkup = false;
                }
            }

            return processedText == null ? text : processedText.ToString();
        }
    }

    private void TryInstallMappedFont(string pluginDirectory, string mappingKey, string fileName, string displayName, int samplingPointSize)
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
        TMP_FontAsset mappedFontAsset = CreateFontAsset(path, "PsychologHan " + displayName, samplingPointSize, out mappedSourceFont);
        if (mappedFontAsset == null)
        {
            logger.LogWarning("Could not create mapped TMP font " + displayName + "; the original font will be preserved for " + mappingKey + ".");
            return;
        }

        mappedSourceFonts.Add(mappingKey, mappedSourceFont);
        mappedFontAssets.Add(mappingKey, mappedFontAsset);
        logger.LogInfo("Installed TMP font mapping " + mappingKey + " -> " + path + ".");
    }

    private static TMP_FontAsset CreateFontAsset(string fontPath, string assetName, int samplingPointSize, out Font createdFont)
    {
        createdFont = new Font(fontPath);
        if (createdFont == null)
        {
            return null;
        }

        TMP_FontAsset createdAsset = TMP_FontAsset.CreateFontAsset(
            createdFont,
            samplingPointSize,
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

        foreach (KeyValuePair<TMP_Text, ITextPreprocessor> originalPreprocessor in originalTextPreprocessorByComponent)
        {
            TMP_Text textComponent = originalPreprocessor.Key;
            if (textComponent != null && textComponent.textPreprocessor is TypewriterDigitFontPreprocessor)
            {
                textComponent.textPreprocessor = originalPreprocessor.Value;
            }
        }

        originalTextPreprocessorByComponent.Clear();
        originalFontScopeByComponent.Clear();

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
