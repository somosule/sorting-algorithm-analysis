"""Non-persistent, exploratory sorting experiments selected from a menu."""
import random
import time

from src import config
from src.data_profile import duplication_stats
from src.experiments import build_orders
from src.growth_estimate import bubble_estimate, growth_factors
from src.load_data import load_column
from src.measure import run_algorithm, verify_sorted
from src.record_lookup import SHOW, find_top_records
from src.sorts import ALGORITHMS

NUMERIC_COLUMNS = (
    "longitude",
    "latitude",
    "housing_median_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "median_income",
    "median_house_value",
)
TINY_SIZES = (5, 10, 20)
CROSSOVER_SIZES = (50, 100)
LARGE_SIZES = (250, 500, 1000, 2000, 4000)
ALL_SCALING_SIZES = TINY_SIZES + CROSSOVER_SIZES + LARGE_SIZES
SAMPLE_SIZES = (1000, 2000, 4000)
LOOKUP_DEFAULT_ROWS = 5
LOOKUP_MAX_ROWS = 20


def _calculate_rows(experiment, sizes, seed, values_by_column):
    """Calculate experiment rows without prompting or writing result files."""
    rows = []

    if experiment == "scaling":
        values = next(iter(values_by_column.values()))
        for n in sizes:
            sample = random.Random(seed).sample(values, n)
            duplicates = duplication_stats(sample)
            for name, sort_fn in ALGORITHMS.items():
                runtime, stats, loop_reps = run_algorithm(sort_fn, sample)
                rows.append({
                    "n": n,
                    "algorithm": name,
                    **stats,
                    "median_runtime_s": runtime,
                    "loop_reps": loop_reps,
                    "distinct_values": duplicates["distinct_values"],
                    "equal_pairs": duplicates["equal_pairs"],
                })
        return rows

    if experiment == "input order":
        values = next(iter(values_by_column.values()))
        n = sizes[0]
        base = random.Random(seed).sample(values, n)
        duplicates = duplication_stats(base)
        for order, data in build_orders(base, seed).items():
            for name, sort_fn in ALGORITHMS.items():
                runtime, stats, _ = run_algorithm(sort_fn, data)
                rows.append({
                    "order": order,
                    "algorithm": name,
                    **stats,
                    "median_runtime_s": runtime,
                    "distinct_values": duplicates["distinct_values"],
                    "equal_pairs": duplicates["equal_pairs"],
                })
        return rows

    if experiment == "repeated values":
        n = sizes[0]
        for column, values in values_by_column.items():
            sample = random.Random(seed).sample(values, n)
            duplicates = duplication_stats(sample)
            for name, sort_fn in ALGORITHMS.items():
                runtime, stats, _ = run_algorithm(sort_fn, sample)
                rows.append({
                    "column": column,
                    "algorithm": name,
                    **stats,
                    "median_runtime_s": runtime,
                    "distinct_values": duplicates["distinct_values"],
                    "most_frequent_count": duplicates["most_frequent_count"],
                    "values_repeated": duplicates["values_repeated"],
                    "elements_in_repeats": duplicates["elements_in_repeats"],
                    "equal_pairs": duplicates["equal_pairs"],
                })
        return rows

    raise ValueError(f"Unknown experiment: {experiment}")


def _prompt_choice(prompt, choices, default, error_message):
    """Ask repeatedly until a listed choice or the displayed default is selected."""
    while True:
        answer = input(prompt).strip().lower()
        if not answer:
            return default
        if answer in choices:
            return choices[answer]
        print(error_message)


def _ask_experiment():
    print("Experiment:")
    print("  1) Scaling")
    print("  2) Input order")
    print("  3) Repeated values")
    return _prompt_choice(
        "Choose [1]: ",
        {"1": "scaling", "2": "input order", "3": "repeated values"},
        "scaling",
        "Please choose 1, 2, or 3.",
    )


def _ask_task():
    print("What would you like to do?")
    print("  1) Run an experiment [default]")
    print("  2) Record lookup (extension)")
    return _prompt_choice(
        "Choose [1]: ",
        {"1": "experiment", "2": "record lookup"},
        "experiment",
        "Please choose 1 or 2.",
    )


