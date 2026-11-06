
"""Time a sort and verify its output. The only module allowed to call sorted()."""
import csv
import statistics
import time

from src import config


def _time_once(sort_fn, values, loop_reps):
    """Run and time the sorting algorithm once."""
    start = time.perf_counter()

    for _ in range(loop_reps):
        out, stats = sort_fn(values)

    elapsed = (time.perf_counter() - start) / loop_reps

    return elapsed, out, stats


def _check_output(out, original, values, stats, first_stats, name, n):
    """Verify sorting correctness, input preservation, and consistent stats."""

    if out != sorted(original):
        raise AssertionError(
            f"{name} failed output check for n={n}"
        )

    if values != original:
        raise AssertionError(
            f"{name} failed input unchanged check for n={n}"
        )

    if stats != first_stats:
        raise AssertionError(
            f"{name} failed stats consistency check for n={n}"
        )


def run_algorithm(sort_fn, values):
    """Return (median_runtime_s, stats, loop_reps)."""

    # Preserve the original input before timing.
    original = list(values)
    n = len(original)

    # Use repeated calls for small inputs to get a measurable runtime.
    loop_reps = (
        config.SMALL_LOOP if n <= config.SMALL_N_MAX else 1
    )

    times = []
    first_stats = None

    for repeat in range(config.REPEATS):

        # Time the sorting algorithm.
        elapsed, out, stats = _time_once(
            sort_fn, values, loop_reps
        )

        times.append(elapsed)

        # Save the stats from the first repeat.
        if repeat == 0:
            first_stats = stats

        # Validate outside the timer.
        _check_output(
            out,
            original,
            values,
            stats,
            first_stats,
            sort_fn.__name__,
            n
        )

    return statistics.median(times), first_stats, loop_reps


def write_results(rows, filename, columns):
    """Write rows (list of dicts) to results/<filename>."""

    # Make sure the results directory exists.
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Build the output path.
    filepath = config.RESULTS_DIR / filename

    # Write the CSV file.
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

def verify_sorted(out, original, name):
    """Raise an error if the sorting output is incorrect."""

    expected = sorted(original)

    if out != expected:
      raise AssertionError(f"{name} produced an incorrect sorting result.")
