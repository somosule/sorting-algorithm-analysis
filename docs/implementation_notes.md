# Implementation notes

Report Section 2 reference: implementation details, design flow, and reproducibility.

## Tools and environment

- The algorithms, CSV input, experiments, command-line interface, and tests use the Python standard library. The project requires Python 3.10 or newer. The recorded official run used Python 3.14.7 on macOS 26.3.1 (Apple silicon, arm); `results/run_info.csv` records the run's exact Python version, platform, processor, date/time, settings, and optional steps.
- The test suite uses `unittest`. `matplotlib` is optional for plots and report-ready tables; `openpyxl` is optional for the workbook. Without either package, its outputs are skipped with a message, while the core CSV experiments still run.
- No Excel application is needed to run the project. Python generates `results/results_workbook.xlsx` from the result files; it can also be rebuilt alone with `python -m src.make_workbook`.

## Input preparation

- `src/load_data.py` reads `housing.csv` with `csv.DictReader`. Selected numeric values are converted to `float`; blank or non-numeric entries are counted as missing and skipped. The main experiments use `median_income`, `housing_median_age`, and `median_house_value`. `total_bedrooms` has 207 missing values and is excluded from the main experiments.
- `src/config.py` sets seed 42. Scaling samples use `random.Random(seed).sample` at n = 5, 10, 20, 50, 100, 250, 500, 1,000, 2,000, and 4,000. Input-order and repeated-values experiments use n = 2,000. Algorithms being compared receive the same input; each sort copies it and leaves the original unchanged.
- The four input orders are made from the same reproducible `median_income` sample: random (a seeded shuffle), sorted (the project's merge sort), reverse (the sorted sample reversed), and nearly sorted (floor of 1% of n seeded random swaps in the sorted sample).
- Repeated-values runs use reproducible samples of the same size and seed from each of the three experiment columns. Duplication statistics are recorded with each sort's results.

## Counting rules

- A comparison is a comparison between two data values, whether the condition is true or false. Loop, index, and length checks are not comparisons.
- A write is a value stored in a list position. A swap is reported separately and counts as two writes. The initial input copy and merge-sort slicing copies are not counted.
- Bubble sort uses `>` on adjacent values, shortens each pass, stops after a pass with no swaps, and counts that final pass. Selection sort uses `<`, counts every outer-loop pass, and swaps only when the minimum is not already in place. Merge sort is top-down and recursive, takes the left value first on equality with `<=`, and reports zero swaps.
- Every value placed into a merge output, including leftovers, counts as one write. There is no separate copy-back step. Passes are an additional measure: bubble counts every pass including its final no-swap pass; selection counts each outer-loop iteration; merge reports zero. The additional counting choices are recorded in [decisions.md](./decisions.md) (D06 and D09).

## Timing and correctness checks

- `src/measure.py` times sort calls with `time.perf_counter()`. Loading and correctness checks are outside the timed interval. The sort's initial input copy is inside the timed call but is not counted as a write.
- Each input is run five times and the median duration is reported. For n <= 20, each timed interval loops over 1,000 calls and reports the average time per call. Operation counts must match across repeats or the run raises an error.
- Outside the timer, each result is compared with `sorted(original)`, and the original input is checked for mutation. `sorted()` is used for verification only, not by the sorting algorithms.
- The automated suite has 76 tests, run with `python -m unittest discover -v`. It covers sorting, data loading and profiling, experiment structure, workbook generation, command-line options, run metadata, and interactive and optional-extension behavior.

## `main.py` call order and outputs

The default `python main.py` run is non-interactive. It profiles the dataset; runs scaling, input-order, and repeated-values experiments; calculates growth factors; writes the bubble-sort estimate; runs the full-size check; measures memory; and generates plots and tables if `matplotlib` is installed. It then runs enabled missing-values and record-lookup extensions, writes run metadata, and builds the workbook if `openpyxl` is installed. Each step reports its elapsed time and output rows or files.

The full-size step sorts all 20,640 `median_income` values with merge sort. The optional full-size bubble-sort check runs only after the estimate. The workbook is the last generated result and is built from the finished CSVs, plots, captions, and run metadata. Extension sheets appear only for optional steps recorded as run in `run_info.csv`.

| Stage or function | File | Purpose |
|---|---|---|
| `main()` | `main.py` | Parses options and coordinates the full run. |
| `profile_dataset()` | `src/data_profile.py` | Reports row, missing, distinct, and range statistics for selected columns. |
| `run_scaling()`, `run_input_order()`, `run_repeated_values()` | `src/experiments.py` | Prepare shared inputs, run all algorithms, and write experiment CSVs. |
| `run_algorithm()` | `src/measure.py` | Times repeated sort calls, verifies results and unchanged inputs, and checks count consistency. |
| `bubble_sort()`, `selection_sort()`, `merge_sort()` | `src/sorts.py` | Implement and count the three algorithms. |
| `write_growth_factors()`, `write_bubble_estimate()` | `src/growth_estimate.py` | Derive growth ratios and extrapolate quadratic-sort runtimes from scaling results. |
| `run_full_size()`, `run_memory()` | `src/experiments.py` | Check merge sort on the complete column, optionally check bubble sort, and measure peak memory. |
| `make_plots()` | `src/make_plots.py` | Generate chart images, a combined PDF, evidence tables, and captions from results. |
| `_write_run_info()` | `main.py` | Records settings and execution environment in `results/run_info.csv`. |
| `make_workbook()` | `src/make_workbook.py` | Collates run information, question evidence, titled tables, charts, and raw results into the workbook. |

### Command-line and interactive mode

- `python main.py` runs the analysis with the default optional steps off. `python main.py --help` lists the options.
- `--bubble-check` runs bubble sort once on all values after its estimate; `--missing-values` runs the missing-data extension; `--record-lookup` runs the record lookup extension. These options can be combined. `--all-extras` enables all three and is the official report run. Enabled optional steps are listed at startup and recorded in `results/run_info.csv`.
- `python main.py --interactive` starts the exploratory menu instead of the full pipeline. Its first question is whether to run an experiment (the default) or a record lookup, which asks for any numeric column and the number of rows (1 to 20, default 5) and prints the top records. The experiments offered are scaling, input-order, or repeated-values experiments; preset sizes; a selectable seed; and one or three numeric columns as appropriate. Pressing Enter selects the displayed defaults. It prints counts and timings to the terminal and does not change the official result files.
- For larger interactive scaling choices, it also shows growth estimates and asks, defaulting to No, whether to run all three sorts on the full column as an estimate check. If `total_bedrooms` is selected, it offers raw values, ratio imputation, or a single median fill.
- `python -m src.make_workbook` rebuilds only the workbook from current result files. `python -m unittest discover -v` runs the tests.

## Workbook

`results/results_workbook.xlsx` is generated by `src/make_workbook.py` as the final pipeline step. It has a linked contents sheet, a Questions sheet mapping the brief's questions to key numbers and evidence, section sheets with titled tables and matching charts, and raw result tables. Inputs from optional steps are included only when that step was run, based on `run_info.csv`. The workbook is an output for browsing and report preparation, not an input to the experiments. `openpyxl` is required; if it is unavailable, the run skips the workbook with an installation hint.

## Known limitations

- Runtime and memory measurements depend on the computer and its current load; they will vary between machines. Counts and seeded samples are reproducible, but timings are not.
- The experiments sort one numeric column at a time, not complete housing records. Record lookup is a separate optional extension.
- Bubble and selection sort have quadratic growth. The full-size bubble check is optional because it can take a long time; the reported estimate is extrapolated from smaller inputs rather than measured on the full dataset.
- The interactive full-column check is a single timing per algorithm, unlike the five-repeat medians in the standard experiments. Interactive results are exploratory and are not saved to the official result files.
- The main experiments skip missing `total_bedrooms` values; optional imputation is a separate what-if analysis and does not modify `housing.csv`.
