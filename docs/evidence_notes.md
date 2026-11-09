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

On already sorted data, bubble sort's first pass compares each adjacent pair once, which is n - 1 comparisons. No pair is out of order, so nothing is swapped, and early termination stops the sort after that one pass. On random data it needs almost n(n - 1)/2 comparisons and nearly n passes.

Numbers: n = 2,000 sorted: 1,999 comparisons, 0 swaps, 0 writes, 1 pass, 0.103 ms (random: 1,998,594 comparisons, 1,971 passes, 210 ms).

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

**Q7. Why selection sort makes about n(n - 1)/2 comparisons even when the input is already sorted.**

Selection sort finds the smallest remaining value by scanning the whole unsorted part on every pass, and it has no way to stop early, even when the data is already in order. The number of comparisons is therefore n(n - 1)/2 for every input order. Sorted input only saves writes, because selection sort swaps only when the smallest value is not already in place.

Numbers: n = 2,000 sorted: 1,999,000 comparisons (2,000 × 1,999 / 2), 0 writes, 1,999 passes, 87.6 ms. Random, reverse and nearly sorted also make 1,999,000 comparisons (87.4 to 92.4 ms).

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

**Q8. Why merge sort's comparison count changes less with input order than bubble sort's.**

Merge sort always splits the list in half and merges the halves back together, so it does the same number of merge levels whatever the input order. Order only changes how many comparisons each merge needs: when one half runs out early, as with sorted or reverse input, the rest of the other half is copied without comparing. Bubble sort's work depends directly on how many pairs are out of order, so it ranges from n - 1 comparisons to n(n - 1)/2.

Numbers: n = 2,000 merge comparisons: sorted 10,864, reverse 11,202, nearly sorted 14,370, random 19,419 (less than 2 times apart); merge writes 21,952 for every order. Bubble comparisons: 1,999 (sorted) to 1,999,000 (reverse), about 1,000 times apart.

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

**Q9. Best-performing algorithm for each input order, justified in 2-3 sentences.**

Random: merge sort is fastest because it does far fewer comparisons than the O(n²) sorts. Sorted: bubble sort is fastest because one pass with no swaps confirms the order and early termination stops it. Nearly sorted and reverse: merge sort is fastest; bubble sort still needs many passes, and selection sort always makes n(n - 1)/2 comparisons.

Numbers: n = 2,000 median runtime (bubble / selection / merge): random 210 / 87.9 / 2.88 ms; sorted 0.103 / 87.6 / 2.32 ms; nearly sorted 98.0 / 87.4 / 2.49 ms; reverse 290 / 92.4 / 2.32 ms.

Evidence: results/input_order.csv, tables/input_order_table.csv, tables/decision_guide_evidence.csv; workbook 4.3 Input order sheet.

**Q10. Bubble sort's worst-case arrangement among the four inputs, and why.**

Reverse order is bubble sort's worst case, because every pair of different values is out of order and each one has to be swapped. Each pass only moves one value to its final place, so it needs the most passes, and early termination never helps. Swaps are slightly fewer than n(n - 1)/2 because equal values in median_income are not swapped.

Numbers: n = 2,000 reverse: 1,999,000 comparisons, 1,998,657 swaps, 3,997,314 writes, 1,999 passes, 290 ms (slowest of all orders; random 210 ms).

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

**Q11. Does early termination help much on nearly sorted input? Why a few out-of-place elements can still force many passes.**

Early termination helps only a little on nearly sorted input. Bubble sort moves a large value to the end quickly, but a small value near the end moves only one position towards the front per pass, so a few out-of-place values can force over a thousand passes. Runtime is about half of random because there are far fewer swaps, not because many passes are skipped.

Numbers: n = 2,000 nearly sorted (20 swaps): 1,542 passes, 1,894,347 comparisons, 24,683 swaps, 98.0 ms. Random: 1,971 passes, 1,998,594 comparisons, 1,012,299 swaps, 210 ms. Sorted: 1 pass.

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

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
