
"""The three required experiments. Each writes one CSV to results/."""
import random
import time
import tracemalloc

from src import config
from src.load_data import load_column
from src.sorts import ALGORITHMS, bubble_sort
from src.measure import run_algorithm, write_results, verify_sorted
from src.data_profile import duplication_stats

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
            rows.append({
                "n": n,
                "algorithm": name,
                "comparisons": stats["comparisons"],
                "writes": stats["writes"],
                "swaps": stats["swaps"],
                "passes": stats["passes"],
                "median_runtime_s": runtime,
                "loop_reps": loop_reps
            })

    # Write all 30 results to CSV.
    write_results(
        rows,
        "scaling.csv",
        columns=config.SCALING_COLUMNS
    )

def run_full_size():
    """Run merge sort and, optionally, one bubble check on the full column."""

    values, _ = load_column(config.DATA_PATH, config.SCALING_COLUMN)

    data = random.Random(config.SEED).sample(values, len(values))

    runtime, stats, _ = run_algorithm(ALGORITHMS["merge"], data)

    rows = [{
        "algorithm": "merge",
        "source": "measured",
        "comparisons": stats["comparisons"],
        "writes": stats["writes"],
        "swaps": stats["swaps"],
        "passes": stats["passes"],
        "runtime_s": runtime,
        "runs": config.REPEATS
    }]

    if config.RUN_BUBBLE_FULL:
        original = list(data)
        started = time.perf_counter()
        result, stats = bubble_sort(data)
        runtime = time.perf_counter() - started

        verify_sorted(result, original, "bubble")
        if data != original:
            raise AssertionError("bubble modified the full-size input.")

        rows.append({
            "algorithm": "bubble",
            "source": "check",
            "comparisons": stats["comparisons"],
            "writes": stats["writes"],
            "swaps": stats["swaps"],
            "passes": stats["passes"],
            "runtime_s": runtime,
            "runs": 1
        })

    write_results(rows, "full_size.csv", config.FULL_SIZE_COLUMNS)


def build_orders(base, seed=config.SEED):
    """Section 4.3: return four different input orders from base."""

    # Random order: shuffle a copy of the original sample.
    r = list(base)
    random.Random(seed).shuffle(r)

    # Sorted order: use our own merge sort.
    s, _ = ALGORITHMS["merge"](base)

    # Reverse order: reverse the ascending list.
    reverse = s[::-1]

    # Nearly sorted order: swap 1% of the elements.
    ns = list(s)
    rng = random.Random(seed)

    k = int(config.NEARLY_SORTED_SWAP_FRACTION * len(ns))

    for _ in range(k):
        i, j = rng.sample(range(len(ns)), 2)
        ns[i], ns[j] = ns[j], ns[i]

    return {
        "random": r,
        "sorted": s,
        "reverse": reverse,
        "nearly_sorted": ns
    }


def run_input_order():
    """Section 4.3: n = config.ORDER_N median_income sample, four orders."""

    # Load the median_income column.
    values, _ = load_column(config.DATA_PATH, "median_income")

    # Generate the same reproducible sample used by scaling at n = 2,000.
    base = random.Random(config.SEED).sample(values, config.ORDER_N)

    # Generate the four input arrangements.
    orders = build_orders(base)

    rows = []

    # Run all three sorting algorithms on each input order.
    for order_name, data in orders.items():

        for algorithm_name, sort_fn in ALGORITHMS.items():

            runtime, stats, _ = run_algorithm(sort_fn, data)

            rows.append({
                "order": order_name,
                "algorithm": algorithm_name,
                "comparisons": stats["comparisons"],
                "writes": stats["writes"],
                "swaps": stats["swaps"],
                "passes": stats["passes"],
                "median_runtime_s": runtime
            })

    # Write the 12 results to CSV.
    write_results(
        rows,
        "input_order.csv",
        columns=config.INPUT_ORDER_COLUMNS
    )


def run_repeated_values():
    """Section 4.4: n = config.ORDER_N sample of each column."""

    rows = []

    # Run the experiment for each configured dataset column.
    for column in config.COLUMNS:

        # Load the column's values.
        values, _ = load_column(config.DATA_PATH, column)

        # Generate a reproducible sample.
        sample = random.Random(config.SEED).sample(values, config.ORDER_N)

        # Calculate duplication statistics for the sample.
        d = duplication_stats(sample)

        # Run all three sorting algorithms on the same sample.
        for algorithm_name, sort_fn in ALGORITHMS.items():

            runtime, stats, _ = run_algorithm(sort_fn, sample)

            rows.append({
                "column": column,
                "algorithm": algorithm_name,
                "comparisons": stats["comparisons"],
                "writes": stats["writes"],
                "swaps": stats["swaps"],
                "passes": stats["passes"],
                "median_runtime_s": runtime,
                "distinct_values": d["distinct_values"],
                "most_frequent_count": d["most_frequent_count"],
                "values_repeated": d["values_repeated"],
                "elements_in_repeats": d["elements_in_repeats"],
                "equal_pairs": d["equal_pairs"],
            })

    # Write all nine results to CSV.
    write_results(
        rows,
        "repeated_values.csv",
        columns=config.REPEATED_COLUMNS
    )

def run_memory():
    """Measure peak memory usage for each sorting algorithm."""

    values, _ = load_column(config.DATA_PATH, config.SCALING_COLUMN)

    # Use the same random input as the random input-order experiment.
    base = random.Random(config.SEED).sample(values, config.ORDER_N)
    orders = build_orders(base)
    data = orders["random"]

    rows = []

    for algorithm_name, sort_fn in ALGORITHMS.items():

        # Start memory tracking immediately before the sort.
        tracemalloc.start()

        try:
            result, _ = sort_fn(data)
            current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()

        verify_sorted(result, data, algorithm_name) 

        rows.append({
            "algorithm": algorithm_name,
            "peak_kib": round(peak / 1024, 1)
        })

    write_results(
        rows,
        "memory.csv",
        columns=config.MEMORY_COLUMNS
    )
