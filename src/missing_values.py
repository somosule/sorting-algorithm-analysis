"""What-if extension (D05, D23): estimate the 207 blank total_bedrooms values.

Kept separate from the main results: housing.csv is never changed, the
experiments never use total_bedrooms, and the estimates are written only to
their own results files.

Method: ratio imputation (an estimate from a related column, not
interpolation). Each blank = that row's households x the median
bedrooms-per-household ratio of its ocean_proximity group. households is used
because it tracks total_bedrooms most closely (correlation 0.98); the accuracy
check below confirms it beats a ratio to total_rooms and a single median fill.
Forward or back fill is not used because rows are independent areas.

Medians are found with our own merge_sort, never sorted().
"""
import csv

from src import config
from src.data_profile import duplication_stats
from src.load_data import load_rows
from src.sorts import merge_sort

TARGET = "total_bedrooms"
AUXILIARY = "households"          # related column used for the estimate
GROUP = "ocean_proximity"

FILLED_FILE = "total_bedrooms_filled.csv"
FILLED_FIELDS = ("row_number", "ocean_proximity", "households", "ratio_used", "estimate")
COMPARE_FILE = "total_bedrooms_before_after.csv"
COMPARE_FIELDS = ("version", "values", "missing", "distinct", "min", "max", "median",
                  "most_frequent_value", "most_frequent_count", "values_repeated")
CHECK_FILE = "total_bedrooms_method_check.csv"
CHECK_FIELDS = ("method", "median_abs_pct_error", "share_within_10pct")


def estimate_missing_bedrooms(path):
    """Estimate each blank, compare versions and check accuracy on known values.

    Saves results/total_bedrooms_filled.csv, results/total_bedrooms_before_after.csv
    and results/total_bedrooms_method_check.csv; returns the before/after rows.
    """
    rows = load_rows(path)
    ratios = _group_ratios(rows, AUXILIARY)

    known, filled = [], []
    for number, row in enumerate(rows, start=1):  # row_number 1 = first data row
        bedrooms = _to_float(row[TARGET])
        if bedrooms is not None:
            known.append(bedrooms)
            continue
        ratio = ratios.get(row[GROUP], ratios["ALL"])
        households = float(row[AUXILIARY])
        filled.append({
            "row_number": number,
            "ocean_proximity": row[GROUP],
            "households": households,
            "ratio_used": round(ratio, 4),
            "estimate": _round(households * ratio),
        })

    median_bedrooms = _median(known)
    comparison = [
        _summary("before (blanks skipped)", known, len(filled)),
        _summary("after: ratio estimate (households)", known + [f["estimate"] for f in filled], 0),
        _summary("after: single median fill", known + [median_bedrooms] * len(filled), 0),
    ]
    check = method_check(rows)

    _write(FILLED_FILE, FILLED_FIELDS, filled)
    _write(COMPARE_FILE, COMPARE_FIELDS, comparison)
    _write(CHECK_FILE, CHECK_FIELDS, check)
    _print(comparison, check, len(filled))
    return comparison


def method_check(rows):
    """Hide each known total_bedrooms value, estimate it each way, and measure the error.

    Returns one row per method with the median absolute % error and the share of
    estimates within 10% of the true value.
    """
    known_rows = [row for row in rows if _to_float(row[TARGET]) is not None]
    truth = [float(row[TARGET]) for row in known_rows]
    median_bedrooms = _median(truth)

    estimates = {"single median fill": [median_bedrooms] * len(known_rows)}
    for auxiliary in ("total_rooms", "households"):
        ratios = _group_ratios(rows, auxiliary)
        estimates[f"ratio to {auxiliary}"] = [
            float(row[auxiliary]) * ratios.get(row[GROUP], ratios["ALL"]) for row in known_rows
        ]

    results = []
    for method, guesses in estimates.items():
        errors = [abs(guess - true) / true for guess, true in zip(guesses, truth)]
        results.append({
            "method": method,
            "median_abs_pct_error": round(100 * _median(errors), 1),
            "share_within_10pct": round(100 * sum(e <= 0.10 for e in errors) / len(errors), 1),
        })
    return results


def bedrooms_column(path, method="ratio"):
    """Return (values, missing) for total_bedrooms with the blanks handled by method.

    method "skip": blanks left out, as load_column does (missing = 207).
    method "ratio": each blank = households x its group's median ratio (missing = 0).
    method "median": each blank = the median of the known values (missing = 0).
    Values stay in file order, so the same seed gives the same sample as load_column.
    Used by the interactive mode (D27); housing.csv is never changed.
    """
    if method not in ("skip", "ratio", "median"):
        raise ValueError("method must be 'skip', 'ratio' or 'median'")
    rows = load_rows(path)
    known = [b for b in (_to_float(r[TARGET]) for r in rows) if b is not None]
    ratios = _group_ratios(rows, AUXILIARY) if method == "ratio" else None
    median_bedrooms = _median(known) if method == "median" else None

    values, missing = [], 0
    for row in rows:
        bedrooms = _to_float(row[TARGET])
        if bedrooms is not None:
            values.append(bedrooms)
        elif method == "skip":
            missing += 1
        elif method == "ratio":
            ratio = ratios.get(row[GROUP], ratios["ALL"])
            values.append(float(_round(float(row[AUXILIARY]) * ratio)))
        else:
            values.append(median_bedrooms)
    return values, missing


def _group_ratios(rows, auxiliary):
    """Median total_bedrooms / auxiliary per ocean_proximity group, plus 'ALL'."""
    by_group = {"ALL": []}
    for row in rows:
        bedrooms = _to_float(row[TARGET])
        base = _to_float(row[auxiliary])
        if bedrooms is None or not base:
            continue
        ratio = bedrooms / base
        by_group.setdefault(row[GROUP], []).append(ratio)
        by_group["ALL"].append(ratio)
    return {group: _median(values) for group, values in by_group.items()}


def _median(values):
    """Median using our own merge sort (sorted() is only allowed for verification)."""
    ordered, _ = merge_sort(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _round(value):
    """Round half up to a whole number of bedrooms."""
    return int(value + 0.5)


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


def _print(comparison, check, blanks):
    """Short summary for the terminal."""
    print(f"total_bedrooms what-if: {blanks} blanks estimated -> results/{FILLED_FILE}, "
          f"results/{COMPARE_FILE}, results/{CHECK_FILE}")
    for item in comparison:
        print(f"  {item['version']:<36} distinct {item['distinct']:>5}  "
              f"most frequent {item['most_frequent_value']} x {item['most_frequent_count']}")
    print("  Accuracy on known values (hidden and re-estimated):")
    for item in check:
        print(f"    {item['method']:<22} typical error {item['median_abs_pct_error']:>5}%  "
              f"within 10%: {item['share_within_10pct']:>5}%")
