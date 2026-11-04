
"""The three required experiments. Each writes one CSV to results/."""
import random

from src import config
from src.load_data import load_column
from src.sorts import ALGORITHMS
from src.measure import run_algorithm, write_results


def _make_row(experiment, column, order, n, name, stats, runtime, loop_reps):
    """Build a result dictionary containing only the required columns."""

    if experiment == "scaling":
        return {
            "n": n,
            "algorithm": name,
            "comparisons": stats["comparisons"],
            "writes": stats["writes"],
            "swaps": stats["swaps"],
            "passes": stats["passes"],
            "median_runtime_s": runtime,
            "loop_reps": loop_reps
        }


def run_scaling():
    """Section 4.2: median_income samples of each size in config.SCALING_SIZES."""

    # Load the data once, outside the timing loop.
    values, _ = load_column(config.DATA_PATH, config.SCALING_COLUMN)

    rows = []

    # Run each configured input size.
    for n in config.SCALING_SIZES:

        # Generate one reproducible sample for this size.
        sample = random.Random(config.SEED).sample(values, n)

        # Run all algorithms on the same sample.
        for name, sort_fn in ALGORITHMS.items():

            runtime, stats, loop_reps = run_algorithm(sort_fn, sample)

            # Build and save this algorithm's result.
            rows.append(
                _make_row(
                    "scaling",
                    None,
                    None,
                    n,
                    name,
                    stats,
                    runtime,
                    loop_reps
                )
            )

    # Write all 30 results to CSV.
    write_results(
        rows,
        "scaling.csv",
        columns=config.SCALING_COLUMNS
    )


def build_orders(base):
    """Section 4.3: return four different input orders from base."""
    raise NotImplementedError


def run_input_order():
    """Section 4.3: n = config.ORDER_N median_income sample, four orders."""
    raise NotImplementedError


def run_repeated_values():
    """Section 4.4: n = config.ORDER_N sample of each column."""
    raise NotImplementedError
