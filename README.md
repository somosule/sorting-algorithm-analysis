# Sorting Algorithm Analysis

DATA 5010 - Group Project 2 · Bowling Green State University · Fall 2026
Team: Henrietta, Patrick, Sarah

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
python main.py                      # dataset profile, all experiments, growth factors, estimate, plots
python -m unittest discover -v      # tests
```

A full run takes about _[to be measured]_ on _[computer, OS, Python version]_.

## Outputs

| File | Contents |
|---|---|
| `results/dataset_summary.csv` | Rows, missing values, distinct values, min and max for each selected column |
| `results/scaling.csv` | Section 4.2: runtime, comparisons, writes and swaps for each algorithm and sample size |
| `results/input_order.csv` | Section 4.3: the same measures for random, sorted, reverse and nearly sorted input |
| `results/repeated_values.csv` | Section 4.4: the same measures for each column, with duplication statistics |
| `results/growth_factors.csv` | Measured vs theoretical growth when n doubles |
| `results/bubble_estimate.csv` | Bubble sort runtime estimate for 20,640 values, with working |
| `results/plots/` | Charts used in the report |
| `results/tables/` | Summary tables used in the report |

### How to read the results

- `comparisons`, `writes` and `swaps` follow the counting rules below. They are identical on every computer and every run.
- `median_runtime_s` is the median of 5 timings in seconds. It varies between computers. For n of 20 or less it is the time per call from a loop of 1,000 calls (`loop_reps`).
- _[Column meanings for each file: to be completed]_

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
