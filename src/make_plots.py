"""Tables and plots from the results CSVs (brief Section 5).

make_plots() reads the experiment CSVs and saves PNG charts to
results/plots/, report-ready tables to results/tables/, every chart in
one PDF (results/plots/all_charts.pdf, D25) and every title in
results/tables/captions.md (D24). A part is skipped with a message if
its results file does not exist yet.
"""
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save files only; never open a window
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullLocator  # noqa: E402

from src import config  # noqa: E402

ALGORITHMS = config.ALGORITHM_NAMES
ORDERS = ("random", "sorted", "nearly_sorted", "reverse")
LARGE_N_MIN = 250  # linear runtime chart and growth factors start here
MS = 1_000
US = 1_000_000

# One colour and line style per sort, used on every chart (H3 item 11).
STYLES = {
    "bubble": {"color": "#1f77b4", "marker": "o", "linestyle": "--",
               "zorder": 3},
    "selection": {"color": "#ff7f0e", "marker": "s", "linestyle": "-"},
    "merge": {"color": "#2ca02c", "marker": "^", "linestyle": "-"},
}

# Report size and presentation style (H3 items 12 and 17).
FIGSIZE = (6.5, 4)
DPI = 200
plt.rcParams.update({
    "axes.titlesize": 10,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
THOUSANDS = FuncFormatter(lambda value, _: f"{value:,.0f}")
SECONDS = FuncFormatter(
    lambda value, _: f"{value:.6f}".rstrip("0").rstrip("."))


def make_plots(source_dir=None):
    """Save the charts, tables, captions and combined PDF.

    source_dir is the folder holding the results CSVs (default results/).
    Point it at the dummy/ folder while building. Returns the PDF path.
    """
    source = Path(source_dir) if source_dir else config.RESULTS_DIR
    config.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    scaling = _read_csv(source, "scaling.csv")
    full_size = _read_csv(source, "full_size.csv")
    input_order = _read_csv(source, "input_order.csv")
    repeated = _read_csv(source, "repeated_values.csv")
    growth = _read_csv(source, "growth_factors.csv")
    estimates = _read_csv(source, "bubble_estimate.csv")

    pdf_path = config.PLOTS_DIR / "all_charts.pdf"
    with PdfPages(pdf_path) as pdf:
        if scaling:
            _scaling_charts(scaling, full_size, pdf)
            _scaling_tables(scaling, full_size)
        if input_order:
            _input_order_charts(input_order, pdf)
            _input_order_table(input_order)
        if repeated:
            _repeated_values_chart(repeated, pdf)
            _repeated_values_table(repeated)
    if growth:
        _growth_factors_table(growth)
    if scaling and full_size and input_order and repeated:
        _decision_guide_evidence(scaling, full_size, input_order, repeated)
    if estimates and full_size:
        _full_size_table(estimates, full_size)
    _write_captions()
    print(f"Saved plots/{pdf_path.name}")
    return pdf_path


# ---------- titles (D24) ----------

def _captions():
    """One title per results file, built from config.py, never typed."""
    column = config.SCALING_COLUMN
    seed, runs, n = config.SEED, config.REPEATS, config.ORDER_N
    sizes = config.SCALING_SIZES
    estimate_sizes = ", ".join(f"{size:,}" for size in sizes[-3:])
    large = [size for size in sizes if size >= LARGE_N_MIN]
    return {
        "dataset_summary.csv":
            f"Dataset profile of housing.csv ({config.FULL_SIZE:,} rows, "
            f"{_column_count()} columns), before any sampling",
        "scaling.csv":
            f"Scaling experiment (4.2): {column}, one random sample per "
            f"size (seed {seed}), n = {sizes[0]:,} to {sizes[-1]:,}; "
            f"median of {runs} runs; loop of {config.SMALL_LOOP:,} calls "
            f"for n <= {config.SMALL_N_MAX}",
        "full_size.csv":
            f"Full dataset: all {config.FULL_SIZE:,} {column} values in "
            f"random order (seed {seed}); merge sort median of {runs} runs; "
            "optional bubble check is a single run",
        "growth_factors.csv":
            f"Growth factors when n doubles ({large[0]:,} to "
            f"{large[-1]:,}), {column}, seed {seed}, compared with theory",
        "bubble_estimate.csv":
            f"Bubble and selection sort estimates for {config.FULL_SIZE:,} "
            f"values, from measured runtimes at n = {estimate_sizes}",
        "full_size_table.csv":
            f"Full dataset (Q4): all {config.FULL_SIZE:,} {column} values, "
            f"seed {seed}; estimates from n = {sizes[-3]:,} to "
            f"{sizes[-1]:,}; merge median of {runs} runs; "
            "bubble check a single run",
        "input_order.csv":
            f"Input-order experiment (4.3): one {column} sample, "
            f"n = {n:,}, seed {seed}, in four versions; median of {runs} runs",
        "repeated_values.csv":
            f"Repeated-values experiment (4.4): {', '.join(config.COLUMNS)}, "
            f"n = {n:,} each, seed {seed}, not reshuffled; "
            f"median of {runs} runs",
        "memory.csv":
            f"Peak memory per sort (tracemalloc), random {column} list, "
            f"n = {n:,}, measured separately from the timings",
        "decision_guide_evidence.csv":
            "Decision-guide evidence, taken by code from the results "
            "files above",
    }


def _column_count():
    """Number of columns in housing.csv, read from its header row."""
    with open(config.DATA_PATH, newline="", encoding="utf-8") as file:
        return len(next(csv.reader(file)))


def _write_captions():
    """Save every title to results/tables/captions.md."""
    lines = ["# Titles for the results files", ""]
    for filename, caption in _captions().items():
        lines.append(f"- **{filename}**: {caption}")
    path = config.TABLES_DIR / "captions.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Saved tables/captions.md")


# ---------- scaling (Section 4.2) ----------

def _scaling_charts(rows, full_size, pdf):
    """Runtime, comparisons and writes against n, one line per sort."""
    subtitle = (f"{config.SCALING_COLUMN}, seed {config.SEED}, "
                f"median of {config.REPEATS} runs")
    large = [row for row in rows if row["n"] >= LARGE_N_MIN]

    fig, ax = _line_chart(large, "median_runtime_s", log=False)
    ax.yaxis.set_major_formatter(SECONDS)
    plt.setp(ax.get_xticklabels(), rotation=45)  # 250 and 500 sit close
    _finish(fig, ax, "Median runtime vs input size", subtitle,
            "Median runtime (seconds)")
    _save(fig, "runtime_vs_n.png", pdf)

    # All sizes on log-log axes, so the crossover is visible (Q5).
    fig, ax = _line_chart(rows, "median_runtime_s", log=True)
    ax.yaxis.set_major_formatter(SECONDS)
    for row in full_size:
        ax.scatter(config.FULL_SIZE, row["runtime_s"], marker="*", s=120,
                   color=STYLES[row["algorithm"]]["color"], zorder=4,
                   label=f"{row['algorithm']}, all {config.FULL_SIZE:,} "
                         "values")
    if full_size:
        ticks = [*ax.get_xticks(), config.FULL_SIZE]
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{int(tick):,}" for tick in ticks],
                           rotation=45)
    _finish(fig, ax, "Median runtime vs input size (log-log)", subtitle,
            "Median runtime (seconds, log scale)")
    _save(fig, "runtime_vs_n_loglog.png", pdf)

    for measure in ("comparisons", "writes"):
        fig, ax = _line_chart(large, measure, log=True)
        ax.yaxis.set_major_formatter(THOUSANDS)
        _finish(fig, ax, f"{measure.capitalize()} vs input size", subtitle,
                f"{measure.capitalize()} (count, log scale)")
        _save(fig, f"{measure}_vs_n.png", pdf)