def _ask_sizes(experiment):
    if experiment == "scaling":
        print("Size:")
        print("  a) tiny 5, 10, 20")
        print("  b) crossover 50, 100")
        print("  c) scaling 250 to 4,000")
        print("  d) all ten 5 to 4,000")
        choices = {
            "a": TINY_SIZES,
            "b": CROSSOVER_SIZES,
            "c": LARGE_SIZES,
            "d": ALL_SCALING_SIZES,
        }
        return _prompt_choice(
            "Choose [c]: ",
            choices,
            LARGE_SIZES,
            "Please choose a, b, c, or d.",
        )

    print("Size: n = 1,000, 2,000 [default, the official size] or 4,000")
    choices = {
        key: (size,)
        for size in SAMPLE_SIZES
        for key in (str(size), f"{size:,}")
    }
    return _prompt_choice(
        "Choose [2,000]: ",
        choices,
        (config.ORDER_N,),
        "Please choose 1,000, 2,000, or 4,000.",
    )


def _ask_seed():
    while True:
        answer = input("Seed [42]: ").strip()
        if not answer:
            return config.SEED
        try:
            return int(answer)
        except ValueError:
            print("Please enter a whole number.")


def _column_choices():
    return {
        str(number): column
        for number, column in enumerate(NUMERIC_COLUMNS, start=1)
    } | {column: column for column in NUMERIC_COLUMNS}


def _print_numeric_columns():
    for number, column in enumerate(NUMERIC_COLUMNS, start=1):
        suffix = " [default]" if column == config.SCALING_COLUMN else ""
        print(f"  {number}) {column}{suffix}")


def _ask_column():
    print("Column:")
    _print_numeric_columns()
    return _prompt_choice(
        f"Choose [{config.SCALING_COLUMN}]: ",
        _column_choices(),
        config.SCALING_COLUMN,
        "Please choose one of the listed numeric columns.",
    )


def _ask_repeated_columns():
    print("Repeated-values columns:")
    print(f"  1) Brief columns: {', '.join(config.COLUMNS)} [default]")
    print("  2) Choose any 3 numeric columns")
    selection = _prompt_choice(
        "Choose [1]: ",
        {"1": "brief", "2": "custom"},
        "brief",
        "Please choose 1 or 2.",
    )
    if selection == "brief":
        return config.COLUMNS

    _print_numeric_columns()
    choices = _column_choices()
    while True:
        answer = input(
            "Choose 3 columns (comma-separated names or numbers): "
        ).strip().lower()
        tokens = [token.strip() for token in answer.split(",")]
        if (
            len(tokens) == 3
            and all(token in choices for token in tokens)
            and len({choices[token] for token in tokens}) == 3
        ):
            return tuple(choices[token] for token in tokens)
        print("Please enter exactly 3 different listed numeric columns.")


def _ask_missing_version(column, raw_values, missing):
    if column != "total_bedrooms":
        raise ValueError(
            f"Missing-value handling is only available for total_bedrooms; "
            f"{column} has {missing} missing values."
        )

    from src.missing_values import bedrooms_column

    raw_count = len(raw_values)
    total_rows = raw_count + missing
    ratio_count = len(bedrooms_column(config.DATA_PATH, "ratio")[0])
    median_count = len(bedrooms_column(config.DATA_PATH, "median")[0])
    percent = 100 * missing / total_rows if total_rows else 0

    print("Which version of the data?")
    print(f"  1) Raw data* ({raw_count:,} values) [default]")
    print(f"  2) With ratio imputation ({ratio_count:,} values)")
    print(
        f"  3) With a single median fill, for comparison "
        f"({median_count:,} values)"
    )
    print(
        f"* {column} has {missing:,} missing values "
        f"({percent:.1f}% of rows), left out of the raw data."
    )
    method = _prompt_choice(
        "Choose [1]: ",
        {"1": "skip", "2": "ratio", "3": "median"},
        "skip",
        "Please choose 1, 2, or 3.",
    )
    version_labels = {
        "skip": "raw data (blanks skipped)",
        "ratio": "ratio-imputed data",
        "median": "single median-filled data",
    }
    print(f"Selected total_bedrooms data version: {version_labels[method]}.")
    return bedrooms_column(config.DATA_PATH, method)[0]


