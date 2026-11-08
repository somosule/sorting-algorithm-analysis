# Titles for the results files

- **dataset_summary.csv**: Dataset profile of housing.csv (20,640 rows, 10 columns), before any sampling
- **scaling.csv**: Scaling experiment (4.2): median_income, one random sample per size (seed 42), n = 5 to 4,000; median of 5 runs; loop of 1,000 calls for n <= 20
- **full_size.csv**: Full dataset: all 20,640 median_income values in random order (seed 42); merge sort median of 5 runs; optional bubble check is a single run
- **growth_factors.csv**: Growth factors when n doubles (250 to 4,000), median_income, seed 42, compared with theory
- **bubble_estimate.csv**: Bubble and selection sort estimates for 20,640 values, from measured runtimes at n = 1,000, 2,000, 4,000
- **scaling_full_size_table.csv**: Full dataset (Q4): all 20,640 median_income values, seed 42; estimates from n = 1,000 to 4,000; merge median of 5 runs; bubble check a single run
- **input_order.csv**: Input-order experiment (4.3): one median_income sample, n = 2,000, seed 42, in four versions; median of 5 runs
- **repeated_values.csv**: Repeated-values experiment (4.4): median_income, housing_median_age, median_house_value, n = 2,000 each, seed 42, not reshuffled; median of 5 runs
- **memory.csv**: Peak memory per sort (tracemalloc), random median_income list, n = 2,000, measured separately from the timings
- **decision_guide_evidence.csv**: Decision-guide evidence, taken by code from the results files above
