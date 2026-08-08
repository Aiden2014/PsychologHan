from pathlib import Path
import unittest


PROJECT = Path(__file__).resolve().parents[1]


def _normalize_newlines(value):
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _runtime_alias(entries, runtime_key, runtime_original):
    """Python mirror of the required Task 4 runtime alias contract."""
    runtime_parts = runtime_key.split("|||")
    assert len(runtime_parts) >= 3
    runtime_prefix = "|||".join(runtime_parts[:2])
    matches = [
        translation
        for key, original, translation in entries
        if "|||".join(key.split("|||")[:2]) == runtime_prefix
        and _normalize_newlines(original) == _normalize_newlines(runtime_original)
    ]
    return matches[0] if len(matches) == 1 else runtime_original


class Task4RuntimeAliasTests(unittest.TestCase):
    def test_runtime_dialogue_alias_matches_extracted_source_line_key(self):
        entries = [
            ("14100|||ME|||2190", "I haven't walked this way home before.", "我以前没走过这条回家的路。"),
        ]

        self.assertEqual(
            _runtime_alias(entries, "14100|||ME|||14100", "I haven't walked this way home before."),
            "我以前没走过这条回家的路。",
        )

    def test_runtime_choice_alias_matches_extracted_source_line_key(self):
        entries = [
            ("14104|||14104|||2200", "continueDownTheStreet2", "继续沿街走"),
        ]

        self.assertEqual(_runtime_alias(entries, "14104|||14104|||14104", "continueDownTheStreet2"), "继续沿街走")

    def test_runtime_choice_alias_matches_all_newline_forms(self):
        cases = [
            (
                "14400|||14401|||2335",
                "14400|||14401|||14401",
                "That reminded me of a teacher",
                "I had in first grade.",
                "这让我想起了一位老师，",
                "我一年级时的老师。",
            ),
            (
                "14400|||14402|||2336",
                "14400|||14402|||14402",
                "If you were to continue the",
                "story, what happens next?",
                "如果你要把这个故事继续讲下去，",
                "接下来会发生什么？",
            ),
        ]
        separators = ("\n", "\r\n", "\r")

        for csv_separator in separators:
            entries = [
                (
                    key,
                    first + csv_separator + second,
                    translated_first + csv_separator + translated_second,
                )
                for key, _, first, second, translated_first, translated_second in cases
            ]
            for runtime_separator in separators:
                for key, runtime_key, first, second, _, _ in cases:
                    with self.subTest(csv_separator=repr(csv_separator), runtime_separator=repr(runtime_separator), key=key):
                        self.assertEqual(
                            _runtime_alias(entries, runtime_key, first + runtime_separator + second),
                            next(translation for entry_key, _, translation in entries if entry_key == key),
                        )

    def test_runtime_alias_preserves_original_when_ambiguous(self):
        entries = [
            ("14100|||ME|||2190", "Same\r\nline.", "译文一"),
            ("14100|||ME|||2191", "Same\nline.", "译文二"),
        ]

        self.assertEqual(_runtime_alias(entries, "14100|||ME|||14100", "Same\rline."), "Same\rline.")

    def test_csharp_uses_runtime_alias_lookup_for_dialogue_and_choice_prefixes(self):
        manager = (PROJECT / "TranslationManager.cs").read_text(encoding="utf-8-sig")
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")
        ui_patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("TryTranslateRuntimeKey", manager)
        self.assertIn("FirstTwoSegmentPrefix", manager)
        self.assertIn("NormalizeNewlines", manager)
        self.assertIn("OriginalsMatch", manager)
        self.assertIn("RecordAmbiguousAlias", manager)
        self.assertIn("TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory", patches)
        self.assertIn('TranslateRuntimeOrOriginal("choice", choiceKey, original)', ui_patches)

    def test_choice_patch_preserves_pac_button_identity_and_translates_display_text_later(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")
        ui_patches = (PROJECT / "UiPatches.cs").read_text(encoding="utf-8-sig")

        self.assertNotIn("text = TranslateRuntimeKeyOrOriginal(ChoiceCategory", patches)
        self.assertIn("TranslateChoiceButtons(__instance);", ui_patches)
        self.assertIn('TranslateRuntimeOrOriginal("choice", choiceKey, original)', ui_patches)
