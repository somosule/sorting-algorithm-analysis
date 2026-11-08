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

The experiments use three columns: `median_income` (scaling and input order), plus `housing_median_age` and `median_house_value` (repeated values). `total_bedrooms` has 207 blank values. It is left out of the main experiments and used only in the optional missing-values extension (`RUN_MISSING_VALUES` in `config.py`).

## Run

From the repository root:

```bash
# macOS
python3 main.py                     # full reproducible run; asks no questions
python3 main.py --all-extras        # the official run: also the three optional steps
python3 main.py --interactive       # exploratory menu; does not write to results/
python3 main.py --help              # lists every option
python3 -m unittest discover -v     # tests

# Windows
python main.py                      # full reproducible run; asks no questions
python main.py --all-extras         # the official run: also the three optional steps
python main.py --interactive        # exploratory menu; does not write to results/
python main.py --help               # lists every option
python -m unittest discover -v      # tests
```

The full run took **55.0 seconds** on **Windows 11**, with an **Intel64 Family 6 Model 198 Stepping 2** processor, using **Python 3.14.4**. Runtime varies by computer and load. The run records its exact date, time, Python version, and computer in `results/run_info.csv`.

The command runs the dataset profile, scaling, input-order and repeated-values experiments, growth factors, bubble estimate, full-size check, memory measurement, and plots, in that order. The full-size check normally measures merge sort; the optional bubble check runs once only when `RUN_BUBBLE_FULL` is enabled after the bubble estimate is saved. Each step reports its row or file count, output path, and elapsed time. The final lines give the paths to the combined chart PDF and report captions, followed by total run time. If matplotlib is not installed, plots are skipped with a message. The three optional steps are off by default. Switch them on with command-line options, with no need to edit any code:

| Option | Optional step |
|---|---|
| `--bubble-check` | Runs bubble sort once on all 20,640 values, after its estimate is saved, as a check of the estimate |
| `--missing-values` | Runs the `total_bedrooms` missing-values extension |
| `--record-lookup` | Runs the record lookup extension |
| `--all-extras` | All three; this is the official run used for the report |

Options can be combined, for example `python3 main.py --bubble-check --record-lookup`. The defaults are the switches `RUN_BUBBLE_FULL`, `RUN_MISSING_VALUES` and `RUN_RECORD_LOOKUP` in `src/config.py`. The run prints which optional steps are on and records them in `results/run_info.csv` (`extras_run`).

Use `python3 main.py --interactive` on macOS or `python main.py --interactive` on Windows for exploratory runs with selectable experiment sizes, columns, and seed. It reports results in the terminal only and leaves the official files in `results/` unchanged.

## Outputs

Every file is written by `main.py`, grouped below by the section of the brief it answers. Raw results sit in `results/`; report-ready tables (rounded, one column per sort) in `results/tables/`; charts in `results/plots/`, all of them also collected in `results/plots/all_charts.pdf`. `results/tables/captions.md` gives each results file its title. Each CSV has a header and only the columns listed.

### Dataset profile (Section 3)

| File | Columns / contents |
|---|---|
| `results/dataset_summary.csv` | `column`, `rows`, `missing`, `distinct`, `min`, `max`, `cap_count` |

### 4.2 Scaling

| File | Columns / contents |
|---|---|
| `results/scaling.csv` | `n`, `algorithm`, `comparisons`, `writes`, `swaps`, `passes`, `median_runtime_s`, `loop_reps` |
| `results/tables/scaling_runtime_table.csv` | `n`, `bubble_ms`, `selection_ms`, `merge_ms`, including the full-dataset row |
| `results/tables/scaling_comparisons_table.csv` | `n`, `bubble`, `selection`, `merge` comparisons |
| `results/tables/scaling_small_n_table.csv` | `n`, `bubble_us`, `selection_us`, `merge_us` for the very small sizes (Q5, decision guide) |
| `results/plots/scaling_runtime.png` | Median runtime against n, n = 250 to 4,000 |
| `results/plots/scaling_runtime_loglog.png` | Median runtime against n on log-log axes, all sizes plus the full dataset (crossover, Q5) |
| `results/plots/scaling_comparisons.png` | Comparisons against n |
| `results/plots/scaling_writes.png` | Writes against n |

### 4.2 step 3: growth factors (Q3)

| File | Columns / contents |
|---|---|
| `results/growth_factors.csv` | `algorithm`, `n_from`, `n_to`, `runtime_ratio`, `comparisons_ratio`, `theory_ratio` |
| `results/tables/scaling_growth_factors_table.csv` | `doubling`, measured runtime and comparisons ratios per sort, and the theoretical growth |

