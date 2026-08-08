using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace PsychologHan;

public sealed class TranslationManager
{
    private static readonly string[] ApprovedCsvFiles =
    {
        "dialogue.csv",
        "choice.csv",
        "character_name.csv",
        "item.csv",
        "client_info.csv",
        "ending.csv",
        "ui.csv"
    };

    private readonly Dictionary<string, Dictionary<string, TranslationEntry>> translationsByCategory =
        new Dictionary<string, Dictionary<string, TranslationEntry>>(StringComparer.Ordinal);

    private readonly Dictionary<string, Dictionary<string, List<TranslationEntry>>> runtimeAliasesByCategory =
        new Dictionary<string, Dictionary<string, List<TranslationEntry>>>(StringComparer.Ordinal);

    private readonly Dictionary<string, Dictionary<string, string>> originalsByCategory =
        new Dictionary<string, Dictionary<string, string>>(StringComparer.Ordinal);

    private readonly Dictionary<string, HashSet<string>> ambiguousOriginalsByCategory =
        new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);

    private readonly Dictionary<string, Dictionary<string, string>> normalizedOriginalsByCategory =
        new Dictionary<string, Dictionary<string, string>>(StringComparer.Ordinal);

    private readonly Dictionary<string, HashSet<string>> ambiguousNormalizedOriginalsByCategory =
        new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);

    private readonly MissingTextTracker diagnostics;

    private TranslationManager(MissingTextTracker diagnostics)
    {
        this.diagnostics = diagnostics;
    }

    public int FileCount { get; private set; }

    public int EntryCount { get; private set; }

    public static TranslationManager Load(string localizationDirectory, MissingTextTracker diagnostics)
    {
        TranslationManager manager = new TranslationManager(diagnostics);

        if (string.IsNullOrEmpty(localizationDirectory) || !Directory.Exists(localizationDirectory))
        {
            diagnostics.RecordResourceIssue(
                "localization-directory-missing",
                "Plugin-local localization directory is absent; all game text will remain original.");
            return manager;
        }

        foreach (string csvFile in ApprovedCsvFiles)
        {
            string path = Path.Combine(localizationDirectory, csvFile);
            if (File.Exists(path))
            {
                manager.LoadCsv(path, Path.GetFileNameWithoutExtension(csvFile));
            }
        }

        if (manager.FileCount == 0)
        {
            diagnostics.RecordResourceIssue(
                "localization-files-missing",
                "No approved CSV files were found in the plugin-local localization directory; all game text will remain original.");
        }

        return manager;
    }

    public bool HasCategory(string category)
    {
        return !string.IsNullOrEmpty(category) && translationsByCategory.ContainsKey(category);
    }

    public string TranslateOrOriginal(string key, string original)
    {
        string translated;
        if (TryTranslate(key, original, out translated))
        {
            return translated;
        }

        diagnostics.RecordMiss("any", key, original);
        return original;
    }

    public string TranslateOrOriginal(string category, string key, string original)
    {
        string translated;
        if (TryTranslate(category, key, original, out translated))
        {
            return translated;
        }

        diagnostics.RecordMiss(category, key, original);
        return original;
    }

    public string TranslateRuntimeOrOriginal(string category, string runtimeKey, string original)
    {
        string translated;
        if (TryTranslateRuntimeKey(category, runtimeKey, original, out translated))
        {
            return translated;
        }

        diagnostics.RecordMiss(category, runtimeKey, original);
        return original;
    }

    public bool TryTranslate(string key, string original, out string translated)
    {
        translated = null;
        if (string.IsNullOrEmpty(key))
        {
            return false;
        }

        foreach (KeyValuePair<string, Dictionary<string, TranslationEntry>> category in translationsByCategory)
        {
            if (TryTranslate(category.Key, key, original, out translated))
            {
                return true;
            }
        }

        return false;
    }

    public bool TryTranslate(string category, string key, string original, out string translated)
    {
        translated = null;
        if (string.IsNullOrEmpty(category) || string.IsNullOrEmpty(key))
        {
            return false;
        }

        TranslationEntry entry;
        if (!TryGetExactEntry(category, key, out entry))
        {
            return false;
        }

        if (!OriginalsMatch(entry.Original, original))
        {
            diagnostics.RecordMiss(category, key, original);
            return false;
        }

        translated = entry.Translation;
        return true;
    }

    public bool TryTranslateRuntimeKey(string category, string runtimeKey, string original, out string translated)
    {
        translated = null;
        if (string.IsNullOrEmpty(category) || string.IsNullOrEmpty(runtimeKey))
        {
            return false;
        }

        TranslationEntry exactEntry;
        if (TryGetExactEntry(category, runtimeKey, out exactEntry) &&
            OriginalsMatch(exactEntry.Original, original))
        {
            translated = exactEntry.Translation;
            return true;
        }

        string aliasPrefix = FirstTwoSegmentPrefix(runtimeKey);
        if (aliasPrefix == null)
        {
            return false;
        }

        Dictionary<string, List<TranslationEntry>> aliases;
        if (!runtimeAliasesByCategory.TryGetValue(category, out aliases))
        {
            return false;
        }

        List<TranslationEntry> candidates;
        if (!aliases.TryGetValue(aliasPrefix, out candidates))
        {
            return false;
        }

        TranslationEntry matchedEntry = null;
        int matchedEntryCount = 0;
        foreach (TranslationEntry candidate in candidates)
        {
            if (OriginalsMatch(candidate.Original, original))
            {
                matchedEntry = candidate;
                matchedEntryCount++;
            }
        }

        if (matchedEntryCount == 1)
        {
            translated = matchedEntry.Translation;
            return true;
        }

        if (matchedEntryCount > 1)
        {
            diagnostics.RecordAmbiguousAlias(category, runtimeKey, original, matchedEntryCount);
        }

        return false;
    }

    public bool TryTranslateDynamicTemplate(
        string category,
        string key,
        string original,
        string expression,
        string originalValue,
        string translatedValue,
        out string translated)
    {
        translated = null;
        if (string.IsNullOrEmpty(category) || string.IsNullOrEmpty(key) ||
            string.IsNullOrEmpty(original) || string.IsNullOrEmpty(expression) ||
            originalValue == null || translatedValue == null)
        {
            return false;
        }

        TranslationEntry entry;
        if (!TryGetExactEntry(category, key, out entry))
        {
            return false;
        }

        if (OriginalsMatch(entry.Original, original))
        {
            translated = entry.Translation;
            return true;
        }

        string renderedOriginal = RenderDynamicTemplate(entry.Original, expression, originalValue);
        if (renderedOriginal == null || !OriginalsMatch(renderedOriginal, original))
        {
            return false;
        }

        string renderedTranslation = RenderDynamicTemplate(entry.Translation, expression, translatedValue);
        if (renderedTranslation == null)
        {
            return false;
        }

        translated = renderedTranslation;
        return true;
    }

    private bool TryGetExactEntry(string category, string key, out TranslationEntry entry)
    {
        entry = null;
        Dictionary<string, TranslationEntry> translations;
        if (!translationsByCategory.TryGetValue(category, out translations))
        {
            return false;
        }

        return translations.TryGetValue(key, out entry);
    }

    private static string RenderDynamicTemplate(string template, string expression, string replacement)
    {
        if (string.IsNullOrEmpty(template) || string.IsNullOrEmpty(expression) || replacement == null)
        {
            return null;
        }

        int expressionIndex = template.IndexOf(expression, StringComparison.Ordinal);
        if (expressionIndex >= 0)
        {
            int plusBefore = template.LastIndexOf('+', expressionIndex);
            int plusAfter = template.IndexOf('+', expressionIndex + expression.Length);
            if (plusBefore < 0 || plusAfter < 0)
            {
                return null;
            }

            string prefix = template.Substring(0, plusBefore).TrimEnd();
            if (prefix.EndsWith("\"", StringComparison.Ordinal))
            {
                prefix = prefix.Substring(0, prefix.Length - 1);
            }

            string suffix = template.Substring(plusAfter + 1).TrimStart();
            if (suffix.StartsWith("\"", StringComparison.Ordinal))
            {
                suffix = suffix.Substring(1);
            }

            return prefix + replacement + suffix;
        }

        int placeholderStart = template.IndexOf("{EXPR_", StringComparison.Ordinal);
        if (placeholderStart < 0)
        {
            return null;
        }

        int placeholderEnd = template.IndexOf('}', placeholderStart + "{EXPR_".Length);
        if (placeholderEnd < 0)
        {
            return null;
        }

        return template.Substring(0, placeholderStart) + replacement +
            template.Substring(placeholderEnd + 1);
    }

    public bool TryTranslateByOriginal(string category, string original, out string translated)
    {
        translated = null;
        if (string.IsNullOrEmpty(category) || string.IsNullOrEmpty(original))
        {
            return false;
        }

        string normalizedOriginal = NormalizeNewlines(original);
        HashSet<string> ambiguousNormalizedOriginals;
        if (ambiguousNormalizedOriginalsByCategory.TryGetValue(category, out ambiguousNormalizedOriginals) &&
            ambiguousNormalizedOriginals.Contains(normalizedOriginal))
        {
            diagnostics.RecordMiss(category, "<ambiguous-normalized-original-fallback>", original);
            return false;
        }

        HashSet<string> ambiguousOriginals;
        if (ambiguousOriginalsByCategory.TryGetValue(category, out ambiguousOriginals) &&
            ambiguousOriginals.Contains(original))
        {
            diagnostics.RecordMiss(category, "<ambiguous-original-fallback>", original);
            return false;
        }

        Dictionary<string, string> originals;
        if (originalsByCategory.TryGetValue(category, out originals) && originals.TryGetValue(original, out translated))
        {
            return true;
        }

        Dictionary<string, string> normalizedOriginals;
        return normalizedOriginalsByCategory.TryGetValue(category, out normalizedOriginals) &&
            normalizedOriginals.TryGetValue(normalizedOriginal, out translated);
    }

    private void LoadCsv(string path, string category)
    {
        string content;
        try
        {
            using (StreamReader reader = new StreamReader(
                path,
                new UTF8Encoding(encoderShouldEmitUTF8Identifier: false, throwOnInvalidBytes: true),
                detectEncodingFromByteOrderMarks: true))
            {
                content = reader.ReadToEnd();
            }
        }
        catch (Exception ex) when (ex is IOException || ex is UnauthorizedAccessException || ex is DecoderFallbackException)
        {
            diagnostics.RecordResourceIssue(path, "Could not read localization CSV: " + ex.Message);
            return;
        }

        List<List<string>> rows;
        try
        {
            rows = ParseCsv(content);
        }
        catch (FormatException ex)
        {
            diagnostics.RecordResourceIssue(path, "Malformed CSV resource: " + ex.Message);
            return;
        }

        int loadedFromFile = 0;
        for (int index = 0; index < rows.Count; index++)
        {
            List<string> row = rows[index];
            int rowNumber = index + 1;
            if (row.Count != 3)
            {
                diagnostics.RecordMalformedRow(path, rowNumber, "Expected exactly 3 columns: key, original, translation.");
                continue;
            }

            string key = StripBom(row[0]);
            string original = row[1];
            string translation = row[2];
            if (string.IsNullOrEmpty(key) || string.IsNullOrEmpty(translation))
            {
                diagnostics.RecordMalformedRow(path, rowNumber, "Key or translation is empty.");
                continue;
            }

            if (AddTranslation(category, key, original, translation, path, rowNumber))
            {
                loadedFromFile++;
            }
        }

        if (loadedFromFile > 0)
        {
            FileCount++;
            EntryCount += loadedFromFile;
        }
    }

    private bool AddTranslation(string category, string key, string original, string translation, string path, int rowNumber)
    {
        Dictionary<string, TranslationEntry> translations = GetTranslations(category);
        TranslationEntry existing;
        if (translations.TryGetValue(key, out existing))
        {
            if (!string.Equals(existing.Original, original, StringComparison.Ordinal) ||
                !string.Equals(existing.Translation, translation, StringComparison.Ordinal))
            {
                diagnostics.RecordMalformedRow(path, rowNumber, "Duplicate key with different original or translation; keeping first row.");
            }

            return false;
        }

        TranslationEntry entry = new TranslationEntry(key, original, translation);
        translations.Add(key, entry);
        AddRuntimeAlias(category, entry);
        AddOriginalFallback(category, original, translation, path, rowNumber);
        AddNormalizedOriginalFallback(category, original, translation, path, rowNumber);
        return true;
    }

    private void AddRuntimeAlias(string category, TranslationEntry entry)
    {
        string aliasPrefix = FirstTwoSegmentPrefix(entry.Key);
        if (aliasPrefix == null)
        {
            return;
        }

        Dictionary<string, List<TranslationEntry>> aliases = GetRuntimeAliases(category);
        List<TranslationEntry> candidates;
        if (!aliases.TryGetValue(aliasPrefix, out candidates))
        {
            candidates = new List<TranslationEntry>();
            aliases.Add(aliasPrefix, candidates);
        }

        candidates.Add(entry);
    }

    private Dictionary<string, List<TranslationEntry>> GetRuntimeAliases(string category)
    {
        Dictionary<string, List<TranslationEntry>> aliases;
        if (!runtimeAliasesByCategory.TryGetValue(category, out aliases))
        {
            aliases = new Dictionary<string, List<TranslationEntry>>(StringComparer.Ordinal);
            runtimeAliasesByCategory.Add(category, aliases);
        }

        return aliases;
    }

    private Dictionary<string, TranslationEntry> GetTranslations(string category)
    {
        Dictionary<string, TranslationEntry> translations;
        if (!translationsByCategory.TryGetValue(category, out translations))
        {
            translations = new Dictionary<string, TranslationEntry>(StringComparer.Ordinal);
            translationsByCategory.Add(category, translations);
        }

        return translations;
    }

    private void AddOriginalFallback(string category, string original, string translation, string path, int rowNumber)
    {
        if (string.IsNullOrEmpty(original))
        {
            return;
        }

        HashSet<string> ambiguousOriginals = GetAmbiguousOriginals(category);
        if (ambiguousOriginals.Contains(original))
        {
            return;
        }

        Dictionary<string, string> originals = GetOriginalFallbacks(category);
        string existing;
        if (originals.TryGetValue(original, out existing))
        {
            if (!string.Equals(existing, translation, StringComparison.Ordinal))
            {
                originals.Remove(original);
                ambiguousOriginals.Add(original);
                diagnostics.RecordMalformedRow(path, rowNumber, "Original text has multiple translations; category-scoped original fallback disabled for this text.");
            }

            return;
        }

        originals.Add(original, translation);
    }

    private Dictionary<string, string> GetOriginalFallbacks(string category)
    {
        Dictionary<string, string> originals;
        if (!originalsByCategory.TryGetValue(category, out originals))
        {
            originals = new Dictionary<string, string>(StringComparer.Ordinal);
            originalsByCategory.Add(category, originals);
        }

        return originals;
    }

    private HashSet<string> GetAmbiguousOriginals(string category)
    {
        HashSet<string> ambiguousOriginals;
        if (!ambiguousOriginalsByCategory.TryGetValue(category, out ambiguousOriginals))
        {
            ambiguousOriginals = new HashSet<string>(StringComparer.Ordinal);
            ambiguousOriginalsByCategory.Add(category, ambiguousOriginals);
        }

        return ambiguousOriginals;
    }

    private void AddNormalizedOriginalFallback(string category, string original, string translation, string path, int rowNumber)
    {
        if (string.IsNullOrEmpty(original))
        {
            return;
        }

        string normalizedOriginal = NormalizeNewlines(original);

        HashSet<string> ambiguousOriginals = GetAmbiguousNormalizedOriginals(category);
        if (ambiguousOriginals.Contains(normalizedOriginal))
        {
            return;
        }

        Dictionary<string, string> originals = GetNormalizedOriginalFallbacks(category);
        string existing;
        if (originals.TryGetValue(normalizedOriginal, out existing))
        {
            if (!string.Equals(existing, translation, StringComparison.Ordinal))
            {
                originals.Remove(normalizedOriginal);
                ambiguousOriginals.Add(normalizedOriginal);
                diagnostics.RecordMalformedRow(path, rowNumber, "Normalized original text has multiple translations; normalized original fallback disabled for this text.");
            }

            return;
        }

        originals.Add(normalizedOriginal, translation);
    }

    private Dictionary<string, string> GetNormalizedOriginalFallbacks(string category)
    {
        Dictionary<string, string> originals;
        if (!normalizedOriginalsByCategory.TryGetValue(category, out originals))
        {
            originals = new Dictionary<string, string>(StringComparer.Ordinal);
            normalizedOriginalsByCategory.Add(category, originals);
        }

        return originals;
    }

    private HashSet<string> GetAmbiguousNormalizedOriginals(string category)
    {
        HashSet<string> ambiguousOriginals;
        if (!ambiguousNormalizedOriginalsByCategory.TryGetValue(category, out ambiguousOriginals))
        {
            ambiguousOriginals = new HashSet<string>(StringComparer.Ordinal);
            ambiguousNormalizedOriginalsByCategory.Add(category, ambiguousOriginals);
        }

        return ambiguousOriginals;
    }

    private static bool OriginalsMatch(string expected, string actual)
    {
        if (string.Equals(expected, actual, StringComparison.Ordinal))
        {
            return true;
        }

        if (expected == null || actual == null)
        {
            return false;
        }

        return string.Equals(NormalizeNewlines(expected), NormalizeNewlines(actual), StringComparison.Ordinal);
    }

    private static string NormalizeNewlines(string value)
    {
        return value.Replace("\r\n", "\n").Replace("\r", "\n");
    }

    private static string StripBom(string value)
    {
        if (!string.IsNullOrEmpty(value) && value[0] == '\uFEFF')
        {
            return value.Substring(1);
        }

        return value;
    }

    private static string FirstTwoSegmentPrefix(string key)
    {
        if (string.IsNullOrEmpty(key))
        {
            return null;
        }

        int firstSeparator = key.IndexOf("|||", StringComparison.Ordinal);
        if (firstSeparator < 0)
        {
            return null;
        }

        int secondSeparator = key.IndexOf("|||", firstSeparator + 3, StringComparison.Ordinal);
        if (secondSeparator < 0)
        {
            return null;
        }

        return key.Substring(0, secondSeparator);
    }

    private static List<List<string>> ParseCsv(string content)
    {
        List<List<string>> rows = new List<List<string>>();
        List<string> row = new List<string>();
        StringBuilder field = new StringBuilder();
        bool inQuotes = false;

        for (int i = 0; i < content.Length; i++)
        {
            char current = content[i];
            if (inQuotes)
            {
                if (current == '"')
                {
                    if (i + 1 < content.Length && content[i + 1] == '"')
                    {
                        field.Append('"');
                        i++;
                    }
                    else
                    {
                        inQuotes = false;
                    }
                }
                else
                {
                    field.Append(current);
                }

                continue;
            }

            if (current == '"' && field.Length == 0)
            {
                inQuotes = true;
            }
            else if (current == ',')
            {
                row.Add(field.ToString());
                field.Clear();
            }
            else if (current == '\r' || current == '\n')
            {
                row.Add(field.ToString());
                field.Clear();
                rows.Add(row);
                row = new List<string>();
                if (current == '\r' && i + 1 < content.Length && content[i + 1] == '\n')
                {
                    i++;
                }
            }
            else
            {
                field.Append(current);
            }
        }

        if (inQuotes)
        {
            throw new FormatException("Unclosed quoted field.");
        }

        if (field.Length > 0 || row.Count > 0)
        {
            row.Add(field.ToString());
            rows.Add(row);
        }

        return rows;
    }

    private sealed class TranslationEntry
    {
        public TranslationEntry(string key, string original, string translation)
        {
            Key = key;
            Original = original;
            Translation = translation;
        }

        public string Key { get; }

        public string Original { get; }

        public string Translation { get; }
    }
}
