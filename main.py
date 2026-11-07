"""Run the complete, reproducible project analysis with ``python main.py``."""
import csv
import platform
import time
from datetime import datetime

from src import config
from src.data_profile import profile_dataset
from src.experiments import (
    run_full_size,
    run_input_order,
    run_memory,
    run_repeated_values,
    run_scaling,
)
from src.growth_estimate import write_bubble_estimate, write_growth_factors


def _relative_path(path):
    """Return a repo-root-relative path suitable for terminal links."""
    return path.relative_to(config.ROOT).as_posix()


def _csv_row_count(path):
    """Count data rows in a results CSV, excluding its header."""
    with open(path, newline="", encoding="utf-8") as file:
        return sum(1 for _ in csv.DictReader(file))


def _report_step(label, action, output_paths):
    """Time one step and report the rows and repo-relative output paths."""
    started = time.perf_counter()
    result = action()
    elapsed = time.perf_counter() - started

    paths = [config.ROOT / path for path in output_paths]
    if len(paths) == 1 and paths[0].is_file():
        count = _csv_row_count(paths[0])
        output = f"{count:,} rows -> {_relative_path(paths[0])}"
    else:
        existing_files = [
            file
            for path in paths
            for file in (path.rglob("*") if path.is_dir() else [path])
            if file.is_file()
        ]
        output = (
            f"{len(existing_files):,} files -> "
            + ", ".join(_relative_path(path) for path in paths)
        )
    print(f"{label}: {output} ({elapsed:.1f} s)")
    return result


def _write_run_info():
    """Write the fixed settings and execution environment for this run."""
    processor = platform.processor()
    computer = platform.platform()
    if processor:
        computer = f"{computer}; processor: {processor}"

    settings = (
        ("seed", config.SEED),
        ("runs_per_timing", config.REPEATS),
        ("small_n_loop_size", config.SMALL_LOOP),
        ("sample_size", config.ORDER_N),
        ("scaling_column", config.SCALING_COLUMN),
        ("python_version", platform.python_version()),
        ("computer", computer),
        ("date_time", datetime.now().astimezone().isoformat(timespec="seconds")),
        (
            "counts_identical_across_repeats",
            "checked by measure.py; every run raises an error if counts differ",
        ),
    )

    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = config.RESULTS_DIR / "run_info.csv"
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("setting", "value"))
        writer.writerows(settings)
    return path


def main():
    if not config.DATA_PATH.exists():
        print(f"housing.csv not found at {config.DATA_PATH}. See README: Data.")
        return

    started = time.perf_counter()
    _report_step(
        "Dataset profile",
        lambda: profile_dataset(config.DATA_PATH),
        ["results/dataset_summary.csv"],
    )
    _report_step("Scaling", run_scaling, ["results/scaling.csv"])
    _report_step("Input order", run_input_order, ["results/input_order.csv"])
    _report_step(
        "Repeated values",
        run_repeated_values,
        ["results/repeated_values.csv"],
    )
    _report_step(
        "Growth factors",
        write_growth_factors,
        ["results/growth_factors.csv"],
    )
    _report_step(
        "Bubble estimate",
        write_bubble_estimate,
        ["results/bubble_estimate.csv"],
    )
    _report_step("Full size", run_full_size, ["results/full_size.csv"])
    _report_step("Memory", run_memory, ["results/memory.csv"])

    try:
        from src.make_plots import make_plots
    except ImportError:
        print("matplotlib not installed: plots skipped.")
    else:
        _report_step(
            "Plots",
            make_plots,
            ["results/plots", "results/tables"],
        )

    if config.RUN_MISSING_VALUES:
        from src.missing_values import estimate_missing_bedrooms

        _report_step(
            "Missing values",
            lambda: estimate_missing_bedrooms(config.DATA_PATH),
            [
                "results/total_bedrooms_filled.csv",
                "results/total_bedrooms_before_after.csv",
                "results/total_bedrooms_method_check.csv",
            ],
        )

    if config.RUN_RECORD_LOOKUP:
        from src.record_lookup import top_records

        _report_step(
            "Record lookup",
            lambda: top_records(config.DATA_PATH, config.SCALING_COLUMN),
            ["results/top_records.csv"],
        )

    _report_step("Run info", _write_run_info, ["results/run_info.csv"])
    print(f"Charts: {_relative_path(config.PLOTS_DIR / 'all_charts.pdf')}")
    print(f"Captions: {_relative_path(config.TABLES_DIR / 'captions.md')}")
    print(f"Done in {time.perf_counter() - started:.1f} s")


if __name__ == "__main__":
    main()