def _scaling_tables(rows, full_size):
    """Runtimes in ms (all sizes), comparisons, and small n in µs."""
    table = _pivot(rows, "n", "median_runtime_s", MS)
    for row in full_size:
        key = f"{config.FULL_SIZE} (full dataset)"
        table.setdefault(key, {})[row["algorithm"]] = _sig3(
            row["runtime_s"] * MS)
    _save_table(table, "scaling_runtime_table.csv", "n", "_ms")
    _save_table(_pivot(rows, "n", "comparisons"),
                "scaling_comparisons_table.csv", "n")
    small = [row for row in rows if row["n"] <= config.SMALL_N_MAX]
    _save_table(_pivot(small, "n", "median_runtime_s", US),
                "small_n_table.csv", "n", "_us")


# ---------- input order (Section 4.3) ----------

def _input_order_charts(rows, pdf):
    """Grouped bars: comparisons and runtime per order and sort."""
    subtitle = (f"{config.SCALING_COLUMN}, n = {config.ORDER_N:,}, "
                f"seed {config.SEED}, median of {config.REPEATS} runs")
    labels = [order.replace("_", " ") for order in ORDERS]
    for measure, ylabel, name in (
        ("comparisons", "Comparisons (count, log scale)",
         "input_order_comparisons.png"),
        ("median_runtime_s", "Median runtime (seconds, log scale)",
         "input_order_runtime.png"),
    ):
        fig, ax = _bar_chart(rows, "order", ORDERS, labels, measure)
        ax.yaxis.set_major_formatter(
            THOUSANDS if measure == "comparisons" else SECONDS)
        title = ("Comparisons by input order" if measure == "comparisons"
                 else "Median runtime by input order")
        _finish(fig, ax, title, subtitle, ylabel, xlabel="Input order",
                bars=True)
        _save(fig, name, pdf)


