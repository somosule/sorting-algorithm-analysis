"""Tests for src/load_data.py (load_rows and load_column).

Run from the repo root with: python -m unittest discover -v
"""
import csv
import os
import tempfile
import unittest

from src import config
from src.load_data import load_column, load_rows

ROWS_IN_DATASET = 20640


class TestRealDataset(unittest.TestCase):
    """Checks against the real housing.csv."""

    def test_load_rows_returns_every_row(self):
        rows = load_rows(config.DATA_PATH)
        self.assertEqual(len(rows), ROWS_IN_DATASET)
        self.assertIsInstance(rows[0], dict)
        self.assertEqual(len(rows[0]), 10)

    def test_experiment_columns_have_no_missing_values(self):
        for column in config.COLUMNS:
            with self.subTest(column=column):
                values, missing = load_column(config.DATA_PATH, column)
                self.assertEqual(len(values), ROWS_IN_DATASET)
                self.assertEqual(missing, 0)
                self.assertTrue(all(isinstance(v, float) for v in values))

    def test_total_bedrooms_has_207_missing(self):
        values, missing = load_column(config.DATA_PATH, "total_bedrooms")
        self.assertEqual(missing, 207)
        self.assertEqual(len(values) + missing, ROWS_IN_DATASET)

    def test_values_keep_file_order(self):
        rows = load_rows(config.DATA_PATH)
        values, _ = load_column(config.DATA_PATH, "median_income")
        first_five = [float(row["median_income"]) for row in rows[:5]]
        self.assertEqual(values[:5], first_five)

    def test_text_column_counts_every_entry_as_missing(self):
        values, missing = load_column(config.DATA_PATH, "ocean_proximity")
        self.assertEqual(values, [])
        self.assertEqual(missing, ROWS_IN_DATASET)

    def test_two_loads_give_identical_results(self):
        first = load_column(config.DATA_PATH, "median_income")
        second = load_column(config.DATA_PATH, "median_income")
        self.assertEqual(first, second)


class TestErrors(unittest.TestCase):
    """A wrong column or path must fail loudly, never return empty data."""

    def test_misspelled_column_raises_key_error(self):
        with self.assertRaises(KeyError):
            load_column(config.DATA_PATH, "median_incme")

    def test_missing_file_raises_file_not_found(self):
        missing_path = os.path.join(tempfile.gettempdir(), "no_such_file.csv")
        with self.assertRaises(FileNotFoundError) as context:
            load_rows(missing_path)
        self.assertIn("See README", str(context.exception))

    def test_load_column_on_missing_file_raises_file_not_found(self):
        missing_path = os.path.join(tempfile.gettempdir(), "no_such_file.csv")
        with self.assertRaises(FileNotFoundError):
            load_column(missing_path, "median_income")


class TestSmallFile(unittest.TestCase):
    """Edge cases on a small file written for the test."""

    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".csv")
        os.close(handle)
        with open(self.path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["a", "b"])
            writer.writerow(["1.5", "x"])
            writer.writerow(["", "2"])
            writer.writerow([" 3 ", "abc"])
            writer.writerow(["-4", "5"])

    def tearDown(self):
        os.remove(self.path)

    def test_blanks_and_text_are_counted_and_skipped(self):
        values, missing = load_column(self.path, "a")
        self.assertEqual(values, [1.5, 3.0, -4.0])
        self.assertEqual(missing, 1)

        values, missing = load_column(self.path, "b")
        self.assertEqual(values, [2.0, 5.0])
        self.assertEqual(missing, 2)


if __name__ == "__main__":
    unittest.main()
