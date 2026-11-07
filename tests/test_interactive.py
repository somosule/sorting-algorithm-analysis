"""Tests for menu-driven experiments, which must not write report results."""
import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src import config
from src.experiments import run_scaling
from src.growth_estimate import bubble_estimate
from src.interactive import (
    ALL_SCALING_SIZES,
    _ask_experiment,
    _ask_missing_version,
    _ask_sizes,
    _calculate_rows,
    _run_one_exploration,
    run_interactive,
)
from src.load_data import load_column
from src.sorts import ALGORITHMS


COUNT_FIELDS = ("comparisons", "writes", "swaps", "passes")


def _read_scaling_counts(path):
    with open(path, newline="", encoding="utf-8") as file:
        return {
            (int(row["n"]), row["algorithm"]): tuple(
                int(row[field]) for field in COUNT_FIELDS
            )
            for row in csv.DictReader(file)
        }


class TestInteractiveCalculations(unittest.TestCase):
    def test_default_scaling_counts_match_official_results(self):
        results_path = config.RESULTS_DIR / "scaling.csv"
        if results_path.is_file():
            expected_counts = _read_scaling_counts(results_path)
        else:
            with tempfile.TemporaryDirectory() as directory:
                temporary_results = Path(directory)
                with patch.object(config, "RESULTS_DIR", temporary_results):
                    run_scaling()
                expected_counts = _read_scaling_counts(
                    temporary_results / "scaling.csv"
                )

        values, missing = load_column(config.DATA_PATH, "median_income")
        self.assertEqual(missing, 0)
        with patch.object(config, "REPEATS", 1):
            rows = _calculate_rows(
                "scaling",
                ALL_SCALING_SIZES,
                config.SEED,
                {"median_income": values},
            )

        actual_counts = {
            (row["n"], row["algorithm"]): tuple(row[field] for field in COUNT_FIELDS)
            for row in rows
        }
        self.assertEqual(actual_counts, expected_counts)
        self.assertEqual(len(actual_counts), len(config.SCALING_SIZES) * len(ALGORITHMS))

    def test_calculations_do_not_create_results_files(self):
        values, _ = load_column(config.DATA_PATH, "median_income")
        with tempfile.TemporaryDirectory() as directory:
            results_dir = Path(directory) / "results"
            with patch.object(config, "RESULTS_DIR", results_dir):
                rows = _calculate_rows(
                    "scaling",
                    (5,),
                    config.SEED,
                    {"median_income": values},
                )
            self.assertEqual(len(rows), len(ALGORITHMS))
            self.assertFalse(results_dir.exists())

    def test_menu_retries_invalid_answers_and_accepts_defaults(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=("invalid", "")):
            with redirect_stdout(output):
                experiment = _ask_experiment()
        self.assertEqual(experiment, "scaling")
        self.assertIn("Please choose 1, 2, or 3.", output.getvalue())

        with patch("builtins.input", return_value=""):
            self.assertEqual(_ask_sizes("scaling"), (250, 500, 1000, 2000, 4000))

    def test_missing_values_prompt_reports_selected_data_version(self):
        labels = {
            "1": "raw data (blanks skipped)",
            "2": "ratio-imputed data",
            "3": "single median-filled data",
        }
        with patch("src.missing_values.bedrooms_column", return_value=([1.0], 0)):
            for choice, label in labels.items():
                output = io.StringIO()
                with patch("builtins.input", return_value=choice):
                    with redirect_stdout(output):
                        values = _ask_missing_version(
                            "total_bedrooms", [1.0], 207
                        )
                self.assertEqual(values, [1.0])
                self.assertIn(
                    f"Selected total_bedrooms data version: {label}.",
                    output.getvalue(),
                )

    def test_repeated_values_label_reports_brief_columns_and_official_settings(self):
        output = io.StringIO()
        columns = config.COLUMNS
        rows = [{"column": column} for column in columns]
        with (
            patch("src.interactive._ask_experiment", return_value="repeated values"),
            patch("src.interactive._ask_sizes", return_value=(config.ORDER_N,)),
            patch("src.interactive._ask_seed", return_value=config.SEED),
            patch("src.interactive._ask_repeated_columns", return_value=columns),
            patch("src.interactive._load_selected_columns", return_value={}),
            patch("src.interactive._calculate_rows", return_value=rows),
            patch("src.interactive._print_result_table"),
            redirect_stdout(output),
        ):
            _run_one_exploration()

        self.assertIn(
            "the report uses the brief's three columns at "
            f"n = {config.ORDER_N:,}, seed {config.SEED}: "
            f"{', '.join(columns)}",
            output.getvalue(),
        )

    def test_main_dispatches_interactive_without_running_official_pipeline(self):
        from main import main

        with patch("src.interactive.run_interactive") as run_interactive:
            main(["--interactive"])
        run_interactive.assert_called_once_with()

    def test_interactive_flow_only_prints_and_does_not_create_results(self):
        answers = ("1", "a", "", "", "n")
        with tempfile.TemporaryDirectory() as directory:
            results_dir = Path(directory) / "results"
            with patch.object(config, "RESULTS_DIR", results_dir):
                with patch("builtins.input", side_effect=answers):
                    with redirect_stdout(io.StringIO()):
                        run_interactive()
            self.assertFalse(results_dir.exists())

    def test_quadratic_estimator_accepts_selection_rows(self):
        rows = [
            {
                "n": n,
                "algorithm": algorithm,
                "comparisons": n * (n - 1) // 2,
                "median_runtime_s": n * n / 1000,
            }
            for algorithm in ("bubble", "selection")
            for n in (250, 500, 1000)
        ]
        estimates = bubble_estimate(rows, 2000, algorithm="selection")
        self.assertEqual(len(estimates), 4)
        self.assertEqual(estimates[-1]["n"], "average")
        self.assertAlmostEqual(estimates[-1]["estimate_s"], 4000)


if __name__ == "__main__":
    unittest.main()
