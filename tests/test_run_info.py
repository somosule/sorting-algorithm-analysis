"""Tests for the reproducibility metadata written by main.py."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import config
from main import _write_run_info


class TestRunInfo(unittest.TestCase):
    def test_records_scaling_sizes_and_repeated_values_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            results_dir = Path(directory)
            with patch.object(config, "RESULTS_DIR", results_dir):
                path = _write_run_info()

            with open(path, newline="", encoding="utf-8") as file:
                settings = {
                    row["setting"]: row["value"] for row in csv.DictReader(file)
                }

        self.assertEqual(
            settings["scaling_sizes"],
            ", ".join(str(size) for size in config.SCALING_SIZES),
        )
        self.assertEqual(
            settings["repeated_values_columns"],
            ", ".join(config.COLUMNS),
        )


if __name__ == "__main__":
    unittest.main()