def _load_selected_columns(columns):
    values_by_column = {}
    for column in columns:
        values, missing = load_column(config.DATA_PATH, column)
        if missing:
            values = _ask_missing_version(column, values, missing)
        values_by_column[column] = values
    return values_by_column


def _format_count(value):
    return f"{value:,}"


def _print_result_table(rows, group_field=None):
    groups = {}
    for row in rows:
        group = row[group_field] if group_field else None
        groups.setdefault(group, []).append(row)

    for group, group_rows in groups.items():
        if group is not None:
            print(f"  {str(group).replace('_', ' ').title()}:")
        first = group_rows[0]
        if first.get("equal_pairs", 0):
            print(
                f"  distinct values: {first['distinct_values']:,}; "
                f"equal_pairs: {first['equal_pairs']:,}"
            )
        print(
            "  Algorithm      Comparisons       Writes       Swaps       "
            "Passes   Runtime (ms)"
        )
        fastest_time = min(row["median_runtime_s"] for row in group_rows)
        for row in group_rows:
            marker = "*" if row["median_runtime_s"] == fastest_time else ""
            print(
                f"  {row['algorithm']:<12}"
                f"{_format_count(row['comparisons']):>13}"
                f"{_format_count(row['writes']):>12}"
                f"{_format_count(row['swaps']):>12}"
                f"{_format_count(row['passes']):>12}"
                f"{row['median_runtime_s'] * 1000:>14,.3f}{marker}"
            )
    print("* Fastest sort in its group")
    print("Counts are exact and repeatable; times depend on this computer.")


def _display_estimates(rows, target_n):
    factors = growth_factors(rows)
    print("Growth factors (runtime ratio / comparisons ratio / theory ratio):")
    for row in factors:
        print(
            f"  {row['algorithm']}: {row['n_from']:,} -> {row['n_to']:,}: "
            f"{_format_ratio(row['runtime_ratio'])} / "
            f"{_format_ratio(row['comparisons_ratio'])} / "
            f"{_format_ratio(row['theory_ratio'])}"
        )

    estimates = {}
    print(f"Estimated time for all {target_n:,} values:")
    for algorithm in ("bubble", "selection"):
        estimates[algorithm] = bubble_estimate(
            rows, target_n, algorithm=algorithm
        )[-1]["estimate_s"]
        print(f"  {algorithm}: {_format_duration(estimates[algorithm])}")
    return estimates


def _format_ratio(value):
    return "n/a" if value is None else f"{value:,.2f}x"


def _format_duration(seconds):
    if seconds >= 60:
        return f"{seconds / 60:,.1f} min"
    return f"{seconds:,.2f} s"


def _ask_yes_no(prompt, default=None):
    choices = {"y": True, "yes": True, "n": False, "no": False}
    default_label = "y" if default else "n"
    suffix = f" [{default_label}]" if default is not None else ""
    while True:
        answer = input(f"{prompt}{suffix}: ").strip().lower()
        if not answer and default is not None:
            return default
        if answer in choices:
            return choices[answer]
        print("Please answer y or n.")


def _run_full_column_check(values, estimates):
    actual_times = {}
    for name, sort_fn in ALGORITHMS.items():
        started = time.perf_counter()
        result, _ = sort_fn(values)
        elapsed = time.perf_counter() - started
        verify_sorted(result, values, name)
        actual_times[name] = elapsed

    fastest = min(actual_times, key=actual_times.get)
    print("Full-column check (one timed run per sort):")
    for algorithm in ALGORITHMS:
        estimate = estimates.get(algorithm)
        if estimate is None or estimate == 0:
            estimate_text, difference = "n/a", "n/a"
        else:
            estimate_text = _format_duration(estimate)
            difference = f"{(actual_times[algorithm] - estimate) / estimate * 100:+,.1f}%"
        marker = " * fastest" if algorithm == fastest else ""
        print(
            f"  {algorithm}: actual {_format_duration(actual_times[algorithm])}; "
            f"estimate {estimate_text}; difference {difference}{marker}"
        )


