## Scaling (4.2)
**Q1. Sample sizes and seed; why very small sizes are included.**

We used ten sample sizes of median_income. Each sample was drawn once with random.Random(42).sample(), using seed 42, and the same sample was given to all three sorts. The sizes are in three groups. The tiny sizes (5, 10 and 20) are for the very small list row of the decision guide. The crossover sizes (50 and 100) show where merge sort overtakes the other two sorts (D19). The scaling sizes (250, 500, 1,000, 2,000 and 4,000) are used for the growth factors and the bubble sort estimate.

Source: results/run_info.csv, results/scaling.csv

**Q2. Runtime, comparisons and writes for each algorithm and size; counts identical across repeats?**

Bubble and selection sort both make about n(n − 1)/2 comparisons. At n = 4,000, bubble made 7,997,010 comparisons, selection made 7,998,000 and merge made 42,817, which is about 187 times fewer. Writes were very different: at n = 4,000, bubble made 8,006,726, selection 7,964 and merge 47,904. The median runtimes at n = 4,000 were 847 ms for bubble, 352 ms for selection and 6.28 ms for merge. The counts were the same in all five repeats, and measure.py stops the run with an error if they are not.

Source: results/scaling.csv, tables/scaling_runtime_table.csv, tables/scaling_comparisons_table.csv, plots scaling_runtime.png, scaling_comparisons.png and scaling_writes.png

**Q3. Observed runtime growth factor when n doubles vs theory (about 4x for O(n²), a little over 2x for O(n log n)); why they differ.**

When n doubles, the comparison ratios are very close to theory. Bubble was between 3.97 and 4.04 and selection between 4.00 and 4.01, against a theoretical 4.00. Merge was between 2.21 and 2.30, against a theoretical 2.18 to 2.25. The runtime ratios were also close but varied more: bubble 3.90 to 4.22, selection 4.00 to 4.15 and merge 2.16 to 2.23. Comparisons are exact counts, so they follow the theory. Runtimes also depend on Python's overhead, memory and cache effects and timer noise, which the median of five runs reduces but does not remove, and each size uses a different random sample.

Source: tables/scaling_growth_factors_table.csv, plot scaling_runtime_loglog.png

**Q4. Bubble sort estimate for 20,640 values: calculation, assumptions, why approximate (and the actual time, if the optional check was run).**

The estimate is the measured time at size n multiplied by (20,640 / n)². From n = 1,000 the estimate was 21.6 s, from n = 2,000 it was 22.3 s and from n = 4,000 it was 22.5 s, giving an average of 22.1 s. One full run of bubble sort on all 20,640 values took 22.9 s, which is 3.3% above the estimate. The estimate assumes that the time grows with n², that the full column behaves like the samples, that the same computer is used under the same conditions, and that early termination makes little difference on random data. It is only approximate because larger lists can be slightly slower per step due to memory and caching, and timings change a little from run to run. Selection sort was estimated at 9.35 s, and merge sort took 0.0387 s on all 20,640 values, about 590 times faster than bubble sort.

Source: results/bubble_estimate.csv, tables/scaling_full_size_table.csv

**Q5. Input size at which merge sort's advantage becomes apparent; why the difference is less visible for very small inputs.**

Merge sort becomes faster than bubble sort between n = 10 and n = 20. At n = 10, bubble took 4.14 µs and merge 5.34 µs, and at n = 20 bubble took 17.5 µs and merge 12.7 µs. Merge sort becomes faster than selection sort between n = 20 and n = 50. At n = 20, selection took 10.8 µs and merge 12.7 µs, and at n = 50 selection took 73.5 µs and merge 42.5 µs. After this the difference grows quickly: bubble sort takes 11 times as long as merge sort at n = 250 and 135 times as long at n = 4,000. For very small lists, merge sort's extra work, such as recursive calls, slicing and creating new lists, takes longer than the sorting itself. Also, n² and n log n are close when n is small, and timings of a few microseconds are affected more by noise.

Source: tables/scaling_small_n_table.csv, tables/scaling_runtime_table.csv, plot scaling_runtime_loglog.png