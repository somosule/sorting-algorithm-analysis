"""Collate every results table and chart into one formatted workbook.

make_workbook() reads the finished results files (it never changes a
result) and writes results/results_workbook.xlsx:
- Contents: the run details and a linked list of every sheet.
- Questions: every question in the brief (4.2 to 4.6) with the key
  numbers from this run, calculated here, and a link to the evidence.
- One sheet per section of the brief: titled tables with readable headings
  and the matching charts beside them; then the raw results.
The written explanations belong in the report; this sheet gives the numbers.
Extension tables appear only if their optional step ran in this run (from
run_info.csv), so leftovers from an earlier run are never shown.
Rebuild the workbook alone from the current results: python3 -m src.make_workbook
Needs openpyxl (pip install openpyxl); main.py skips the workbook without it.
"""
import csv
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src import config

try:
    from openpyxl.drawing.image import Image
except ImportError:  # Pillow missing: tables only, no charts
    Image = None

NAVY = "1F3864"
GREY = "595959"
LINK = "0563C1"
HEADER_FILL = PatternFill("solid", fgColor="DCE6F1")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CHART_WIDTH = 560  # pixels; charts keep their proportions
WORKBOOK_NAME = "results_workbook.xlsx"

# Sheet name, one-line description, (title, file) tables, chart files.
SECTIONS = [
    ("Data profile", "Brief Section 3: the dataset inspected in code before any sampling.",
     [("Dataset profile", "dataset_summary.csv")], []),
    ("4.2 Scaling", "Brief 4.2: runtime, comparisons and writes as the input size grows.",
     [("Median runtime by input size (ms), including all 20,640 values (Q5; decision guide)",
       "tables/scaling_runtime_table.csv"),
      ("Comparisons by input size (Q3, Q15)", "tables/scaling_comparisons_table.csv"),
      ("Very small inputs: median time per call in µs (Q5; decision guide, very small list)",
       "tables/scaling_small_n_table.csv")],
     ["scaling_runtime.png", "scaling_runtime_loglog.png",
      "scaling_comparisons.png", "scaling_writes.png"]),
    ("4.2 Growth (Q3)", "Brief 4.2 step 3: how much each measure grows when n doubles, "
     "against theory.",
     [("Growth factors when n doubles", "tables/scaling_growth_factors_table.csv")], []),
    ("4.2 Full data (Q4)", "Brief 4.2 step 4: estimates for all 20,640 values against the "
     "full-dataset runs.",
     [("Estimates against the full-dataset runs", "tables/scaling_full_size_table.csv"),
      ("Working: estimate from each measured size", "bubble_estimate.csv"),
      ("Full-dataset runs", "full_size.csv")], []),
    ("4.3 Input order", "Brief 4.3: the same sample in random, sorted, nearly sorted and "
     "reverse order.",
     [("Comparisons by input order (Q6, Q7, Q8)", ("derived", "_order_comparisons")),
      ("Writes and swaps by input order (Q10, Q13)", ("derived", "_order_writes")),
      ("Passes by input order (Q6, Q11, Q13)", ("derived", "_order_passes")),
      ("Median runtime by input order, fastest marked (Q9; decision guide)",
       ("derived", "_order_runtime")),
      ("All measures", "tables/input_order_table.csv")],
     ["input_order_comparisons.png", "input_order_runtime.png"]),
    ("4.4 Repeated values", "Brief 4.4: columns with different amounts of duplication.",
     [("Duplication in each column (Q12)", ("derived", "_dup_stats")),
      ("Comparisons by column (Q12)", ("derived", "_dup_comparisons")),
      ("Bubble sort swaps against a random arrangement (Q12: duplication or order?)",
       ("derived", "_dup_swaps")),
      ("Median runtime by column, fastest marked (Q12; decision guide)",
       ("derived", "_dup_runtime")),
      ("All measures", "tables/repeated_values_table.csv")],
     ["repeated_values.png"]),
    ("Decision guide", "Brief 4.5: the evidence behind each row of the decision guide.",
     [("Decision-guide evidence", "tables/decision_guide_evidence.csv")], []),
    ("Extras", "Optional steps, kept separate from the main results (D23).",
     [("Peak memory per sort (Q16)", "memory.csv"),
      ("Record lookup: top records", "top_records.csv"),
      ("total_bedrooms: before and after the estimate", "total_bedrooms_before_after.csv"),
      ("total_bedrooms: accuracy of each method", "total_bedrooms_method_check.csv"),
      ("total_bedrooms: the 207 estimated values", "total_bedrooms_filled.csv")], []),
    ("Run info", "The settings, machine and optional steps of this run.",
     [("Run details", "run_info.csv")], []),
    ("Raw results", "The raw results files, full precision, as written by main.py.",
     [("scaling.csv", "scaling.csv"), ("input_order.csv", "input_order.csv"),
      ("repeated_values.csv", "repeated_values.csv"),
      ("growth_factors.csv", "growth_factors.csv")], []),
]

