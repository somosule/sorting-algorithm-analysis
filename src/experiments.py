"""The three required experiments. Each writes one CSV to results/."""
from src import config


def run_scaling():
    """Section 4.2: median_income samples of each size in config.SCALING_SIZES.

    For each n: sample = random.Random(SEED).sample(values, n); run all three
    algorithms on the same sample; write results/scaling.csv.
    """
    raise NotImplementedError


def build_orders(base):
    """Section 4.3: return {"random", "sorted", "reverse", "nearly_sorted"} lists from base.

    random: copy shuffled with random.Random(SEED)
    sorted: our own merge_sort output, not sorted()
    reverse: sorted list reversed
    nearly_sorted: sorted copy with floor(0.01 * n) swaps of two distinct random
    positions, chosen with one random.Random(SEED)
    """
    raise NotImplementedError


def run_input_order():
    """Section 4.3: n = config.ORDER_N median_income sample, four orders; write results/input_order.csv."""
    raise NotImplementedError


def run_repeated_values():
    """Section 4.4: n = config.ORDER_N sample of each column, same seed.

    Add duplication_stats() values to each row; write results/repeated_values.csv.
    """
    raise NotImplementedError
