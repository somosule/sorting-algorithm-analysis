"""Tests for the record lookup extension (src/record_lookup.py, D08)."""
import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src import config
from src.record_lookup import find_top_records, sort_row_numbers, top_records


class TestSortRowNumbers(unittest.TestCase):

    def test_sorts_by_value(self):
        pairs = [(0, 3.0), (1, 1.0), (2, 2.0)]
        self.assertEqual(sort_row_numbers(pairs), [(1, 1.0), (2, 2.0), (0, 3.0)])

    def test_stable_for_equal_values(self):
        pairs = [(0, 5.0), (1, 2.0), (2, 5.0), (3, 2.0)]
        self.assertEqual([n for n, _ in sort_row_numbers(pairs)], [1, 3, 0, 2])

    def test_input_unchanged(self):
        pairs = [(0, 2.0), (1, 1.0)]
        sort_row_numbers(pairs)
        self.assertEqual(pairs, [(0, 2.0), (1, 1.0)])


class TestTopRecords(unittest.TestCase):

    def test_matches_the_data(self):
        results = find_top_records(config.DATA_PATH, "median_income", k=5)
        with open(config.DATA_PATH, encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        expected = sorted(range(len(rows)), key=lambda i: -float(rows[i]["median_income"]))[:5]
        self.assertEqual([r["csv_line"] for r in results], [i + 2 for i in expected])
        self.assertEqual(results[0]["median_income"], 15.0001)

    def test_ties_keep_file_order(self):
        results = find_top_records(config.DATA_PATH, "median_house_value", k=3)
        lines = [r["csv_line"] for r in results]
        self.assertTrue(all(r["median_house_value"] == 500001.0 for r in results))
        self.assertEqual(lines, sorted(lines))

    def test_blanks_are_skipped(self):
        results = find_top_records(config.DATA_PATH, "total_bedrooms", k=3)
        self.assertEqual(len(results), 3)

    def test_saves_the_file(self):
        # Written to a temporary folder, so the official results file is never touched.
        with tempfile.TemporaryDirectory() as directory:
            results_dir = Path(directory)
            with patch.object(config, "RESULTS_DIR", results_dir):
                with redirect_stdout(io.StringIO()):
                    results = top_records(config.DATA_PATH, "median_income", k=2)
            with open(results_dir / "top_records.csv", encoding="utf-8") as file:
                saved = list(csv.DictReader(file))
        self.assertEqual(len(saved), 2)
        self.assertEqual([int(row["csv_line"]) for row in saved], [r["csv_line"] for r in results])


if __name__ == "__main__":
    unittest.main()