### 4.2 step 4: full dataset, 20,640 values (Q4)

| File | Columns / contents |
|---|---|
| `results/bubble_estimate.csv` | `algorithm`, `n`, `runtime_s`, `scale_factor`, `estimate_s`; bubble rows then selection rows, each ending with an average row (the working for the estimates) |
| `results/full_size.csv` | `algorithm`, `source`, `comparisons`, `writes`, `swaps`, `passes`, `runtime_s`, `runs`; merge sort (measured) and, with `--bubble-check`, the bubble check |
| `results/tables/scaling_full_size_table.csv` | `algorithm`, `estimate_s`, `actual_s`, `source`, `difference_pct`; estimates against the full-dataset runs |

### 4.3 Input order

| File | Columns / contents |
|---|---|
| `results/input_order.csv` | `order`, `algorithm`, `comparisons`, `writes`, `swaps`, `passes`, `median_runtime_s` |
| `results/tables/input_order_table.csv` | `order`, comparisons, writes, passes and runtime in ms for each sort |
| `results/plots/input_order_comparisons.png` | Comparisons by input order |
| `results/plots/input_order_runtime.png` | Median runtime by input order |

### 4.4 Repeated values

| File | Columns / contents |
|---|---|
| `results/repeated_values.csv` | `column`, `algorithm`, `comparisons`, `writes`, `swaps`, `passes`, `median_runtime_s`, `distinct_values`, `most_frequent_count`, `values_repeated`, `elements_in_repeats`, `equal_pairs` |
| `results/tables/repeated_values_table.csv` | `column`, duplication statistics, comparisons, swaps and runtimes per sort |
| `results/plots/repeated_values.png` | Median runtime by column |

### Decision guide

| File | Columns / contents |
|---|---|
| `results/tables/decision_guide_evidence.csv` | `situation`, `source`, `n`, `algorithm`, `comparisons`, `writes`, `passes`, `median_runtime_s`, `fastest`; the evidence for each row of the guide, taken by code from the files above |

### Extras

| File | Columns / contents |
|---|---|
| `results/memory.csv` | `algorithm`, `peak_kib`; peak memory per sort (Q16) |
| `results/top_records.csv` | `csv_line`, `median_income`, `population`, `households`, `ocean_proximity` (optional, `--record-lookup`) |
| `results/total_bedrooms_filled.csv` | `row_number`, `ocean_proximity`, `households`, `ratio_used`, `estimate` (optional, `--missing-values`) |
| `results/total_bedrooms_before_after.csv` | `version`, `values`, `missing`, `distinct`, `min`, `max`, `median`, `most_frequent_value`, `most_frequent_count`, `values_repeated` (optional, `--missing-values`) |
| `results/total_bedrooms_method_check.csv` | `method`, `median_abs_pct_error`, `share_within_10pct` (optional, `--missing-values`) |

### Run details

| File | Columns / contents |
|---|---|
| `results/run_info.csv` | `setting`, `value`: seed, runs per timing, sizes, columns, optional steps run, Python version, computer, date and time |
| `results/tables/captions.md` | The title of every results file, built from `src/config.py` |
| `results/plots/all_charts.pdf` | Every chart, one per page |

### How to read the results

- `comparisons`, `writes` and `swaps` follow the counting rules below. They are identical on every computer and every run.
- `median_runtime_s` is the median of 5 timings in seconds. It varies between computers. For n of 20 or less it is the time per call from a loop of 1,000 calls (`loop_reps`).
- `run_info.csv` holds the fixed settings used for the run: seed, runs per timing, small-n loop size, sample size, scaling column and sizes, repeated-values columns, and which optional steps were run. It also records the Python version, computer, date and time, and that `measure.py` checks counts for consistency across repeats (raising an error if they differ).

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
  experiments.py     experiments, with optional full-size bubble check
  data_profile.py    dataset inspection and duplication statistics
  growth_estimate.py growth factors and bubble sort estimate
  interactive.py     non-persistent exploratory menu
  make_plots.py      tables and plots
  missing_values.py  optional total_bedrooms missing-values extension
  record_lookup.py   optional: look up original records after sorting
tests/
  test_data_profile.py    dataset profile tests
  test_interactive.py     exploratory menu tests
  test_load_data.py       data-loading tests
  test_main_options.py    command-line option tests
  test_missing_values.py  optional missing-values tests
  test_record_lookup.py   optional record-lookup tests
  test_run_info.py        run metadata tests
  test_sorts.py           correctness tests
  test_structure.py       checks banned libraries, sorted() use, settings, files
results/             generated outputs (committed)
docs/                checklist, decisions and notes for the report
```
