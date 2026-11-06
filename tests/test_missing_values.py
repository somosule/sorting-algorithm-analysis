"""Tests for the what-if extension in src/missing_values.py (D05, D23)."""
import csv
import unittest

from src import config
from src.missing_values import bedrooms_column, estimate_missing_bedrooms


class TestMissingValues(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comparison = {item["version"]: item for item in estimate_missing_bedrooms(config.DATA_PATH)}
        with open(config.RESULTS_DIR / "total_bedrooms_filled.csv", encoding="utf-8") as file:
            cls.filled = list(csv.DictReader(file))

    def test_all_207_blanks_estimated(self):
        self.assertEqual(len(self.filled), 207)
        self.assertEqual(self.comparison["after: ratio estimate (households)"]["values"], 20640)
        self.assertEqual(self.comparison["after: ratio estimate (households)"]["missing"], 0)

    def test_worked_example(self):
        # Row 291: 218 households in NEAR BAY: 218 x 1.0466 = 228.2, so 228 bedrooms.
        match = [r for r in self.filled if r["row_number"] == "291"]
        self.assertEqual(match[0]["ocean_proximity"], "NEAR BAY")
        self.assertEqual(float(match[0]["households"]), 218.0)
        self.assertEqual(int(match[0]["estimate"]), 228)

    def test_households_ratio_is_most_accurate(self):
        with open(config.RESULTS_DIR / "total_bedrooms_method_check.csv", encoding="utf-8") as file:
            check = {r["method"]: float(r["median_abs_pct_error"]) for r in csv.DictReader(file)}
        self.assertLess(check["ratio to households"], check["ratio to total_rooms"])
        self.assertLess(check["ratio to total_rooms"], check["single median fill"])

    def test_median_fill_creates_more_duplicates(self):
        ratio = self.comparison["after: ratio estimate (households)"]
        single = self.comparison["after: single median fill"]
        self.assertGreater(single["most_frequent_count"], ratio["most_frequent_count"])

    def test_housing_csv_unchanged(self):
        with open(config.DATA_PATH, encoding="utf-8") as file:
            blanks = sum(1 for row in csv.DictReader(file) if not row["total_bedrooms"].strip())
        self.assertEqual(blanks, 207)


class TestBedroomsColumn(unittest.TestCase):
    """bedrooms_column() gives the three versions used by the interactive mode."""

    def test_skip_matches_the_loader(self):
        from src.load_data import load_column
        self.assertEqual(bedrooms_column(config.DATA_PATH, "skip"),
                         load_column(config.DATA_PATH, "total_bedrooms"))

    def test_ratio_and_median_fill_every_blank(self):
        for method in ("ratio", "median"):
            with self.subTest(method=method):
                values, missing = bedrooms_column(config.DATA_PATH, method)
                self.assertEqual(len(values), 20640)
                self.assertEqual(missing, 0)

    def test_median_fill_adds_207_copies_of_435(self):
        values, _ = bedrooms_column(config.DATA_PATH, "median")
        self.assertEqual(values.count(435.0), 244)  # 37 real + 207 filled

    def test_unknown_method_raises(self):
        with self.assertRaises(ValueError):
            bedrooms_column(config.DATA_PATH, "interpolate")


if __name__ == "__main__":
    unittest.main()