# Extension outputs and the optional step that writes them (D28). A file from an
# earlier run whose step is off in this run is left out of the workbook.
EXTENSION_FILES = {
    "top_records.csv": "record-lookup",
    "total_bedrooms_filled.csv": "missing-values",
    "total_bedrooms_before_after.csv": "missing-values",
    "total_bedrooms_method_check.csv": "missing-values",
}

WORDS = {"csv": "CSV", "ms": "(ms)", "us": "(µs)", "s": "(s)", "pct": "(%)", "kib": "(KiB)"}


def make_workbook(results_dir=None, out_path=None):
    """Write the workbook from the results folder and return its path."""
    results = Path(results_dir) if results_dir else config.RESULTS_DIR
    out_path = Path(out_path) if out_path else results / WORKBOOK_NAME
    captions = _read_captions(results / "tables" / "captions.md")
    info = {r["setting"]: r["value"] for r in _read_csv(results / "run_info.csv")}
    extras = info.get("extras_run", "")

    book = Workbook()
    contents = book.active
    contents.title = "Contents"
    questions = book.create_sheet("Questions")
    listing = []
    for sheet_name, intro, tables, charts in SECTIONS:
        present = [(title, source) for title, source in tables
                   if isinstance(source, tuple) or ((results / source).exists()
                                                    and _from_this_run(source, extras))]
        if not present:
            continue
        sheet = book.create_sheet(sheet_name)
        _build_sheet(sheet, sheet_name, intro, present, charts, results, captions)
        listing.append((sheet_name, intro, [title for title, _ in present], charts))
    _build_questions(questions, results, {name for name, *_ in listing})
    _build_contents(contents, listing, results)
    book.save(out_path)
    return out_path


# ---------- section sheets ----------

def _build_sheet(sheet, name, intro, tables, charts, results, captions):
    _heading(sheet, name, intro)
    row, widest = 4, 1
    derived = _Derived(results)
    for title, source in tables:
        if isinstance(source, tuple):  # built here from the raw results file
            rows, note = getattr(derived, source[1])()
            row, width = _write_table(sheet, row, title, note, None, rows)
        else:
            rows = _read_csv(results / source)
            caption = captions.get(Path(source).name) or captions.get(_raw_name(source))
            row, width = _write_table(sheet, row, title, caption, source, rows)
        widest = max(widest, width)
    if charts and Image is not None:
        _place_charts(sheet, charts, results / "plots", widest + 2)
    sheet.freeze_panes = "A4"


