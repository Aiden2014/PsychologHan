from pathlib import Path
import unittest


PROJECT = Path(__file__).resolve().parents[1]


def _runtime_alias(entries, runtime_key, runtime_original):
    """Python mirror of the required Task 4 runtime alias contract."""
    runtime_parts = runtime_key.split("|||")
    assert len(runtime_parts) >= 3
    runtime_prefix = "|||".join(runtime_parts[:2])
    matches = [
        translation
        for key, original, translation in entries
        if "|||".join(key.split("|||")[:2]) == runtime_prefix
        and original == runtime_original
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

    def test_runtime_alias_preserves_original_when_ambiguous(self):
        entries = [
            ("14100|||ME|||2190", "Same line.", "译文一"),
            ("14100|||ME|||2191", "Same line.", "译文二"),
        ]

        self.assertEqual(_runtime_alias(entries, "14100|||ME|||14100", "Same line."), "Same line.")

    def test_csharp_uses_runtime_alias_lookup_for_dialogue_and_choice_prefixes(self):
        manager = (PROJECT / "TranslationManager.cs").read_text(encoding="utf-8-sig")
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertIn("TryTranslateRuntimeKey", manager)
        self.assertIn("FirstTwoSegmentPrefix", manager)
        self.assertIn("RecordAmbiguousAlias", manager)
        self.assertIn("TranslateRuntimeKeyWithOptionalOriginalFallback(DialogueCategory", patches)
        self.assertIn("TranslateRuntimeKeyOrOriginal(ChoiceCategory", patches)