def _ask_lookup_rows():
    while True:
        answer = input(
            f"How many rows, 1 to {LOOKUP_MAX_ROWS} [{LOOKUP_DEFAULT_ROWS}]: "
        ).strip()
        if not answer:
            return LOOKUP_DEFAULT_ROWS
        if answer.isdigit() and 1 <= int(answer) <= LOOKUP_MAX_ROWS:
            return int(answer)
        print(f"Please enter a whole number from 1 to {LOOKUP_MAX_ROWS}.")


def _run_record_lookup():
    """Print the rows with the highest values in one column; writes no file."""
    column = _ask_column()
    k = _ask_lookup_rows()
    show = tuple(field for field in SHOW if field != column)
    results = find_top_records(config.DATA_PATH, column, k, show)

    print(
        f"Record lookup, top {len(results)} rows by {column} (exploration; "
        f"the official run uses {config.SCALING_COLUMN}, top "
        f"{LOOKUP_DEFAULT_ROWS})"
    )
    fields = ("csv_line", column, *show)
    widths = [
        max(len(field), *(len(str(row[field])) for row in results)) + 2
        for field in fields
    ]
    print("  " + "".join(f"{field:<{width}}" for field, width in zip(fields, widths)))
    for row in results:
        print(
            "  "
            + "".join(f"{str(row[field]):<{width}}" for field, width in zip(fields, widths))
        )
    print("csv_line is the line in housing.csv (the header is line 1).")
    print("Equal values are listed in file order; blank values are left out.")


def _run_one_exploration():
    if _ask_task() == "record lookup":
        _run_record_lookup()
        return
    experiment = _ask_experiment()
    sizes = _ask_sizes(experiment)
    seed = _ask_seed()
    columns = (
        (_ask_column(),)
        if experiment != "repeated values"
        else _ask_repeated_columns()
    )
    values_by_column = _load_selected_columns(columns)
    rows = _calculate_rows(experiment, sizes, seed, values_by_column)

    if experiment == "scaling":
        column = columns[0]
        print(
            f"Scaling, {column}, n = {', '.join(f'{n:,}' for n in sizes)}, "
            f"seed {seed} (exploration; the report uses "
            f"{config.SCALING_COLUMN}, seed {config.SEED})"
        )
        _print_result_table(rows, "n")
        if any(n >= 250 for n in sizes):
            estimates = _display_estimates(rows, len(values_by_column[column]))
            if _ask_yes_no(
                "Run all three sorts on the full column to check these "
                "estimates? (about 1.5 minutes) (y/n)",
                False,
            ):
                _run_full_column_check(values_by_column[column], estimates)
    elif experiment == "input order":
        column = columns[0]
        print(
            f"Input order, {column}, n = {sizes[0]:,}, seed {seed} "
            f"(exploration; the report uses "
            f"{config.SCALING_COLUMN}, seed {config.SEED})"
        )
        _print_result_table(rows, "order")
    else:
        for column in columns:
            column_rows = [row for row in rows if row["column"] == column]
            print(
                f"Repeated values, {column}, n = {sizes[0]:,}, seed {seed} "
                f"(exploration; the report uses the brief's three columns at "
                f"n = {config.ORDER_N:,}, seed {config.SEED}: "
                f"{', '.join(config.COLUMNS)})"
            )
            _print_result_table(column_rows)


def run_interactive():
    """Run the menu-driven exploration flow; it never writes to results/."""
    try:
        while True:
            _run_one_exploration()
            if not _ask_yes_no("Run another? (y/n)"):
                break
    except KeyboardInterrupt:
        print("\nGoodbye.")
        return
    print("Goodbye.")
