"""Correctness tests for the three sorts and duplication_stats (unittest).

To cover, for each algorithm:
- output equals sorted() for seeded random lists of size 0, 1, 2, 10, 100
- input list unchanged after the call
- all-equal values, many duplicates, negatives and decimals
- identical stats on two calls with the same input
- known counts, e.g. sorted n = 100: bubble 99 comparisons, 0 writes;
  selection 4,950 comparisons, 0 swaps; reverse n = 100: bubble 4,950 swaps,
  selection 50 swaps; merge on sorted n = 8: 12 comparisons, 24 writes
- duplication_stats([1, 1, 2, 3, 3, 3]): distinct 3, most frequent count 3,
  values_repeated 2, elements_in_repeats 5
"""
import unittest
