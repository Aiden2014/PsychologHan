import unittest

from scripts.apply_client_info_translation import (
    DEATH_NOTICE, DEATH_NOTICE_TRANSLATION, TRANSLATIONS, translate_rows,
)


class ClientInfoTranslationTests(unittest.TestCase):
    def test_death_notices_preserve_reviewed_translations_and_ordinary_alignment(self):
        source = [[str(index), "Original " + str(index), ""] for index in range(len(TRANSLATIONS))]
        reviewed = [[row[0], row[1], "已审校" + row[0]] for row in source]
        for client in ("Vera", "Jaden", "Joe", "Deborah", "Ashley"):
            for field in ("trustComment", "treatmentComment"):
                source.insert(12, [field + client, DEATH_NOTICE, ""])
        result = translate_rows(source, reviewed)
        self.assertEqual(len(result), 60)
        for key, original, translated in result:
            self.assertEqual(translated, DEATH_NOTICE_TRANSLATION if original == DEATH_NOTICE else "已审校" + key)
        fallback = translate_rows(source, [])
        self.assertEqual([row[2] for row in fallback if row[1] != DEATH_NOTICE], TRANSLATIONS)
        self.assertEqual(translate_rows(source, result), result)

    def test_unexpected_source_rows_fail_before_writing_translations(self):
        with self.assertRaises(ValueError):
            translate_rows([["unknown", "Changed source", ""]], [])


if __name__ == "__main__":
    unittest.main()
