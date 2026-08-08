import csv
from pathlib import Path
import unittest


PROJECT = Path(__file__).resolve().parents[1]
EXPRESSION = '((gS.homeworkFloor == 3) ? "third" : "fifth")'


def _render_dynamic_template(template, expression, replacement):
    expression_index = template.find(expression)
    if expression_index >= 0:
        plus_before = template.rfind("+", 0, expression_index + 1)
        plus_after = template.find("+", expression_index + len(expression))
        if plus_before < 0 or plus_after < 0:
            return None

        prefix = template[:plus_before].rstrip()
        if prefix.endswith('"'):
            prefix = prefix[:-1]
        suffix = template[plus_after + 1:].lstrip()
        if suffix.startswith('"'):
            suffix = suffix[1:]
        return prefix + replacement + suffix

    placeholder_start = template.find("{EXPR_")
    if placeholder_start < 0:
        return None
    placeholder_end = template.find("}", placeholder_start + len("{EXPR_"))
    if placeholder_end < 0:
        return None
    return template[:placeholder_start] + replacement + template[placeholder_end + 1:]


class Task4DynamicTextTests(unittest.TestCase):
    def test_existing_dynamic_item_row_renders_the_runtime_fifth_floor_sentence(self):
        path = PROJECT / "resources" / "work" / "approved-translations" / "item.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            row = next(row for row in csv.reader(handle) if row and row[0] == "15700|||5290")

        runtime_original = (
            "Yes, Detective. Yesterday evening, at about nine PM, Mr. Thompson was in the "
            "university building, section B2, on the fifth floor, standing by an open window. "
            'Presumably doing some "cognitive behavioral therapy" exercise.'
        )
        expected_translation = (
            "是的，侦探。昨晚大约九点，汤普森先生在大学大楼 B2 区的第五层，站在一扇开着的窗边。"
            "推测当时正在进行某种 \"认知行为疗法\" 练习。"
        )

        self.assertEqual(_render_dynamic_template(row[1], EXPRESSION, "fifth"), runtime_original)
        self.assertEqual(_render_dynamic_template(row[2], EXPRESSION, "第五"), expected_translation)

        self.assertIn("on the third floor", _render_dynamic_template(row[1], EXPRESSION, "third"))
        self.assertIn("的第三层", _render_dynamic_template(row[2], EXPRESSION, "第三"))

    def test_dynamic_template_supports_the_current_extractor_placeholder(self):
        source = "A {EXPR_1} B"
        translation = "甲{EXPR_1}乙"

        self.assertEqual(_render_dynamic_template(source, EXPRESSION, "third"), "A third B")
        self.assertEqual(_render_dynamic_template(translation, EXPRESSION, "第三"), "甲第三乙")

    def test_dynamic_dialogue_uses_a_targeted_update_situation_hook(self):
        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")
        manager = (PROJECT / "TranslationManager.cs").read_text(encoding="utf-8-sig")

        self.assertIn(
            '[HarmonyPatch(typeof(global::GameManager), nameof(global::GameManager.updateSituationView))]',
            patches,
        )
        self.assertIn("DynamicHomeworkItemKey", patches)
        self.assertIn("TryTranslateDynamicTemplate", patches)
        self.assertIn("homeworkFloor == 3", patches)
        self.assertIn("IsDynamicPlaceholder", patches)
        self.assertIn("public bool TryTranslateDynamicTemplate", manager)
        self.assertNotIn("TMP_Text.text", patches)

    def test_dynamic_josh_dialogue_is_retranslated_after_the_game_callback(self):
        path = PROJECT / "resources" / "work" / "approved-translations" / "dialogue.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            row = next(row for row in csv.reader(handle) if row and row[0] == "19340|||JOSH|||8639")

        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertTrue(row[2])
        self.assertIn("DynamicJoshNodeId", patches)
        self.assertIn('private const string DynamicJoshSpeaker = "JOSH";', patches)
        self.assertIn("TranslateDynamicJoshText(__instance);", patches)
        self.assertIn("TryTranslateRuntimeKey(DialogueCategory, runtimeKey, sitItem.text", patches)

    def test_dynamic_deborah_items_are_retranslated_after_the_game_callback(self):
        path = PROJECT / "resources" / "work" / "approved-translations" / "item.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = {
                row[0]: row
                for row in csv.reader(handle)
                if row and row[0].startswith("2820|||")
            }

        patches = (PROJECT / "GamePatches.cs").read_text(encoding="utf-8-sig")

        self.assertEqual(set(rows), {"2820|||3241", "2820|||3245", "2820|||3249", "2820|||3253"})
        self.assertTrue(all(row[2] for row in rows.values()))
        self.assertIn("DynamicDeborahNodeId", patches)
        self.assertIn('private const string DynamicDeborahPlaceholder = "[DECIDE DYNAMICALLY]";', patches)
        self.assertIn("TranslateDynamicDeborahText(__instance);", patches)
        self.assertIn("TryTranslateByOriginal(ItemCategory, sitItem.text", patches)


if __name__ == "__main__":
    unittest.main()
