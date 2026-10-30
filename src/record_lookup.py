"""Optional extension: sort row numbers by one column, then look up the original records.

Not part of the timed experiments. Uses the same merge logic as merge_sort (<= keeps
equal values in original order) without counters.
"""
import csv


def _load_rows(path):
    # Keep every original row, in file order.
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _merge_sort_indices(indices, values):
    # Sort row numbers by their value; <= keeps equal values in original order.
    if len(indices) <= 1:
        return indices
    mid = len(indices) // 2
    left = _merge_sort_indices(indices[:mid], values)
    right = _merge_sort_indices(indices[mid:], values)
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if values[left[i]] <= values[right[j]]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def top_records(path, column, k=5, show=("population", "households", "ocean_proximity")):
    """Print the k rows with the highest value in column, with other fields."""
    rows = _load_rows(path)
    values = [float(r[column]) for r in rows]
    order = _merge_sort_indices(list(range(len(rows))), values)
    print("csv_line", column, *show)
    for idx in reversed(order[-k:]):
        print(idx + 2, values[idx], *(rows[idx][c] for c in show))
