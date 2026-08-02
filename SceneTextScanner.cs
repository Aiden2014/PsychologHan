using System;
using System.Collections.Generic;
using BepInEx.Logging;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace PsychologHan;

internal static class SceneTextScanner
{
    private const int MaxLoggedTextLength = 2000;

    internal static void LogCurrentScene(ManualLogSource logger)
    {
        if (logger == null)
        {
            return;
        }

        Scene activeScene = SceneManager.GetActiveScene();
        TMP_Text[] allTexts = UnityEngine.Object.FindObjectsOfType<TMP_Text>(true);
        List<TMP_Text> currentSceneTexts = new List<TMP_Text>();
        for (int index = 0; index < allTexts.Length; index++)
        {
            TMP_Text text = allTexts[index];
            if (text != null && text.gameObject.scene.handle == activeScene.handle)
            {
                currentSceneTexts.Add(text);
            }
        }

        currentSceneTexts.Sort((left, right) =>
            string.CompareOrdinal(GetHierarchyPath(left.transform), GetHierarchyPath(right.transform)));

        logger.LogInfo("[PsychologHan][SceneScan] scene='" + activeScene.name + "' handle=" + activeScene.handle + " TMP count=" + currentSceneTexts.Count);
        for (int index = 0; index < currentSceneTexts.Count; index++)
        {
            TMP_Text text = currentSceneTexts[index];
            string fontName = text.font == null ? "<null>" : text.font.name;
            string value = Abbreviate(text.text);
            logger.LogInfo(
                "[PsychologHan][SceneScan][TMP " + index + "] path='" + GetHierarchyPath(text.transform) +
                "' activeSelf=" + text.gameObject.activeSelf +
                " activeInHierarchy=" + text.gameObject.activeInHierarchy +
                " enabled=" + text.enabled +
                " font='" + fontName +
                "' text='" + value + "'");
        }

        logger.LogInfo("[PsychologHan][SceneScan] completed.");
    }

    private static string GetHierarchyPath(Transform transform)
    {
        if (transform == null)
        {
            return "<null>";
        }

        List<string> segments = new List<string>();
        Transform current = transform;
        while (current != null)
        {
            segments.Add(current.name);
            current = current.parent;
        }

        segments.Reverse();
        return string.Join("/", segments);
    }

    private static string Abbreviate(string value)
    {
        if (string.IsNullOrEmpty(value))
        {
            return string.Empty;
        }

        string flattened = value.Replace("\r", "\\r").Replace("\n", "\\n");
        if (flattened.Length <= MaxLoggedTextLength)
        {
            return flattened;
        }

        return flattened.Substring(0, MaxLoggedTextLength) + "... [truncated]";
    }
}
