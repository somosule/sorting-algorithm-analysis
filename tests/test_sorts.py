"""Correctness tests for the three sorts and duplication_stats (unittest).
Run from the repo root with: python -m unittest discover -v
"""
import random
import unittest

from src import config
from src.data_profile import duplication_stats
from src.sorts import ALGORITHMS, bubble_sort, merge_sort, selection_sort


STAT_KEYS = {"comparisons", "writes", "swaps", "passes"}


def seeded_list(n):
    """Return n random floats in [-100, 100], the same on every run."""
    rng = random.Random(config.SEED)
    return [rng.uniform(-100, 100) for _ in range(n)]


class TestSortedOutput(unittest.TestCase):
    """Every sort returns the values in ascending order (brief Section 7)."""

    def test_seeded_random_lists(self):
        for name, sort_fn in ALGORITHMS.items():
            for n in (0, 1, 2, 10, 100):
                with self.subTest(name=name, n=n):
                    values = seeded_list(n)
                    result, _ = sort_fn(values)
                    self.assertEqual(result, sorted(values))

    def test_special_inputs(self):
        cases = {
            "all equal": [7.0] * 20,
            "many duplicates": [3, 1, 2, 3, 1, 2, 3, 1, 2, 2],
            "negatives and decimals": [-2.5, 0.0, 3.75, -10.1, 2.5, -0.001],
            "already sorted": list(range(20)),
            "reverse sorted": list(range(20, 0, -1)),
        }
        for name, sort_fn in ALGORITHMS.items():
            for label, values in cases.items():
                with self.subTest(name=name, case=label):
                    result, _ = sort_fn(values)
                    self.assertEqual(result, sorted(values))


class TestInputUnchanged(unittest.TestCase):
    """The original list must not be modified (brief Section 4)."""

    def test_input_list_is_not_modified(self):
        for name, sort_fn in ALGORITHMS.items():
            with self.subTest(name=name):
                values = seeded_list(50)
                original = list(values)
                sort_fn(values)
                self.assertEqual(values, original)


class TestReproducibleStats(unittest.TestCase):
    """The same input gives the same counts every time (brief Section 7)."""

    def test_two_calls_give_identical_stats(self):
        for name, sort_fn in ALGORITHMS.items():
            with self.subTest(name=name):
                values = seeded_list(100)
                _, first = sort_fn(values)
                _, second = sort_fn(values)
                self.assertEqual(first, second)

    def test_stats_have_the_agreed_counters(self):
        for name, sort_fn in ALGORITHMS.items():
            with self.subTest(name=name):
                _, stats = sort_fn([3, 1, 2])
                self.assertEqual(set(stats), STAT_KEYS)


class TestKnownCounts(unittest.TestCase):
    """Counts worked out by hand from the Section 4.1 rules."""

    def test_bubble_on_sorted_100(self):
        _, stats = bubble_sort(list(range(100)))
        self.assertEqual(stats["comparisons"], 99)
        self.assertEqual(stats["writes"], 0)
        self.assertEqual(stats["swaps"], 0)
        self.assertEqual(stats["passes"], 1)  # one pass, no swaps, stop

    def test_selection_on_sorted_100(self):
        _, stats = selection_sort(list(range(100)))
        self.assertEqual(stats["comparisons"], 4950)  # 100 x 99 / 2
        self.assertEqual(stats["swaps"], 0)
        self.assertEqual(stats["passes"], 99)  # always n - 1

    def test_bubble_on_reversed_100(self):
        _, stats = bubble_sort(list(range(100, 0, -1)))
        self.assertEqual(stats["comparisons"], 4950)
        self.assertEqual(stats["swaps"], 4950)
        self.assertEqual(stats["writes"], 9900)  # 2 writes per swap
        self.assertEqual(stats["passes"], 99)

    def test_selection_on_reversed_100(self):
        _, stats = selection_sort(list(range(100, 0, -1)))
        self.assertEqual(stats["comparisons"], 4950)
        self.assertEqual(stats["swaps"], 50)
        self.assertEqual(stats["passes"], 99)

    def test_merge_on_sorted_8(self):
        _, stats = merge_sort(list(range(8)))
        self.assertEqual(stats["comparisons"], 12)
        self.assertEqual(stats["writes"], 24)  # 8 values x 3 merge levels
        self.assertEqual(stats["passes"], 0)  # merge sort has no passes

    def test_merge_on_16_values(self):
        _, stats = merge_sort(seeded_list(16))
        self.assertEqual(stats["writes"], 64)  # 16 values x 4 merge levels
        self.assertEqual(stats["swaps"], 0)
        self.assertEqual(stats["passes"], 0)


class TestDuplicationStats(unittest.TestCase):
    """duplication_stats() as agreed for Section 4.4."""

    def test_agreed_example(self):
        result = duplication_stats([1, 1, 2, 3, 3, 3])
        self.assertEqual(result["distinct_values"], 3)
        self.assertEqual(result["most_frequent_value"], 3)
        self.assertEqual(result["most_frequent_count"], 3)
        self.assertEqual(result["values_repeated"], 2)
        self.assertEqual(result["elements_in_repeats"], 5)

    def test_no_repeated_values(self):
        result = duplication_stats([1.5, 2.5, 3.5])
        self.assertEqual(result["distinct_values"], 3)
        self.assertEqual(result["most_frequent_count"], 1)
        self.assertEqual(result["values_repeated"], 0)
        self.assertEqual(result["elements_in_repeats"], 0)


if __name__ == "__main__":
    unittest.main()
