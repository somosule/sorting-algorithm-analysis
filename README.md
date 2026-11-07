# Sorting Algorithm Analysis

**DATA 5010 - Group Project 2** · Bowling Green State University · Fall 2026

**Team:** Henrietta, Patrick, Sarah

We implement bubble sort, selection sort and merge sort from scratch in Python, count their comparisons and writes, time them, and compare them across input sizes, input orders and columns with different amounts of duplication. The results support a decision guide recommending an algorithm for each situation.

## Requirements

- Python 3.10 or newer, standard library only for loading data and the algorithms.
- matplotlib (optional) for plots: `pip install matplotlib`. Without it, every results CSV is still produced and plots are skipped.

## Data

`housing.csv` (California Housing Prices, 20,640 rows, 10 columns) is included in the repository root, next to `main.py`, as the brief requires.

If it is missing, download it from:
https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv

Note the hyphen in `handson-ml2`; the link often loses it when copied from the PDF. Save the file as `housing.csv` in the repository root without opening and re-saving it in Excel.

The experiments use three columns: `median_income` (scaling and input order), plus `housing_median_age` and `median_house_value` (repeated values). `total_bedrooms` contains blank values and is not used.

## Run

From the repository root:

```bash
python main.py                      # full reproducible run; asks no questions
python -m unittest discover -v      # tests
```

The full run took **55.0 seconds** on **Windows 11**, with an **Intel64 Family 6 Model 198 Stepping 2** processor, using **Python 3.14.4**. Runtime varies by computer and load. The run records its exact date, time, Python version, and computer in `results/run_info.csv`.

The command runs the dataset profile, scaling, input-order and repeated-values experiments, growth factors, bubble estimate, full-size check, memory measurement, and plots—in that order. Each step reports its row or file count, output path, and elapsed time. The final lines give the paths to the combined chart PDF and report captions, followed by total run time. If matplotlib is not installed, plots are skipped with a message. The optional `RUN_MISSING_VALUES` and `RUN_RECORD_LOOKUP` extensions are disabled by default.

## Outputs

Each generated CSV has a header and only the columns listed below.

| File | Columns / contents |
|---|---|
| `results/dataset_summary.csv` | `column`, `rows`, `missing`, `distinct`, `min`, `max`, `cap_count` |
| `results/scaling.csv` | `n`, `algorithm`, `comparisons`, `writes`, `swaps`, `passes`, `median_runtime_s`, `loop_reps` |
| `results/input_order.csv` | `order`, `algorithm`, `comparisons`, `writes`, `swaps`, `passes`, `median_runtime_s` |
| `results/repeated_values.csv` | `column`, `algorithm`, `comparisons`, `writes`, `swaps`, `passes`, `median_runtime_s`, `distinct_values`, `most_frequent_count`, `values_repeated`, `elements_in_repeats`, `equal_pairs` |
| `results/growth_factors.csv` | `algorithm`, `n_from`, `n_to`, `runtime_ratio`, `comparisons_ratio`, `theory_ratio` |
| `results/bubble_estimate.csv` | `n`, `runtime_s`, `scale_factor`, `estimate_s`; the final row averages the estimates |
| `results/full_size.csv` | `algorithm`, `source`, `comparisons`, `writes`, `swaps`, `passes`, `runtime_s`, `runs` |
| `results/memory.csv` | `algorithm`, `peak_kib` |
| `results/run_info.csv` | `setting`, `value`; fixed settings and run environment |
| `results/plots/` | `all_charts.pdf` and PNG charts for scaling runtimes, comparisons and writes, input-order comparisons and runtimes, and repeated values |
| `results/tables/captions.md` | Captions for the report's results files |
| `results/tables/scaling_runtime_table.csv` | `n`, `bubble_ms`, `selection_ms`, `merge_ms` |
| `results/tables/scaling_comparisons_table.csv` | `n`, `bubble`, `selection`, `merge` comparisons |
| `results/tables/small_n_table.csv` | `n`, `bubble_us`, `selection_us`, `merge_us` |
| `results/tables/input_order_table.csv` | `order`, comparisons, writes, passes and runtime in ms for each algorithm |
| `results/tables/repeated_values_table.csv` | `column`, duplication statistics, sort comparisons, swaps and runtimes |
| `results/tables/growth_factors_table.csv` | `doubling`, measured runtimes and comparisons, and theoretical growth |
| `results/tables/decision_guide_evidence.csv` | `situation`, `source`, `n`, `algorithm`, `comparisons`, `writes`, `passes`, `median_runtime_s`, `fastest` |

### How to read the results

- `comparisons`, `writes` and `swaps` follow the counting rules below. They are identical on every computer and every run.
- `median_runtime_s` is the median of 5 timings in seconds. It varies between computers. For n of 20 or less it is the time per call from a loop of 1,000 calls (`loop_reps`).
- `run_info.csv` holds the fixed settings used for the run: seed, runs per timing, small-n loop size, sample size, and scaling column. It also records the Python version, computer, date and time, and that `measure.py` checks counts for consistency across repeats (raising an error if they differ).

## Method summary

- **Counting (brief Section 4.1).** A comparison is two data values compared; loop and index checks are not counted. A write is a value stored into a list position; a swap is 2 writes. In merge sort, each value placed into the merged output is 1 write. Slicing copies and the initial copy of the input are not counted.
- **Algorithms.** Bubble sort stops after a full pass with no swaps. Selection sort swaps only when the minimum is out of place. Merge sort takes the left value first when values are equal (`<=`).
- **Timing.** `time.perf_counter()` around the sort call only; data loading is excluded. Every output is checked against `sorted()` and the input is checked unchanged.
- **Reproducibility.** Seed 42 and all sample sizes are set in `src/config.py`.

## Repository layout

```
README.md            this file
CONTRIBUTING.md      team rules: branches, reviews, code rules
main.py              runs everything
housing.csv          dataset
src/
  config.py          shared settings (seed, sizes, paths)
  load_data.py       reads housing.csv with the csv module
  sorts.py           bubble, selection and merge sort with counters
  measure.py         timing and output verification
  experiments.py     scaling, input-order and repeated-values experiments
  data_profile.py    dataset inspection and duplication statistics
  growth_estimate.py growth factors and bubble sort estimate
  make_plots.py      tables and plots
  record_lookup.py   optional: look up original records after sorting
tests/
  test_sorts.py      correctness tests
  test_structure.py  checks banned libraries, sorted() use, settings, files
results/             generated outputs (committed)
docs/                checklist, decisions and notes for the report
```