def _write_table(sheet, row, title, caption, filename, rows):
    sheet.cell(row, 1, title).font = Font(size=12, bold=True)
    row += 1
    if filename is None:
        note = caption
    elif caption:
        note = f"{caption}  (file: results/{filename})"
    else:
        note = f"File: results/{filename}"
    sheet.cell(row, 1, note).font = Font(size=9, color=GREY)
    row += 1
    if not rows:
        return row + 1, 1
    headers = list(rows[0].keys())
    for col, header in enumerate(headers, start=1):
        _header_cell(sheet.cell(row, col, _label(header)))
    sheet.row_dimensions[row].height = 45 if max(len(_label(h)) for h in headers) > 24 else 30
    for record in rows:
        row += 1
        for col, header in enumerate(headers, start=1):
            value = _number(record[header])
            cell = sheet.cell(row, col, value)
            cell.border = BORDER
            if value == "fastest":
                cell.font = Font(bold=True, color="375623")
            if isinstance(value, int):
                cell.number_format = "#,##0"
            elif isinstance(value, float) and filename and not filename.startswith("tables/"):
                cell.number_format = "#,##0.000###"  # raw files: up to 6 decimals
            if isinstance(value, (int, float)):
                cell.alignment = Alignment(horizontal="right")
    for col, header in enumerate(headers, start=1):
        letter = get_column_letter(col)
        longest = max([len(_label(header)) // 2 + 2] +
                      [len(str(record[header])) + 2 for record in rows])
        current = sheet.column_dimensions[letter].width or 0
        sheet.column_dimensions[letter].width = max(current, min(longest, 40), 10)
    return row + 3, len(headers)


def _place_charts(sheet, charts, plots, first_col):
    anchor_row = 4
    for name in charts:
        path = plots / name
        if not path.exists():
            continue
        picture = Image(str(path))
        scale = CHART_WIDTH / picture.width
        picture.width, picture.height = CHART_WIDTH, int(picture.height * scale)
        sheet.add_image(picture, f"{get_column_letter(first_col)}{anchor_row}")
        anchor_row += int(picture.height / 20) + 2  # about 20 pixels per row


# ---------- focused tables for 4.3 and 4.4 (built from the raw files) ----------

ORDER_NAMES = {"random": "Random", "sorted": "Sorted", "reverse": "Reverse",
               "nearly_sorted": "Nearly sorted"}


class _Derived:
    """Small tables shaped around the questions, from the raw results files.

    Each method returns (rows, note): rows are dicts with readable headings.
    """

    def __init__(self, folder):
        self.order = _numeric(_read_csv(folder / "input_order.csv"))
        self.repeated = _numeric(_read_csv(folder / "repeated_values.csv"))
        self.n = config.ORDER_N
        self.source = (f"n = {self.n:,}, seed {config.SEED}, median of "
                       f"{config.REPEATS} runs")

    def _by(self, rows, key):
        """{group: {algorithm: row}} in file order."""
        groups = {}
        for row in rows:
            groups.setdefault(row[key], {})[row["algorithm"]] = row
        return groups

    def _runtime_rows(self, groups, label, names):
        out = []
        for group, sorts in groups.items():
            times = {name: sorts[name]["median_runtime_s"] for name in sorts}
            best = min(times, key=times.get)
            entry = {label: names.get(group, group)}
            for name in config.ALGORITHM_NAMES:
                entry[f"{name.capitalize()} (ms)"] = float(f"{times[name] * 1000:.3g}")
            entry["Fastest"] = best
            out.append(entry)
        return out

    def _order_comparisons(self):
        rows = [{"Order": ORDER_NAMES.get(order, order),
                 **{name.capitalize(): sorts[name]["comparisons"]
                    for name in config.ALGORITHM_NAMES}}
                for order, sorts in self._by(self.order, "order").items()]
        note = (f"Input order (4.3): {self.source}. For reference, n - 1 = {self.n - 1:,} "
                f"and n(n - 1)/2 = {self.n * (self.n - 1) // 2:,}.  (from results/input_order.csv)")
        return rows, note

    def _order_writes(self):
        rows = []
        for order, sorts in self._by(self.order, "order").items():
            rows.append({"Order": ORDER_NAMES.get(order, order),
                         "Bubble writes": sorts["bubble"]["writes"],
                         "Bubble swaps": sorts["bubble"]["swaps"],
                         "Selection writes": sorts["selection"]["writes"],
                         "Selection swaps": sorts["selection"]["swaps"],
                         "Merge writes": sorts["merge"]["writes"]})
        note = (f"Input order (4.3): {self.source}. A swap is 2 writes; merge sort writes "
                "each value placed into the merged list.  (from results/input_order.csv)")
        return rows, note

    def _order_passes(self):
        rows = [{"Order": ORDER_NAMES.get(order, order),
                 "Bubble passes": sorts["bubble"]["passes"],
                 "Selection passes": sorts["selection"]["passes"]}
                for order, sorts in self._by(self.order, "order").items()]
        swaps = int(config.NEARLY_SORTED_SWAP_FRACTION * self.n)
        note = (f"Input order (4.3): {self.source}. Nearly sorted = the sorted list after "
                f"{swaps} random swaps; merge sort has no passes.  (from results/input_order.csv)")
        return rows, note

    def _order_runtime(self):
        rows = self._runtime_rows(self._by(self.order, "order"), "Order", ORDER_NAMES)
        return rows, f"Input order (4.3): {self.source}.  (from results/input_order.csv)"

    def _dup_stats(self):
        rows = []
        for column, sorts in self._by(self.repeated, "column").items():
            first = sorts["bubble"]
            rows.append({"Column": column,
                         "Distinct values": first["distinct_values"],
                         "Most frequent count": first["most_frequent_count"],
                         "Values repeated": first["values_repeated"],
                         "Elements in repeats": first["elements_in_repeats"],
                         "Equal pairs": first["equal_pairs"]})
        note = (f"Repeated values (4.4): {self.source}, same sample positions in each "
                "column.  (from results/repeated_values.csv)")
        return rows, note

    def _dup_comparisons(self):
        rows = [{"Column": column,
                 **{name.capitalize(): sorts[name]["comparisons"]
                    for name in config.ALGORITHM_NAMES}}
                for column, sorts in self._by(self.repeated, "column").items()]
        return rows, f"Repeated values (4.4): {self.source}.  (from results/repeated_values.csv)"

    def _dup_swaps(self):
        rows = []
        pairs = self.n * (self.n - 1) / 2
        for column, sorts in self._by(self.repeated, "column").items():
            bubble = sorts["bubble"]
            expected = round((pairs - bubble["equal_pairs"]) / 2)
            rows.append({"Column": column,
                         "Bubble swaps": bubble["swaps"],
                         "Expected for a random arrangement": expected,
                         "Difference (order effect)": bubble["swaps"] - expected})
        note = ("Bubble sort swaps once per out-of-order pair and never for equal values; a "
                "random arrangement has half the unequal pairs out of order (D20). The "
                "difference is the effect of this sample's order, not of duplication.  "
                "(from results/repeated_values.csv)")
        return rows, note

    def _dup_runtime(self):
        rows = self._runtime_rows(self._by(self.repeated, "column"), "Column", {})
        return rows, f"Repeated values (4.4): {self.source}.  (from results/repeated_values.csv)"


# ---------- questions sheet ----------

QUESTIONS = [
    ("4.2 step 1", "Random samples of increasing size with a recorded seed, including very "
     "small sizes.", "4.2 Scaling", "_q_sizes"),
    ("4.2 step 2", "Runtime, comparisons and writes per size; median of at least 5 timings; "
     "a loop of repetitions for very small inputs.", "Run info", "_q_method"),
    ("Q3 (4.2 step 3)", "Observed runtime growth factor when n doubles, against O(n²) and "
     "O(n log n); why measurements may differ from theory.", "4.2 Growth (Q3)", "_q_growth"),
    ("Q4 (4.2 step 4)", "Estimate bubble sort on 20,640 values, with the calculation and "
     "assumptions; the optional full-size check.", "4.2 Full data (Q4)", "_q_estimate"),
    ("Q5 (4.2 step 5)", "Input sizes at which merge sort's advantage becomes apparent; why it "
     "is less visible for very small inputs.", "4.2 Scaling", "_q_crossover"),
    ("Q6", "Bubble sort with early termination on sorted data: about n - 1 comparisons and no "
     "swaps. Why?", "4.3 Input order", "_q6"),
    ("Q7", "Selection sort makes about n(n - 1)/2 comparisons even on sorted input. Why?",
     "4.3 Input order", "_q7"),
    ("Q8", "Why merge sort's comparison count changes less with input order than bubble "
     "sort's.", "4.3 Input order", "_q8"),
    ("Q9", "Best-performing algorithm for each input order, justified in 2-3 sentences.",
     "4.3 Input order", "_q9"),
    ("Q10", "Bubble sort's worst-case arrangement among the four inputs, and why.",
     "4.3 Input order", "_q10"),
    ("Q11", "Does early termination help much on nearly sorted input? Why a few out-of-place "
     "values can still force many passes.", "4.3 Input order", "_q11"),
    ("Q12", "Comparisons, writes and runtimes across the three columns: what is due to "
     "duplication, and what to order or implementation.", "4.4 Repeated values", "_q12"),
    ("Decision guide (4.5)", "Best algorithm for each situation, with evidence from our "
     "results.", "Decision guide", "_q_guide"),
    ("Q13", "Bubble and selection sort are both O(n²). Why can they behave differently on "
     "sorted input?", "4.3 Input order", "_q13"),
    ("Q14", "One realistic reason to choose selection or bubble sort over merge sort.",
     "4.2 Scaling", "_q14"),
    ("Q15", "Why the measured slowdown when doubling n is not exactly 4x or 2x (two "
     "reasons).", "4.2 Growth (Q3)", "_q_growth_range"),
    ("Q16", "How merge sort's extra memory affects the choice of algorithm.", "Extras",
     "_q16"),
    ("Q17", "Why the same input and a consistent measurement method matter.", "Run info",
     "_q17"),
]


def _build_questions(sheet, results, sheets):
    _heading(sheet, "Questions", "Every question in the brief, with the key numbers from "
             "this run (calculated from the results files) and a link to the evidence. "
             "The explanations go in the report.")
    data = _Results(results)
    row = 4
    for col, header in enumerate(("Question", "What the brief asks",
                                  "Key numbers from this run", "Evidence"), start=1):
        _header_cell(sheet.cell(row, col, header))
    for label, asks, target, method in QUESTIONS:
        row += 1
        try:
            numbers = getattr(data, method)()
        except (KeyError, ValueError, ZeroDivisionError, IndexError, TypeError):
            numbers = "See the evidence sheet."
        values = (label, asks, numbers, f"{target} sheet" if target in sheets else "")
        for col, value in enumerate(values, start=1):
            cell = sheet.cell(row, col, value)
            cell.border = BORDER
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        sheet.cell(row, 1).font = Font(bold=True)
        if target in sheets:
            sheet.cell(row, 4).hyperlink = f"#'{target}'!A1"
            sheet.cell(row, 4).font = Font(color=LINK, underline="single")
    for letter, width in zip("ABCD", (18, 48, 70, 20)):
        sheet.column_dimensions[letter].width = width
    sheet.freeze_panes = "A5"


class _Results:
    """The results files, with one method per question returning its key numbers."""

    def __init__(self, folder):
        self.scaling = _numeric(_read_csv(folder / "scaling.csv"))
        self.order = _numeric(_read_csv(folder / "input_order.csv"))
        self.repeated = _numeric(_read_csv(folder / "repeated_values.csv"))
        self.growth = _numeric(_read_csv(folder / "growth_factors.csv"))
        self.full = _numeric(_read_csv(folder / "tables" / "scaling_full_size_table.csv"))
        self.memory = _numeric(_read_csv(folder / "memory.csv"))
        self.guide = _numeric(_read_csv(folder / "tables" / "decision_guide_evidence.csv"))
        self.info = {r["setting"]: r["value"] for r in _read_csv(folder / "run_info.csv")}

    def _row(self, rows, **match):
        return next(r for r in rows if all(r[k] == v for k, v in match.items()))

    def _q_sizes(self):
        return (f"{self.info['scaling_column']}, seed {self.info['seed']}; "
                f"n = {self.info['scaling_sizes']}; all three sorts on the same sample at "
                "each size.")

    def _q_method(self):
        return (f"Median of {self.info['runs_per_timing']} timings on the same input; "
                f"n <= {config.SMALL_N_MAX} timed as a loop of "
                f"{int(self.info['small_n_loop_size']):,} calls. "
                f"{self.info['counts_identical_across_repeats'].capitalize()}.")

    def _q_growth(self):
        lines = []
        for name in config.ALGORITHM_NAMES:
            rows = [r for r in self.growth if r["algorithm"] == name]
            runtime = [r["runtime_ratio"] for r in rows]
            comparisons = [r["comparisons_ratio"] for r in rows]
            lines.append(f"{name}: runtime {_span(runtime)}; comparisons "
                         f"{_span(comparisons)}; theory "
                         f"{_span([r['theory_ratio'] for r in rows])}")
        return "\n".join(lines)

    def _q_estimate(self):
        bubble = self._row(self.full, algorithm="bubble")
        merge = self._row(self.full, algorithm="merge")
        selection = self._row(self.full, algorithm="selection")
        text = f"Bubble estimate {bubble['estimate_s']} s"
        if bubble["actual_s"] != "":
            text += (f"; actual (one run) {bubble['actual_s']} s, "
                     f"{bubble['difference_pct']:+}% from the estimate")
        return (text + f". Selection estimate {selection['estimate_s']} s. "
                f"Merge measured {merge['actual_s']} s. Estimate = runtime x "
                f"({config.FULL_SIZE:,} / n)² from n = 1,000, 2,000, 4,000, averaged.")

    def _q_crossover(self):
        sizes = list(dict.fromkeys(r["n"] for r in self.scaling))
        fastest = {}
        for n in sizes:
            rows = [r for r in self.scaling if r["n"] == n]
            fastest[n] = min(rows, key=lambda r: r["median_runtime_s"])["algorithm"]
        from_n = None
        for n in sizes:
            if all(fastest[m] == "merge" for m in sizes if m >= n):
                from_n = n
                break
        small = ", ".join(f"n = {n}: {fastest[n]}" for n in sizes if n <= config.SMALL_N_MAX)
        lead = (f"Merge sort is fastest at every size from n = {from_n:,}."
                if from_n else "Merge sort is not fastest at the largest size.")
        return f"{lead} Fastest at very small sizes: {small}."

    def _q6(self):
        row = self._row(self.order, order="sorted", algorithm="bubble")
        n = config.ORDER_N
        return (f"Sorted, n = {n:,}: bubble {row['comparisons']:,} comparisons "
                f"(n - 1 = {n - 1:,}), {row['swaps']:,} swaps, {row['passes']} pass.")

    def _q7(self):
        n = config.ORDER_N
        counts = ", ".join(f"{r['order'].replace('_', ' ')} {r['comparisons']:,}"
                           for r in self.order if r["algorithm"] == "selection")
        return f"Selection comparisons: {counts}; n(n - 1)/2 = {n * (n - 1) // 2:,}."

    def _q8(self):
        parts = []
        for name in ("merge", "bubble"):
            counts = [r["comparisons"] for r in self.order if r["algorithm"] == name]
            parts.append(f"{name}: {min(counts):,} to {max(counts):,} comparisons "
                         f"across the four orders")
        return "; ".join(parts) + "."

    def _fastest_by(self, rows, key):
        groups = list(dict.fromkeys(r[key] for r in rows))
        out = []
        for group in groups:
            members = [r for r in rows if r[key] == group]
            best = min(members, key=lambda r: r["median_runtime_s"])
            out.append((group, best))
        return out

    def _q9(self):
        return "\n".join(f"{order.replace('_', ' ')}: {best['algorithm']} "
                         f"({best['median_runtime_s'] * 1000:,.3g} ms)"
                         for order, best in self._fastest_by(self.order, "order"))

    def _q10(self):
        rows = [r for r in self.order if r["algorithm"] == "bubble"]
        worst = max(rows, key=lambda r: r["median_runtime_s"])
        most = max(rows, key=lambda r: r["swaps"])
        return (f"Slowest for bubble: {worst['order'].replace('_', ' ')} "
                f"({worst['median_runtime_s'] * 1000:,.3g} ms). Most swaps: "
                f"{most['order'].replace('_', ' ')} ({most['swaps']:,} swaps, "
                f"{most['passes']:,} passes).")

    def _q11(self):
        bubble = {r["order"]: r for r in self.order if r["algorithm"] == "bubble"}
        near, rand, done = bubble["nearly_sorted"], bubble["random"], bubble["sorted"]
        swaps = int(config.NEARLY_SORTED_SWAP_FRACTION * config.ORDER_N)
        return (f"Bubble passes: sorted {done['passes']}, nearly sorted {near['passes']:,} "
                f"(after only {swaps} swaps), random {rand['passes']:,}. Nearly sorted "
                f"runtime is {near['median_runtime_s'] / rand['median_runtime_s']:.0%} of "
                "random.")

    def _q12(self):
        lines = []
        for column in dict.fromkeys(r["column"] for r in self.repeated):
            rows = {r["algorithm"]: r for r in self.repeated if r["column"] == column}
            first = next(iter(rows.values()))
            lines.append(f"{column}: {first['distinct_values']:,} distinct, "
                         f"{first['equal_pairs']:,} equal pairs; bubble swaps "
                         f"{rows['bubble']['swaps']:,}; merge comparisons "
                         f"{rows['merge']['comparisons']:,}")
        return "\n".join(lines)

    def _q_guide(self):
        lines = []
        for situation in dict.fromkeys(r["situation"] for r in self.guide):
            winners = [f"{r['algorithm']} ({r['source']}, n = {r['n']:,})"
                       for r in self.guide
                       if r["situation"] == situation and r["fastest"] == "yes"]
            lines.append(f"{situation}: fastest {'; '.join(winners) or 'see sheet'}")
        return "\n".join(lines)

    def _q13(self):
        rows = {r["algorithm"]: r for r in self.order if r["order"] == "sorted"}
        return (f"Sorted, n = {config.ORDER_N:,}: bubble {rows['bubble']['comparisons']:,} "
                f"comparisons, {rows['bubble']['passes']} pass; selection "
                f"{rows['selection']['comparisons']:,} comparisons, "
                f"{rows['selection']['passes']:,} passes.")

    def _q14(self):
        rows = {r["algorithm"]: r for r in self.order if r["order"] == "random"}
        small = [r for r in self.scaling if r["n"] == min(r["n"] for r in self.scaling)]
        best = min(small, key=lambda r: r["median_runtime_s"])
        return (f"Random, n = {config.ORDER_N:,}: writes selection "
                f"{rows['selection']['writes']:,}, bubble {rows['bubble']['writes']:,}, "
                f"merge {rows['merge']['writes']:,}. At n = {best['n']}, fastest is "
                f"{best['algorithm']}.")

    def _q_growth_range(self):
        quadratic = [r["runtime_ratio"] for r in self.growth if r["algorithm"] != "merge"]
        merge = [r["runtime_ratio"] for r in self.growth if r["algorithm"] == "merge"]
        return (f"Bubble and selection runtime ratios x{min(quadratic):.2f} to "
                f"x{max(quadratic):.2f} (theory x4.00); merge x{min(merge):.2f} to "
                f"x{max(merge):.2f} (theory about x2.2). Comparisons ratios sit much "
                "closer to theory (see Q3).")

    def _q16(self):
        return "Peak memory (n = 2,000): " + ", ".join(
            f"{r['algorithm']} {r['peak_kib']} KiB" for r in self.memory) + "."

    def _q17(self):
        return (f"Every sort ran on the same samples (seed {self.info['seed']}); counts are "
                "identical across repeats and on every computer; times are the median of "
                f"{self.info['runs_per_timing']} runs with time.perf_counter() around the "
                "sort call only.")


# ---------- contents sheet and shared helpers ----------

def _build_contents(sheet, listing, results):
    info = {r["setting"]: r["value"] for r in _read_csv(results / "run_info.csv")}
    _heading(sheet, "Sorting Algorithm Analysis: results workbook",
             f"Run {info.get('date_time', '')}; Python {info.get('python_version', '')}; "
             f"optional steps: {info.get('extras_run', '')}; seed {info.get('seed', '')}")
    row = 4
    for col, header in enumerate(("Sheet", "What it shows", "Tables", "Charts"), start=1):
        _header_cell(sheet.cell(row, col, header))
    entries = [("Questions", "Every question in the brief, with the key numbers from this "
                "run and a link to the evidence.", ["Questions and key numbers"], [])]
    for name, intro, tables, charts in entries + listing:
        row += 1
        values = (name, intro, "\n".join(tables), "\n".join(charts) or "-")
        for col, value in enumerate(values, start=1):
            cell = sheet.cell(row, col, value)
            cell.border = BORDER
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        sheet.cell(row, 1).hyperlink = f"#'{name}'!A1"
        sheet.cell(row, 1).font = Font(color=LINK, underline="single")
    for letter, width in zip("ABCD", (22, 55, 55, 30)):
        sheet.column_dimensions[letter].width = width


def _from_this_run(filename, extras_run):
    """False for an extension file whose optional step did not run this time."""
    step = EXTENSION_FILES.get(Path(filename).name)
    return step is None or step in extras_run


def _span(values):
    """x3.97 to x4.04, or x4.00 when every value rounds the same."""
    low, high = f"x{min(values):.2f}", f"x{max(values):.2f}"
    return low if low == high else f"{low} to {high}"


def _heading(sheet, title, subtitle):
    sheet["A1"] = title
    sheet["A1"].font = Font(size=16, bold=True, color=NAVY)
    sheet["A2"] = subtitle
    sheet["A2"].font = Font(italic=True, color=GREY)
    sheet.sheet_view.showGridLines = False


def _header_cell(cell):
    cell.font = Font(bold=True)
    cell.fill = HEADER_FILL
    cell.border = BORDER
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _read_csv(path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _numeric(rows):
    return [{key: _number(value) for key, value in row.items()} for row in rows]


def _read_captions(path):
    if not path.exists():
        return {}
    pattern = re.compile(r"- \*\*(.+?)\*\*: (.+)")
    matches = map(pattern.match, path.read_text(encoding="utf-8").splitlines())
    return {m.group(1): m.group(2) for m in matches if m}


def _raw_name(filename):
    """Caption key for a report table: the raw results file it comes from."""
    name = Path(filename).name
    return {"scaling_runtime_table.csv": "scaling.csv",
            "scaling_comparisons_table.csv": "scaling.csv",
            "scaling_small_n_table.csv": "scaling.csv",
            "scaling_growth_factors_table.csv": "growth_factors.csv",
            "input_order_table.csv": "input_order.csv",
            "repeated_values_table.csv": "repeated_values.csv"}.get(name, name)


def _label(header):
    """bubble_ms -> Bubble (ms); median_runtime_s -> Median runtime (s)."""
    if header == "n" or header != header.lower() or " " in header:
        return header
    text = " ".join(WORDS.get(part, part) for part in header.split("_"))
    return text[:1].upper() + text[1:]


def _number(text):
    if isinstance(text, (int, float)):
        return text
    for convert in (int, float):
        try:
            return convert(text)
        except (TypeError, ValueError):
            pass
    return text


if __name__ == "__main__":
    print(f"Saved {make_workbook()}")
