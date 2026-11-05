"""Tests for the what-if extension in src/missing_values.py (D05, D23)."""
import csv
import unittest

from src import config
from src.missing_values import estimate_missing_bedrooms


class TestMissingValues(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.comparison = {item["version"]: item for item in estimate_missing_bedrooms(config.DATA_PATH)}
        with open(config.RESULTS_DIR / "total_bedrooms_filled.csv", encoding="utf-8") as file:
            cls.filled = list(csv.DictReader(file))

    def test_all_207_blanks_estimated(self):
        self.assertEqual(len(self.filled), 207)
        self.assertEqual(self.comparison["after: ratio estimate"]["values"], 20640)
        self.assertEqual(self.comparison["after: ratio estimate"]["missing"], 0)

    def test_worked_example(self):
        # 1,256 rooms in NEAR BAY: 1,256 x 0.2067 = 259.6, so 260 bedrooms.
        match = [r for r in self.filled
                 if float(r["total_rooms"]) == 1256 and r["ocean_proximity"] == "NEAR BAY"]
        self.assertTrue(match)
        self.assertEqual(int(match[0]["estimate"]), 260)

    def test_median_fill_creates_more_duplicates(self):
        ratio = self.comparison["after: ratio estimate"]
        single = self.comparison["after: single median fill"]
        self.assertGreater(single["most_frequent_count"], ratio["most_frequent_count"])

    def test_housing_csv_unchanged(self):
        with open(config.DATA_PATH, encoding="utf-8") as file:
            blanks = sum(1 for row in csv.DictReader(file) if not row["total_bedrooms"].strip())
        self.assertEqual(blanks, 207)


if __name__ == "__main__":
    unittest.main()
