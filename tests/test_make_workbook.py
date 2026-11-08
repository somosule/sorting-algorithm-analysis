"""Tests for the results workbook (skipped if openpyxl is not installed)."""
import tempfile
import unittest
from pathlib import Path

from src import config

try:
    from openpyxl import load_workbook
    from src.make_workbook import QUESTIONS, _from_this_run, _label, make_workbook
except ImportError:  # openpyxl is optional, like matplotlib
    load_workbook = None


@unittest.skipIf(load_workbook is None, "openpyxl not installed")
class TestMakeWorkbook(unittest.TestCase):
    def test_labels_are_readable(self):
        self.assertEqual(_label("bubble_ms"), "Bubble (ms)")
        self.assertEqual(_label("median_runtime_s"), "Median runtime (s)")
        self.assertEqual(_label("n"), "n")

    def test_extension_tables_only_when_their_step_ran(self):
        self.assertTrue(_from_this_run("top_records.csv", "bubble-check, record-lookup"))
        self.assertFalse(_from_this_run("top_records.csv", "none"))
        self.assertFalse(_from_this_run("total_bedrooms_filled.csv", "record-lookup"))
        self.assertTrue(_from_this_run("memory.csv", "none"))

    def test_every_question_in_the_brief_is_listed(self):
        labels = " ".join(label for label, *_ in QUESTIONS)
        for number in range(3, 18):
            self.assertIn(f"Q{number}", labels)
        self.assertIn("Decision guide", labels)

    @unittest.skipUnless((config.RESULTS_DIR / "scaling.csv").exists(),
                         "no results yet: run python3 main.py first")
    def test_workbook_has_contents_questions_and_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = make_workbook(out_path=Path(directory) / "workbook.xlsx")
            book = load_workbook(path)
        for name in ("Contents", "Questions", "4.2 Scaling", "4.3 Input order",
                     "4.4 Repeated values", "Decision guide"):
            self.assertIn(name, book.sheetnames)
        questions = book["Questions"]
        self.assertEqual(questions.max_row, 4 + len(QUESTIONS))


if __name__ == "__main__":
    unittest.main()
