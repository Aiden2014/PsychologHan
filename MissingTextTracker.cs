using System;
using System.Collections.Generic;
using BepInEx.Logging;

namespace PsychologHan;

public sealed class MissingTextTracker
{
    private readonly ManualLogSource logger;
    private readonly Func<bool> diagnosticsEnabled;
    private readonly HashSet<string> reportedDiagnostics = new HashSet<string>(StringComparer.Ordinal);

    public MissingTextTracker(ManualLogSource logger, Func<bool> diagnosticsEnabled)
    {
        this.logger = logger;
        this.diagnosticsEnabled = diagnosticsEnabled;
    }

    public void RecordMiss(string category, string key, string original)
    {
        if (string.IsNullOrEmpty(original))
        {
            return;
        }

        RecordDevelopmentDiagnostic(
            "miss|" + category + "|" + key + "|" + original,
            "Missing localization [" + category + "] key='" + key + "' original='" + Abbreviate(original) + "'. Preserving original.");
    }

    public void RecordMalformedRow(string path, int rowNumber, string reason)
    {
        RecordDevelopmentDiagnostic(
            "malformed-row|" + path + "|" + rowNumber + "|" + reason,
            "Malformed localization row " + path + ":" + rowNumber + " - " + reason + " Preserving original at runtime.");
    }

    public void RecordResourceIssue(string key, string message)
    {
        RecordDevelopmentDiagnostic("resource|" + key + "|" + message, message);
    }

    private void RecordDevelopmentDiagnostic(string key, string message)
    {
        if (diagnosticsEnabled == null || !diagnosticsEnabled())
        {
            return;
        }

        if (reportedDiagnostics.Add(key) && logger != null)
        {
            logger.LogDebug(message);
        }
    }

    private static string Abbreviate(string value)
    {
        if (value == null)
        {
            return string.Empty;
        }

        const int maxLength = 160;
        string flattened = value.Replace("\r", "\\r").Replace("\n", "\\n");
        if (flattened.Length <= maxLength)
        {
            return flattened;
        }

        return flattened.Substring(0, maxLength) + "...";
    }
}