def _input_order_table(rows):
    """Orders down the side; counts, passes and runtimes across."""
    table = {}
    for row in rows:
        entry = table.setdefault(row["order"].replace("_", " "), {})
        name = row["algorithm"]
        entry[f"{name}_comparisons"] = row["comparisons"]
        entry[f"{name}_writes"] = row["writes"]
        if name != "merge":
            entry[f"{name}_passes"] = row["passes"]
        entry[f"{name}_ms"] = _sig3(row["median_runtime_s"] * MS)
    _save_rows(table, "input_order_table.csv", "order")


# ---------- repeated values (Section 4.4) ----------

def _repeated_values_chart(rows, pdf):
    """Grouped bars: runtime per column, distinct values in the labels."""
    columns = list(dict.fromkeys(row["column"] for row in rows))
    distinct = {row["column"]: row["distinct_values"] for row in rows}
    labels = [f"{column}\n({distinct[column]:,} distinct)"
              for column in columns]
    subtitle = (f"n = {config.ORDER_N:,} per column, seed {config.SEED}, "
                f"median of {config.REPEATS} runs")
    fig, ax = _bar_chart(rows, "column", columns, labels,
                         "median_runtime_s")
    ax.yaxis.set_major_formatter(SECONDS)
    _finish(fig, ax, "Median runtime by column", subtitle,
            "Median runtime (seconds, log scale)", xlabel="Column",
            bars=True)
    _save(fig, "repeated_values.png", pdf)


def _repeated_values_table(rows):
    """Columns down the side: duplication, counts, runtimes and D20."""
    n = config.ORDER_N
    table = {}
    for row in rows:
        entry = table.setdefault(row["column"], {})
        for key in ("distinct_values", "most_frequent_count",
                    "values_repeated", "elements_in_repeats",
                    "equal_pairs"):
            entry[key] = row[key]
        name = row["algorithm"]
        entry[f"{name}_comparisons"] = row["comparisons"]
        entry[f"{name}_ms"] = _sig3(row["median_runtime_s"] * MS)
        if name == "bubble":
            # Bubble swaps once per out-of-order pair, never for equal
            # values; a random arrangement has half the unequal pairs.
            expected = round((n * (n - 1) / 2 - row["equal_pairs"]) / 2)
            entry["bubble_swaps"] = row["swaps"]
            entry["expected_bubble_swaps"] = expected
            entry["order_effect"] = row["swaps"] - expected
    _save_rows(table, "repeated_values_table.csv", "column")


