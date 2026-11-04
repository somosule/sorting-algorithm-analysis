"""Tables and plots from the results CSVs (brief Section 5)."""
import csv

import matplotlib

matplotlib.use("Agg")  # save files only; never open a window
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import NullLocator  # noqa: E402

from src import config  # noqa: E402

ALGORITHMS = config.ALGORITHM_NAMES
LARGE_N_MIN = 250  # charts start here; smaller sizes go in small_n_table
MICROSECONDS = 1_000_000

# One look per sort, so lines stay visible when they overlap.
LINE_STYLES = {
    "bubble": {"marker": "o", "linestyle": "--", "zorder": 3},
    "selection": {"marker": "s", "linestyle": "-"},
    "merge": {"marker": "^", "linestyle": "-"},
}


def make_plots():
    """Save the charts to results/plots/ and the tables to results/tables/."""
    config.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    scaling = _read_csv("scaling.csv")
    if scaling:
        _scaling_charts(scaling)
        _scaling_tables(scaling)


def _scaling_charts(rows):
    """Runtime, comparisons and writes against n, one line per sort."""
    large = [row for row in rows if row["n"] >= LARGE_N_MIN]
    _line_chart(
        large, "median_runtime_s", "runtime_vs_n.png",
        "Median runtime vs input size (median_income)",
        "Median runtime (seconds)",
    )
    _line_chart(
        large, "median_runtime_s", "runtime_vs_n_loglog.png",
        "Median runtime vs input size, log-log scale",
        "Median runtime (seconds, log scale)", log=True,
    )
    _line_chart(
        large, "comparisons", "comparisons_vs_n.png",
        "Comparisons vs input size (median_income)",
        "Comparisons (count, log scale)", log=True,
    )
    _line_chart(
        large, "writes", "writes_vs_n.png",
        "Writes vs input size (median_income)",
        "Writes (count, log scale)", log=True,
    )


def _scaling_tables(rows):
    """Report-ready tables: sizes down the side, sorts across the top."""
    _save_table(
        _pivot(rows, "n", "median_runtime_s"),
        "scaling_runtime_table.csv", "n", "seconds",
    )
    _save_table(
        _pivot(rows, "n", "comparisons"),
        "scaling_comparisons_table.csv", "n",
    )
    small = [row for row in rows if row["n"] <= config.SMALL_N_MAX]
    small_us = [
        {**row, "median_runtime_s": row["median_runtime_s"] * MICROSECONDS}
        for row in small
    ]
    _save_table(
        _pivot(small_us, "n", "median_runtime_s", decimals=2),
        "small_n_table.csv", "n", "microseconds",
    )


def _read_csv(filename):
    """Read results/<filename>; numbers become int or float.

    Returns an empty list (and prints a message) if the file is missing.
    """
    path = config.RESULTS_DIR / filename
    if not path.exists():
        print(f"{filename} not found: its charts and tables are skipped.")
        return []
    with open(path, newline="", encoding="utf-8") as file:
        return [
            {key: _to_number(value) for key, value in row.items()}
            for row in csv.DictReader(file)
        ]


def _to_number(text):
    """Turn '42' into 42 and '0.5' into 0.5; leave other text unchanged."""
    for convert in (int, float):
        try:
            return convert(text)
        except ValueError:
            pass
    return text


def _line_chart(rows, measure, filename, title, ylabel, log=False):
    """One line per sort: measure against n, saved to results/plots/."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for algorithm in ALGORITHMS:
        points = [row for row in rows if row["algorithm"] == algorithm]
        ax.plot(
            [row["n"] for row in points],
            [row[measure] for row in points],
            label=algorithm, **LINE_STYLES[algorithm],
        )
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    sizes = list(dict.fromkeys(row["n"] for row in rows))  # file order
    ax.set_xticks(sizes)
    ax.set_xticklabels([f"{n:,}" for n in sizes])
    ax.xaxis.set_minor_locator(NullLocator())  # plain sizes only
    ax.set_title(title)
    ax.set_xlabel("Input size n (values)")
    ax.set_ylabel(ylabel)
    ax.legend(title="Sort")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(config.PLOTS_DIR / filename, dpi=150)
    plt.close(fig)
    print(f"Saved plots/{filename}")


def _pivot(rows, row_key, measure, decimals=None):
    """Turn long rows into one row per row_key with a column per sort."""
    table = {}
    for row in rows:
        value = row[measure]
        if decimals is not None:
            value = round(value, decimals)
        table.setdefault(row[row_key], {})[row["algorithm"]] = value
    return table


def _save_table(table, filename, row_label, unit=None):
    """Save a pivoted table to results/tables/<filename>."""
    headers = [f"{name} ({unit})" if unit else name for name in ALGORITHMS]
    path = config.TABLES_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([row_label, *headers])
        for key, values in table.items():
            writer.writerow([key, *(values.get(a, "") for a in ALGORITHMS)])
    print(f"Saved tables/{filename}")
