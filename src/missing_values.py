"""What-if extension (D05, D23): estimate the 207 blank total_bedrooms values.

Kept separate from the main results: housing.csv is never changed, the
experiments never use total_bedrooms, and the estimates are written only to
their own results files.

Method (ratio-based imputation, not interpolation): total_bedrooms is closely
related to total_rooms, so each blank is estimated as that row's total_rooms
times the median bedrooms-per-room ratio of its ocean_proximity group.
Forward or back fill is not used because rows are independent areas, and a
single median fill would give every blank the same value.

Medians are found with our own merge_sort, never sorted().
"""
import csv

from src import config
from src.data_profile import duplication_stats
from src.load_data import load_rows
from src.sorts import merge_sort

FILLED_FILE = "total_bedrooms_filled.csv"
FILLED_FIELDS = ("row_number", "ocean_proximity", "total_rooms", "ratio_used", "estimate")
COMPARE_FILE = "total_bedrooms_before_after.csv"
COMPARE_FIELDS = ("version", "values", "missing", "distinct", "min", "max", "median",
                  "most_frequent_value", "most_frequent_count", "values_repeated")


def estimate_missing_bedrooms(path):
    """Estimate each blank total_bedrooms value and compare with a plain median fill.

    Saves results/total_bedrooms_filled.csv and results/total_bedrooms_before_after.csv
    and returns the comparison rows (before, ratio fill, median fill).
    """
    rows = load_rows(path)
    ratios = _group_ratios(rows)

    known, blanks = [], []
    for number, row in enumerate(rows, start=1):  # row_number 1 = first data row
        bedrooms = _to_float(row["total_bedrooms"])
        if bedrooms is None:
            blanks.append((number, row))
        else:
            known.append(bedrooms)

    filled = []
    for number, row in blanks:
        group = row["ocean_proximity"]
        ratio = ratios.get(group, ratios["ALL"])
        rooms = float(row["total_rooms"])
        filled.append({
            "row_number": number,
            "ocean_proximity": group,
            "total_rooms": rooms,
            "ratio_used": round(ratio, 4),
            "estimate": int(rooms * ratio + 0.5),  # round half up
        })

    median_bedrooms = _median(known)
    ratio_version = known + [item["estimate"] for item in filled]
    median_version = known + [median_bedrooms] * len(blanks)

    comparison = [
        _summary("before (blanks skipped)", known, len(blanks)),
        _summary("after: ratio estimate", ratio_version, 0),
        _summary("after: single median fill", median_version, 0),
    ]
    _write(FILLED_FILE, FILLED_FIELDS, filled)
    _write(COMPARE_FILE, COMPARE_FIELDS, comparison)
    _print(comparison, len(blanks))
    return comparison


def _group_ratios(rows):
    """Median total_bedrooms / total_rooms per ocean_proximity group, plus 'ALL'."""
    by_group = {"ALL": []}
    for row in rows:
        bedrooms = _to_float(row["total_bedrooms"])
        rooms = _to_float(row["total_rooms"])
        if bedrooms is None or not rooms:
            continue
        ratio = bedrooms / rooms
        by_group.setdefault(row["ocean_proximity"], []).append(ratio)
        by_group["ALL"].append(ratio)
    return {group: _median(values) for group, values in by_group.items()}


def _median(values):
    """Median using our own merge sort (sorted() is only allowed for verification)."""
    ordered, _ = merge_sort(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _to_float(text):
    """Return text as a float, or None if it is blank or not a number."""
    try:
        return float((text or "").strip())
    except ValueError:
        return None


def _summary(version, values, missing):
    """Profile figures for one version of the column."""
    dup = duplication_stats(values)
    return {
        "version": version,
        "values": len(values),
        "missing": missing,
        "distinct": dup["distinct_values"],
        "min": min(values),
        "max": max(values),
        "median": _median(values),
        "most_frequent_value": dup["most_frequent_value"],
        "most_frequent_count": dup["most_frequent_count"],
        "values_repeated": dup["values_repeated"],
    }


def _write(filename, fields, rows):
    """Save rows to results/<filename>."""
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.RESULTS_DIR / filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _print(comparison, blanks):
    """Short summary for the terminal."""
    print(f"total_bedrooms what-if: {blanks} blanks estimated "
          f"-> results/{FILLED_FILE}, results/{COMPARE_FILE}")
    for item in comparison:
        print(f"  {item['version']:<26} distinct {item['distinct']:>5}  "
              f"most frequent {item['most_frequent_value']} x {item['most_frequent_count']}")
