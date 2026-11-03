"""Bubble, selection and merge sort with operation counters.

Each function copies its input, never changes it, and returns
(sorted_list, stats) where stats = {"comparisons": int, "writes": int, "swaps": int, "passes": int}.

Counting rules (brief Section 4.1):
- Comparison: two data values compared. Loop and index checks are not counted.
- Write: a value stored into a list position. A swap is 2 writes and 1 swap.
- Passes: bubble adds 1 at the start of each pass, including the last pass with no swaps; 
  selection counts each outer-loop step (n - 1); merge is always 0.
- Merge sort: each value placed into the merged output is 1 write, leftovers included.
  Slicing copies and the initial copy of the input are not counted.
No list.sort() or sorted() here.
"""


def _new_stats():
    return {"comparisons": 0, "writes": 0, "swaps": 0, "passes": 0}


def bubble_sort(values):
    """Compare a[j] > a[j + 1]; each pass is one shorter; stop after a pass with no swaps."""
    a = list(values)
    stats = _new_stats()

    n = len(a)

    for i in range(n - 1):
        stats["passes"] += 1  # Count each outer pass.
        swapped = False

        for j in range(n - 1 - i):
            stats["comparisons"] += 1  # Count comparison of adjacent values.

            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                stats["writes"] += 2  # Count the two list writes.
                stats["swaps"] += 1  # Count the swap.
                swapped = True

        if not swapped:
            break

    return a, stats


def selection_sort(values):
    """Find the minimum with a[j] < a[min_index]; swap only if min_index != i."""
    a = list(values)
    stats = _new_stats()

    n = len(a)

    for i in range(n - 1):
        stats["passes"] += 1  # Count each outer-loop iteration.
        min_index = i

        for j in range(i + 1, n):
            stats["comparisons"] += 1  # Count comparison of values.

            if a[j] < a[min_index]:
                min_index = j

        if min_index != i:
            a[i], a[min_index] = a[min_index], a[i]
            stats["writes"] += 2  # Count the two list writes.
            stats["swaps"] += 1  # Count the swap.

    return a, stats


def _merge(left, right, stats):
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        stats["comparisons"] += 1  # Count comparison of front values.

        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

        stats["writes"] += 1  # Count the value placed in merged.

    # Append remaining values from the left half.
    while i < len(left):
        merged.append(left[i])
        i += 1
        stats["writes"] += 1  # Count the leftover value placed in merged.

    # Append remaining values from the right half.
    while j < len(right):
        merged.append(right[j])
        j += 1
        stats["writes"] += 1  # Count the leftover value placed in merged.

    return merged


def _merge_sort(lst, stats):
    if len(lst) <= 1:
        return lst

    mid = len(lst) // 2

    left = _merge_sort(lst[:mid], stats)
    right = _merge_sort(lst[mid:], stats)

    return _merge(left, right, stats)


def merge_sort(values):
    """Top-down recursive; when values are equal take the left one first (<=)."""
    a = list(values)
    stats = _new_stats()

    a = _merge_sort(a, stats)

    return a, stats


# Name used in results files -> function.
ALGORITHMS = {"bubble": bubble_sort, "selection": selection_sort, "merge": merge_sort}
