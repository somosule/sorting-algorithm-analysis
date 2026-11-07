"""Tests for the full-size merge run and optional single bubble check."""
import unittest
from unittest.mock import patch

from src import config
from src.experiments import run_full_size
from src.sorts import bubble_sort


class TestFullSize(unittest.TestCase):
    def run_with_bubble_setting(self, enabled):
        written = {}

        def capture_results(rows, filename, columns):
            written["rows"] = rows
            written["filename"] = filename
            written["columns"] = columns

        with (
            patch("src.experiments.load_column", return_value=([4, 1, 3, 2], 0)),
            patch.object(config, "RUN_BUBBLE_FULL", enabled),
            patch("src.experiments.write_results", side_effect=capture_results),
            patch("src.experiments.bubble_sort", wraps=bubble_sort) as bubble,
        ):
            run_full_size()
        written["bubble_calls"] = bubble.call_count
        return written

    def test_optional_bubble_check_runs_once_and_writes_check_row(self):
        written = self.run_with_bubble_setting(True)

        self.assertEqual(written["filename"], "full_size.csv")
        self.assertEqual(written["columns"], config.FULL_SIZE_COLUMNS)
        self.assertEqual(
            [(row["algorithm"], row["source"], row["runs"]) for row in written["rows"]],
            [("merge", "measured", config.REPEATS), ("bubble", "check", 1)],
        )
        self.assertEqual(written["bubble_calls"], 1)
        self.assertGreaterEqual(written["rows"][1]["runtime_s"], 0)

    def test_bubble_check_is_disabled_by_default(self):
        self.assertFalse(config.RUN_BUBBLE_FULL)

    def test_disabled_setting_writes_only_the_merge_row(self):
        written = self.run_with_bubble_setting(False)

        self.assertEqual(len(written["rows"]), 1)
        self.assertEqual(written["bubble_calls"], 0)
        self.assertEqual(written["rows"][0]["algorithm"], "merge")
        self.assertEqual(written["rows"][0]["source"], "measured")


if __name__ == "__main__":
    unittest.main()
