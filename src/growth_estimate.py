"""Section 4.2 steps 3 and 4: growth factors when n doubles, and the bubble sort estimate.

growth_factors() and bubble_estimate() work on rows in memory, so the
interactive mode (D27) uses the same maths without writing files.
write_growth_factors() and write_bubble_estimate() read results/scaling.csv,
call them and save the results files used by make_plots.py and Q3, Q4.
"""
import csv
import math

from src import config
from src.measure import write_results

GROWTH_N_MIN = 250  # doublings start here; smaller sizes are timing noise
ESTIMATE_POINTS = 3  # the largest three sizes feed the estimate
GROWTH_COLUMNS = (
    "algorithm", "n_from", "n_to",
    "runtime_ratio", "comparisons_ratio", "theory_ratio",
)
ESTIMATE_COLUMNS = ("n", "runtime_s", "scale_factor", "estimate_s")


def growth_factors(rows):
    """Return one row per sort and doubling (n to 2n), from n = 250 up.

    runtime_ratio and comparisons_ratio are measured; theory_ratio is 4.0
    for the O(n^2) sorts and 2 * log2(2n) / log2(n) for merge sort.
    """
    results = []
    for algorithm in config.ALGORITHM_NAMES:
        by_n = {row["n"]: row for row in rows
                if row["algorithm"] == algorithm and row["n"] >= GROWTH_N_MIN}
        for n_from in by_n:
            n_to = 2 * n_from
            if n_to not in by_n:
                continue
            before, after = by_n[n_from], by_n[n_to]
            results.append({
                "algorithm": algorithm,
                "n_from": n_from,
                "n_to": n_to,
                "runtime_ratio": _ratio(after["median_runtime_s"],
                                        before["median_runtime_s"]),
                "comparisons_ratio": _ratio(after["comparisons"],
                                            before["comparisons"]),
                "theory_ratio": _theory(algorithm, n_from, n_to),
            })
    return results


def bubble_estimate(rows, target_n, algorithm="bubble"):
    """Estimate a quadratic sort's runtime for target_n values.

    From each of the three largest measured sizes:
    estimate = runtime x (target_n / n) ** 2, assuming quadratic growth.
    The last row (n = "average") holds the mean of the three estimates.
    """
    if algorithm not in ("bubble", "selection"):
        raise ValueError("algorithm must be 'bubble' or 'selection'")
    measured = [row for row in rows if row["algorithm"] == algorithm]
    largest = measured[-ESTIMATE_POINTS:]  # scaling rows list sizes in order
    if len(largest) < ESTIMATE_POINTS:
        raise ValueError(
            f"at least {ESTIMATE_POINTS} {algorithm} scaling rows are required"
        )
    results = []
    for row in largest:
        scale = (target_n / row["n"]) ** 2
        results.append({
            "n": row["n"],
            "runtime_s": row["median_runtime_s"],
            "scale_factor": scale,
            "estimate_s": row["median_runtime_s"] * scale,
        })
    average = sum(r["estimate_s"] for r in results) / len(results)
    results.append({"n": "average", "runtime_s": "", "scale_factor": "",
                    "estimate_s": average})
    return results


def write_growth_factors():
    """Write results/growth_factors.csv from results/scaling.csv."""
    rows = growth_factors(_read_scaling())
    write_results(rows, "growth_factors.csv", GROWTH_COLUMNS)
    return rows


def write_bubble_estimate():
    """Write results/bubble_estimate.csv for all config.FULL_SIZE values."""
    rows = bubble_estimate(_read_scaling(), config.FULL_SIZE)
    write_results(rows, "bubble_estimate.csv", ESTIMATE_COLUMNS)
    return rows


def _read_scaling():
    """Rows of results/scaling.csv with numbers converted."""
    path = config.RESULTS_DIR / "scaling.csv"
    with open(path, newline="", encoding="utf-8") as file:
        return [
            {
                "n": int(row["n"]),
                "algorithm": row["algorithm"],
                "comparisons": int(row["comparisons"]),
                "median_runtime_s": float(row["median_runtime_s"]),
            }
            for row in csv.DictReader(file)
        ]


def _ratio(after, before):
    """after / before, or None when before is zero."""
    return after / before if before else None


def _theory(algorithm, n_from, n_to):
    """Expected growth when n doubles: n^2 sorts 4.0, merge n log n."""
    if algorithm == "merge":
        return 2 * math.log2(n_to) / math.log2(n_from)
    return (n_to / n_from) ** 2
