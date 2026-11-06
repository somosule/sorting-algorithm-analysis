"""Tests for src/data_profile.py (profile_dataset and duplication_stats).

Run from the repo root with: python3 -m unittest discover -v
"""
import unittest

from src import config
from src.data_profile import duplication_stats, profile_dataset


class TestDuplicationStats(unittest.TestCase):
    """duplication_stats() gives the agreed figures (D07, D20)."""

    def test_agreed_example(self):
        result = duplication_stats([1, 1, 2, 3, 3, 3])
        self.assertEqual(result["distinct_values"], 3)
        self.assertEqual(result["most_frequent_value"], 3)
        self.assertEqual(result["most_frequent_count"], 3)
        self.assertEqual(result["values_repeated"], 2)
        self.assertEqual(result["elements_in_repeats"], 5)
        self.assertEqual(result["equal_pairs"], 4)  # 1 pair of 1s + 3 pairs of 3s

    def test_empty_list_gives_zeros(self):
        result = duplication_stats([])
        for key in ("distinct_values", "most_frequent_count", "values_repeated",
                    "elements_in_repeats", "equal_pairs"):
            with self.subTest(key=key):
                self.assertEqual(result[key], 0)
        self.assertIsNone(result["most_frequent_value"])

    def test_all_equal_values(self):
        result = duplication_stats([7.0] * 5)
        self.assertEqual(result["distinct_values"], 1)
        self.assertEqual(result["most_frequent_count"], 5)
        self.assertEqual(result["elements_in_repeats"], 5)
        self.assertEqual(result["equal_pairs"], 10)  # 5 x 4 / 2

    def test_input_unchanged(self):
        values = [3.0, 1.0, 3.0]
        duplication_stats(values)
        self.assertEqual(values, [3.0, 1.0, 3.0])


class TestProfileDataset(unittest.TestCase):
    """profile_dataset() reports the real figures for housing.csv (brief Section 3)."""

    @classmethod
    def setUpClass(cls):
        # Runs once; profile_dataset also prints a table and saves dataset_summary.csv.
        summary = profile_dataset(config.DATA_PATH)
        cls.by_column = {item["column"]: item for item in summary}

    def test_every_column_has_20640_rows(self):
        for column, item in self.by_column.items():
            with self.subTest(column=column):
                self.assertEqual(item["rows"], 20640)

    def test_experiment_columns_have_no_missing_values(self):
        for column in config.COLUMNS:
            with self.subTest(column=column):
                self.assertEqual(self.by_column[column]["missing"], 0)

    def test_total_bedrooms_has_207_missing(self):
        self.assertEqual(self.by_column["total_bedrooms"]["missing"], 207)

    def test_distinct_values(self):
        expected = {"median_income": 12928, "housing_median_age": 52,
                    "median_house_value": 3842}
        for column, distinct in expected.items():
            with self.subTest(column=column):
                self.assertEqual(self.by_column[column]["distinct"], distinct)

    def test_house_value_cap(self):
        item = self.by_column["median_house_value"]
        self.assertEqual(item["max"], 500001.0)
        self.assertEqual(item["cap_count"], 965)


if __name__ == "__main__":
    unittest.main()
