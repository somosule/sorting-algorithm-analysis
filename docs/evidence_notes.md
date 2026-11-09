# Evidence notes

For each question: the answer in 2-4 sentences, the exact numbers, and the table or plot that shows them. Sarah writes the final report answers from these notes.

## Scaling (4.2)

**Q1. Sample sizes and seed; why very small sizes are included.**

We timed all three sorts on one random sample of median_income at each of ten sizes, using the same sample for every sort so the comparison is fair. The seed is fixed at 42, so the same samples are drawn on every run and computer. The tiny sizes give evidence for the decision guide's very small list row, the crossover sizes show where merge sort overtakes the O(n²) sorts, and the larger sizes are used for the growth factors and the bubble estimate.

Numbers: seed 42; tiny n = 5, 10, 20; crossover n = 50, 100; scaling n = 250, 500, 1,000, 2,000, 4,000. Samples drawn with random.Random(42).sample().

Evidence: results/run_info.csv, results/scaling.csv; workbook 4.2 Scaling sheet.

**Q2. Runtime, comparisons and writes for each algorithm and size; counts identical across repeats?**

Bubble and selection sort compare almost every pair of values, about n(n - 1)/2 comparisons, while merge sort compares far fewer because it only compares values while merging sorted halves. Their writes differ because bubble sort writes on every swap, selection sort makes at most one swap per pass, and merge sort writes each value once per merge level. The counts were identical in all five repeats, which measure.py checks on every run.

Numbers: n = 4,000 comparisons: bubble 7,997,010, selection 7,998,000, merge 42,817. Writes: bubble 8,006,726, selection 7,964, merge 47,904. Median runtime: bubble 847 ms, selection 352 ms, merge 6.28 ms. Each timing is the median of 5 runs; n ≤ 20 timed as a loop of 1,000 calls.

Evidence: results/scaling.csv, tables/scaling_runtime_table.csv, tables/scaling_comparisons_table.csv, plots scaling_runtime.png, scaling_comparisons.png, scaling_writes.png; workbook 4.2 Scaling and Run info sheets.

**Q3. Observed runtime growth factor when n doubles vs theory (about 4x for O(n²), a little over 2x for O(n log n)); why they differ.**

The comparison ratio matches theory exactly only for selection sort, because it always makes n(n - 1)/2 comparisons whatever the order of the data. Bubble and merge sort's comparison counts also depend on the order of each sample, and each size uses a different sample, so their ratios move slightly around theory (bubble 3.97 to 4.04, merge 2.21 to 2.30). The runtime ratios vary more, because runtime also includes Python overhead, memory and cache effects, and timer noise, which the median of five runs reduces but does not remove.

Numbers: doubling n from 250 to 4,000, runtime ratios: bubble 3.90 to 4.22, selection 4.00 to 4.15 (theory 4.00), merge 2.16 to 2.23 (theory 2.18 to 2.25). Comparison ratios: bubble 3.97 to 4.04, selection 4.00 to 4.01, merge 2.21 to 2.30.

Evidence: tables/scaling_growth_factors_table.csv, plot scaling_runtime_loglog.png; workbook 4.2 Growth (Q3) sheet.

**Q4. Bubble sort estimate for 20,640 values: calculation, assumptions, why approximate (and the actual time, if the optional check was run).**

Bubble sort's runtime grows with n², so each measured time is scaled by (20,640 / n)² and the three estimates are averaged. The estimate assumes quadratic growth up to 20,640 values, that the full column behaves like the samples, the same computer and conditions, and that early termination barely helps on random data. It is approximate because larger lists can run slightly slower per step due to memory and cache effects, and timings vary between runs; the full run came within 3.3% of the estimate.

Numbers: n = 1,000: 0.0506 s × 426.0 = 21.6 s; n = 2,000: 0.210 s × 106.5 = 22.3 s; n = 4,000: 0.847 s × 26.6 = 22.5 s; average 22.1 s. Actual bubble run on all 20,640 values: 22.9 s (+3.3%). Selection estimate 9.35 s; merge measured 0.0387 s.

Evidence: results/bubble_estimate.csv, tables/scaling_full_size_table.csv; workbook 4.2 Full data (Q4) sheet.

**Q5. Input size at which merge sort's advantage becomes apparent; why the difference is less visible for very small inputs.**

 Merge sort overtakes bubble sort between n = 10 and 20 and selection sort between n = 20 and 50, and is the fastest sort at every size from n = 50. After that its advantage roughly doubles each time n doubles. For very small lists, merge sort's fixed costs (recursive calls, slicing and creating new lists) outweigh the sorting work, and n² and n log n are close when n is small. Timings of a few microseconds are also more affected by noise.

Numbers: n = 10: bubble 4.14 µs, selection 3.53 µs, merge 5.34 µs. n = 20: bubble 17.5 µs, selection 10.8 µs, merge 12.7 µs. n = 50: bubble 132 µs, selection 73.5 µs, merge 42.5 µs. Bubble takes 11 times as long as merge at n = 250 and 135 times as long at n = 4,000.

Evidence: tables/scaling_small_n_table.csv, tables/scaling_runtime_table.csv, plot scaling_runtime_loglog.png; workbook 4.2 Scaling sheet.


## Input order (4.3)
**Q6. Why bubble sort on already sorted data makes about n - 1 comparisons and no swaps.**

**Q7. Why selection sort makes about n(n - 1)/2 comparisons even when the input is already sorted.**

**Q8. Why merge sort's comparison count changes less with input order than bubble sort's.**

**Q9. Best-performing algorithm for each input order, justified in 2-3 sentences.**

**Q10. Bubble sort's worst-case arrangement among the four inputs, and why.**

**Q11. Does early termination help much on nearly sorted input? Why a few out-of-place elements can still force many passes.**

## Repeated values (4.4)
**Q12. Comparisons, writes and runtimes across the three columns; which observations come from duplication and which from input order or implementation.**

## Decision guide (4.5)

| Situation | Best algorithm | Evidence from our results | Why |
|---|---|---|---|
| Large random input | | | |
| Very small list (n < 20) | | | |
| Already sorted input | | | |
| Nearly sorted input | | | |
| Reverse-sorted input | | | |
| Many repeated values | | | |

## Reflection (4.6)
**Q13. Bubble and selection sort are both O(n²). Why can they behave differently on sorted input?**

**Q14. One realistic reason someone might still choose selection or bubble sort.**

**Q15. At least two reasons the measured slowdown when doubling n is not exactly 4x or 2x.**

**Q16. How merge sort's additional memory requirement affects the choice of algorithm.**

**Q17. Why the same input and a consistent measurement method matter when comparing algorithms.**
