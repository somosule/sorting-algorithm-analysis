"""Time a sort and verify its output. The only module allowed to call sorted()."""
import csv
import statistics
import time

from src import config


def run_algorithm(sort_fn, values):
    """Return (median_runtime_s, stats, loop_reps).

    - Keep an unchanged copy of values before timing.
    - Time only the sort call with time.perf_counter(), config.REPEATS times; report the median.
    - If len(values) <= config.SMALL_N_MAX, time a loop of config.SMALL_LOOP calls and divide.
    - Outside the timer, after every run, check: output == sorted(original),
      values == original, and stats identical to the first run. Raise an error naming
      the algorithm and n if any check fails.
    """
    raise NotImplementedError


def write_results(rows, filename, columns=config.RESULT_COLUMNS):
    """Write rows (list of dicts) to results/<filename> with csv.DictWriter."""
    raise NotImplementedError
