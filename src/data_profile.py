"""Dataset profile (brief Section 3) and duplication statistics (Section 4.4).

profile_dataset() describes the full file exactly as loaded, before any
sampling or sorting. duplication_stats() is reused by the repeated-values
experiment on each 2,000-value sample.
"""
import csv

from src import config
from src.load_data import load_column, load_rows

# Experiment columns, plus total_bedrooms as the "before" picture for the
# optional missing-value cleaning.
PROFILE_COLUMNS = config.COLUMNS + ("total_bedrooms",)
CAPPED_COLUMN = "median_house_value"
SUMMARY_FILE = "dataset_summary.csv"
SUMMARY_FIELDS = (
    "column", "rows", "missing", "distinct", "min", "max", "cap_count",
)


def profile_dataset(path):
    """Print and save results/dataset_summary.csv.

    Total rows and columns; for each selected column: missing values, distinct values,
    min and max; the median_house_value cap and how many rows equal it.
    """
    rows = load_rows(path)
    total_rows = len(rows)
    total_columns = len(rows[0]) if rows else 0
    print(f"Dataset: {total_rows} rows, {total_columns} columns")

    summary = [
        _column_summary(path, column, total_rows)
        for column in PROFILE_COLUMNS
    ]
    _print_summary(summary)
    _write_summary(summary)
    return summary


def duplication_stats(values):
    """Return a dict with distinct_values, most_frequent_value, most_frequent_count,
    values_repeated (distinct values appearing more than once) and
    elements_in_repeats (entries belonging to those values)."""
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1

    most_frequent_value, most_frequent_count = None, 0
    values_repeated, elements_in_repeats = 0, 0
    for value, count in counts.items():
        if count > most_frequent_count:  # on a tie, the first value seen wins
            most_frequent_value, most_frequent_count = value, count
        if count > 1:
            values_repeated += 1
            elements_in_repeats += count

    return {
        "distinct_values": len(counts),
        "most_frequent_value": most_frequent_value,
        "most_frequent_count": most_frequent_count,
        "values_repeated": values_repeated,
        "elements_in_repeats": elements_in_repeats,
    }


def _column_summary(path, column, total_rows):
    """Return the summary figures for one column.

    min() and max() are allowed: they find one value and do not sort.
    cap_count is filled only for the capped column, blank otherwise.
    """
    values, missing = load_column(path, column)
    highest = max(values)
    cap_count = ""
    if column == CAPPED_COLUMN:
        cap_count = sum(1 for value in values if value == highest)

    return {
        "column": column,
        "rows": total_rows,
        "missing": missing,
        "distinct": len(set(values)),
        "min": min(values),
        "max": highest,
        "cap_count": cap_count,
    }


def _print_summary(summary):
    """Print the summary as an aligned table."""
    header = ("column", "missing", "distinct", "min", "max", "cap_count")
    row_format = "{:<20}{:>9}{:>10}{:>12}{:>12}{:>11}"
    print(row_format.format(*header))
    for item in summary:
        print(row_format.format(*(item[name] for name in header)))


def _write_summary(summary):
    """Save the summary to results/dataset_summary.csv."""
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = config.RESULTS_DIR / SUMMARY_FILE
    with open(out_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary)
    print(f"Saved {out_path}")
