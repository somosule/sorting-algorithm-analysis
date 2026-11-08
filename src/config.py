"""Fixed settings shared by every module. Change values here only, and only with team agreement."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "housing.csv"
RESULTS_DIR = ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
TABLES_DIR = RESULTS_DIR / "tables"

# Reproducibility: every random step creates a fresh random.Random(SEED).
SEED = 42

# Columns used in the experiments.
COLUMNS = ("median_income", "housing_median_age", "median_house_value")
SCALING_COLUMN = "median_income"  # few duplicates, so they do not confound 4.2 and 4.3

# Scaling experiment (4.2): very small sizes support the "n < 20" decision-guide row.
SCALING_SIZES = (5, 10, 20, 50, 100, 250, 500, 1000, 2000, 4000)

# Input-order (4.3) and repeated-values (4.4) sample size.
ORDER_N = 2000
NEARLY_SORTED_SWAP_FRACTION = 0.01  # floor(0.01 * n) random swaps

# Timing.
REPEATS = 5         # timings per input; the median is reported
SMALL_N_MAX = 20    # at or below this size, time a loop instead of one call
SMALL_LOOP = 1000   # calls per timed loop for very small inputs

# Bubble sort estimate target (4.2 step 4).
FULL_SIZE = 20640

# Optional full-size check, enabled only after the estimate is saved.
# Default off; switch on for one run with: python3 main.py --bubble-check (or --all-extras).
RUN_BUBBLE_FULL = False

# Algorithm names used in every results file.
ALGORITHM_NAMES = ("bubble", "selection", "merge")

# Columns for each experiment's results CSV.
SCALING_COLUMNS = (
    "n",
    "algorithm",
    "comparisons",
    "writes",
    "swaps",
    "passes",
    "median_runtime_s",
    "loop_reps"
)

INPUT_ORDER_COLUMNS = (
    "order",
    "algorithm",
    "comparisons",
    "writes",
    "swaps",
    "passes",
    "median_runtime_s"
)

REPEATED_COLUMNS = (
    "column",
    "algorithm",
    "comparisons",
    "writes",
    "swaps",
    "passes",
    "median_runtime_s",
    "distinct_values",
    "most_frequent_count",
    "values_repeated",
    "elements_in_repeats",
    "equal_pairs"
)

FULL_SIZE_COLUMNS = (
    "algorithm",
    "source",
    "comparisons",
    "writes",
    "swaps",
    "passes",
    "runtime_s",
    "runs"
)

MEMORY_COLUMNS = (
    "algorithm",
    "peak_kib"
)

# Optional extension: look up original records after sorting (not part of the timed experiments).
# Default off; switch on for one run with: python3 main.py --record-lookup (or --all-extras).
RUN_RECORD_LOOKUP = False

# What-if extension (D23): estimate the missing total_bedrooms values; separate from the main results.
# Default off; switch on for one run with: python3 main.py --missing-values (or --all-extras).
RUN_MISSING_VALUES = False