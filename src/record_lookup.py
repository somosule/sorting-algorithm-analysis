"""Extension (D08, D23): sort row numbers by one column, then look up the original records.

Brief Section 3, step 4: the experiments sort values only, but a real user often
wants the whole record (e.g. which areas have the highest income). This sorts the
row numbers using the column as the key, so every original row can be looked up.
It uses the same merge logic as merge_sort (<= keeps equal values in their
original order, so the sort is stable) without counters, and runs after the timed
experiments. housing.csv is never changed; the output goes only to
results/top_records.csv.
"""
import csv

from src import config
from src.load_data import load_rows

TOP_FILE = "top_records.csv"
SHOW = ("population", "households", "ocean_proximity")


def top_records(path, column, k=5, show=SHOW):
    """Save and return the k rows with the highest value in column, highest first.

    Rows with a blank or non-numeric value in column are left out. Each result
    gives csv_line (the line number in housing.csv, header = line 1), the
    value, and the fields in show. Ties keep the original file order.
    """
    rows = load_rows(path)
    numbered = [(number, _to_float(row[column])) for number, row in enumerate(rows)]
    usable = [(number, value) for number, value in numbered if value is not None]
    order = sort_row_numbers(usable)                 # ascending, stable
    top = _highest(order, k)

    results = []
    for number, value in top:
        record = {"csv_line": number + 2, column: value}
        record.update({field: rows[number][field] for field in show})
        results.append(record)

    _write(results, ("csv_line", column, *show))
    print(f"Record lookup: top {len(results)} rows by {column} -> results/{TOP_FILE}")
    return results


def sort_row_numbers(pairs):
    """Stable merge sort of (row_number, value) pairs by value, ascending."""
    if len(pairs) <= 1:
        return list(pairs)
    mid = len(pairs) // 2
    left = sort_row_numbers(pairs[:mid])
    right = sort_row_numbers(pairs[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i][1] <= right[j][1]:          # <= keeps equal values in file order
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def _highest(order, k):
    """The k largest values, highest first; equal values stay in file order."""
    top = []
    index = len(order) - 1
    while index >= 0 and len(top) < k:
        value = order[index][1]
        start = index
        while start > 0 and order[start - 1][1] == value:   # the whole tie group
            start -= 1
        top.extend(order[start:index + 1])                  # file order within the tie
        index = start - 1
    return top[:k]


def _to_float(text):
    """Return text as a float, or None if it is blank or not a number."""
    try:
        return float((text or "").strip())
    except ValueError:
        return None


def _write(results, fields):
    """Save the results to results/top_records.csv."""
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.RESULTS_DIR / TOP_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