# ---------- growth factors (Section 4.2, from H4) ----------

def _growth_factors_table(rows):
    """Doublings down the side; runtime and comparisons ratios per sort,
    then the theory (Q3, Q15)."""
    columns = [f"{name}_{ratio}" for name in ALGORITHMS
               for ratio in ("runtime", "comparisons")]
    columns += ["theory_n_squared", "theory_n_log_n"]
    table = {}
    for row in rows:
        key = f"{row['n_from']} to {row['n_to']}"
        entry = table.setdefault(key, {column: "" for column in columns})
        name = row["algorithm"]
        entry[f"{name}_runtime"] = f"{row['runtime_ratio']:.2f}"
        entry[f"{name}_comparisons"] = f"{row['comparisons_ratio']:.2f}"
        theory = ("theory_n_log_n" if name == "merge"
                  else "theory_n_squared")
        entry[theory] = f"{row['theory_ratio']:.2f}"
    _save_rows(table, "growth_factors_table.csv", "doubling")


# ---------- full dataset, Q4 ----------

def _full_size_table(estimates, full_size):
    """Estimates against the full-dataset runs (Q4), one row per sort."""
    average = {row.get("algorithm"): row["estimate_s"]
               for row in estimates if row["n"] == "average"}
    actual = {row["algorithm"]: row["runtime_s"] for row in full_size}

    table = {}
    for name, source in (("bubble", "estimate + check"),
                         ("selection", "estimate"), ("merge", "measured")):
        estimate = average.get(name) if name != "merge" else None
        measured = actual.get(name) if name != "selection" else None
        difference = ""
        if estimate and measured:
            difference = f"{(measured - estimate) / estimate * 100:.1f}"
        table[name] = {
            "estimate_s": _sig3(estimate) if estimate else "",
            "actual_s": _sig3(measured) if measured else "",
            "source": source,
            "difference_pct": difference,
        }
    _save_rows(table, "full_size_table.csv", "algorithm")


# ---------- decision guide (D17) ----------

def _decision_guide_evidence(scaling, full_size, input_order, repeated):
    """Pick out the numbers for each decision-guide row (D17)."""
    groups = []
    for n in (config.SCALING_SIZES[-1],):
        groups.append(("Large random input", "scaling.csv", n,
                       _pick(scaling, n=n)))
    # Merge only: the bubble check is evidence for Q4, not the guide.
    groups.append(("Large random input", "full_size.csv", config.FULL_SIZE,
                   _pick(full_size, algorithm="merge")))
    for n in (size for size in config.SCALING_SIZES
              if size <= config.SMALL_N_MAX):
        groups.append(("Very small list (n < 20)", "scaling.csv", n,
                       _pick(scaling, n=n)))
    for order, situation in (("sorted", "Already sorted input"),
                             ("nearly_sorted", "Nearly sorted input"),
                             ("reverse", "Reverse-sorted input")):
        groups.append((situation, "input_order.csv", config.ORDER_N,
                       _pick(input_order, order=order)))
    for column in ("housing_median_age", config.SCALING_COLUMN):
        groups.append(("Many repeated values",
                       f"repeated_values.csv: {column}", config.ORDER_N,
                       _pick(repeated, column=column)))

    fields = ("situation", "source", "n", "algorithm", "comparisons",
              "writes", "passes", "median_runtime_s", "fastest")
    out = []
    for situation, source, n, rows in groups:
        times = [_runtime(row) for row in rows]
        for row in rows:
            fastest = len(rows) > 1 and _runtime(row) == min(times)
            out.append({
                "situation": situation, "source": source, "n": n,
                "algorithm": row["algorithm"],
                "comparisons": row["comparisons"], "writes": row["writes"],
                "passes": row["passes"],
                "median_runtime_s": _runtime(row),
                "fastest": "yes" if fastest else "",
            })
    path = config.TABLES_DIR / "decision_guide_evidence.csv"
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)
    print("Saved tables/decision_guide_evidence.csv")


