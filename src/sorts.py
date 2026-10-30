"""Bubble, selection and merge sort with operation counters.

Each function copies its input, never changes it, and returns
(sorted_list, stats) where stats = {"comparisons": int, "writes": int, "swaps": int}.

Counting rules (brief Section 4.1):
- Comparison: two data values compared. Loop and index checks are not counted.
- Write: a value stored into a list position. A swap is 2 writes and 1 swap.
- Merge sort: each value placed into the merged output is 1 write, leftovers included.
  Slicing copies and the initial copy of the input are not counted.
No list.sort() or sorted() here.
"""


def _new_stats():
    return {"comparisons": 0, "writes": 0, "swaps": 0}


def bubble_sort(values):
    """Compare a[j] > a[j + 1]; each pass is one shorter; stop after a pass with no swaps."""
    raise NotImplementedError


def selection_sort(values):
    """Find the minimum with a[j] < a[min_index]; swap only if min_index != i."""
    raise NotImplementedError


def merge_sort(values):
    """Top-down recursive; when values are equal take the left one first (<=)."""
    raise NotImplementedError


# Name used in results files -> function.
ALGORITHMS = {"bubble": bubble_sort, "selection": selection_sort, "merge": merge_sort}
