"""Run the whole project with one command: python main.py"""
import time

from src import config
from src.data_profile import profile_dataset
from src.experiments import run_input_order, run_repeated_values, run_scaling
from src.growth_estimate import write_bubble_estimate, write_growth_factors


def main():
    if not config.DATA_PATH.exists():
        print(f"housing.csv not found at {config.DATA_PATH}. See README: Data.")
        return
    start = time.perf_counter()

    profile_dataset(config.DATA_PATH)
    run_scaling()
    run_input_order()
    run_repeated_values()
    write_growth_factors()
    write_bubble_estimate()

    try:
        from src.make_plots import make_plots
    except ImportError:
        print("matplotlib not installed: plots skipped.")
    else:
        make_plots()

    if config.RUN_RECORD_LOOKUP:
        from src.record_lookup import top_records
        top_records(config.DATA_PATH, config.SCALING_COLUMN)

    print(f"Done in {time.perf_counter() - start:.1f} s. Results in {config.RESULTS_DIR}")


if __name__ == "__main__":
    main()