def _pick(rows, **filters):
    """Rows whose values match every filter, e.g. _pick(rows, n=20)."""
    return [row for row in rows
            if all(row[key] == value for key, value in filters.items())]


def _runtime(row):
    """Runtime in seconds from either results format."""
    return row.get("median_runtime_s", row.get("runtime_s"))


# ---------- shared helpers ----------

def _read_csv(folder, filename):
    """Read folder/filename; numbers become int or float.

    Returns an empty list (and prints a message) if the file is missing.
    """
    path = Path(folder) / filename
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


def _line_chart(rows, measure, log):
    """One line per sort: measure against n. Returns (fig, ax)."""
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for algorithm in ALGORITHMS:
        points = [row for row in rows if row["algorithm"] == algorithm]
        ax.plot([row["n"] for row in points],
                [row[measure] for row in points],
                label=algorithm, **STYLES[algorithm])
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    sizes = list(dict.fromkeys(row["n"] for row in rows))  # file order
    ax.set_xticks(sizes)
    ax.set_xticklabels([f"{size:,}" for size in sizes])
    ax.xaxis.set_minor_locator(NullLocator())
    return fig, ax


def _bar_chart(rows, group_key, groups, labels, measure):
    """Grouped bars on a log axis: one group per key, one bar per sort."""
    fig, ax = plt.subplots(figsize=FIGSIZE)
    width = 0.8 / len(ALGORITHMS)
    for index, algorithm in enumerate(ALGORITHMS):
        values = [
            _pick(rows, **{group_key: group, "algorithm": algorithm})[0]
            [measure] for group in groups
        ]
        positions = [g + (index - 1) * width for g in range(len(groups))]
        ax.bar(positions, values, width, label=algorithm,
               color=STYLES[algorithm]["color"])
    ax.set_yscale("log")
    top = max(row[measure] for row in rows)
    ax.set_ylim(top=top * 30)  # room above the bars for the legend
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(labels)
    ax.grid(False, axis="x")
    return fig, ax


def _finish(fig, ax, title, subtitle, ylabel, xlabel="Input size n (values)",
            bars=False):
    """Bold title, grey settings subtitle, labels and legend."""
    fig.suptitle(title, fontsize=13, fontweight="bold")
    ax.set_title(subtitle, color="grey")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if bars:  # one row across the top, above the tallest bar
        ax.legend(loc="upper center", ncol=len(ALGORITHMS), frameon=False)
    else:
        ax.legend(title="Sort", loc="best")
    fig.tight_layout()


def _save(fig, filename, pdf):
    """Save one chart as a PNG and as a page of the combined PDF."""
    fig.savefig(config.PLOTS_DIR / filename, dpi=DPI)
    pdf.savefig(fig)
    plt.close(fig)
    print(f"Saved plots/{filename}")


def _sig3(value):
    """Text with 3 significant figures, e.g. 0.00211, 4.27, 333, 1130."""
    if value == 0:
        return "0"
    decimals = max(0, 2 - math.floor(math.log10(abs(value))))
    return f"{float(f'{value:.3g}'):.{decimals}f}"


def _pivot(rows, row_key, measure, scale=None):
    """One row per row_key, one column per sort; scale converts units."""
    table = {}
    for row in rows:
        value = row[measure]
        if scale:
            value = _sig3(value * scale)
        table.setdefault(row[row_key], {})[row["algorithm"]] = value
    return table


def _save_table(table, filename, row_label, suffix=""):
    """Save a pivoted table: sorts across the top, unit in the header."""
    headers = [f"{name}{suffix}" for name in ALGORITHMS]
    path = config.TABLES_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([row_label, *headers])
        for key, values in table.items():
            writer.writerow([key, *(values.get(a, "") for a in ALGORITHMS)])
    print(f"Saved tables/{filename}")


def _save_rows(table, filename, row_label):
    """Save a table whose rows already hold named columns."""
    fields = list(dict.fromkeys(key for row in table.values() for key in row))
    path = config.TABLES_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([row_label, *fields])
        for key, values in table.items():
            writer.writerow([key, *(values.get(f, "") for f in fields)])
    print(f"Saved tables/{filename}")
