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

Merge sort always splits the list in half and merges the halves back together, so it does the same number of merge levels whatever the input order. Order only changes how many comparisons each merge needs: when one half runs out early, as with sorted or reverse input, the rest of the other half is copied without comparing. Bubble sort's work depends directly on how many pairs are out of order, so it ranges from n - 1 comparisons to n(n - 1)/2. These counts also depend on our implementation: it splits at the middle, uses <= and counts every placed value as a write, so a version that first checks whether two halves are already in order would give different counts.

Numbers: n = 2,000 merge comparisons: sorted 10,864, reverse 11,202, nearly sorted 14,370, random 19,419 (less than 2 times apart); merge writes 21,952 for every order. Bubble comparisons: 1,999 (sorted) to 1,999,000 (reverse), about 1,000 times apart.

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

**Q9. Best-performing algorithm for each input order, justified in 2-3 sentences.**

Random: merge sort is fastest because it does far fewer comparisons than the O(n²) sorts. Sorted: bubble sort is fastest because one pass with no swaps confirms the order and early termination stops it. Nearly sorted and reverse: merge sort is fastest; bubble sort still needs many passes, and selection sort always makes n(n - 1)/2 comparisons.

Numbers: n = 2,000 median runtime (bubble / selection / merge): random 210 / 87.9 / 2.88 ms; sorted 0.103 / 87.6 / 2.32 ms; nearly sorted 98.0 / 87.4 / 2.49 ms; reverse 290 / 92.4 / 2.32 ms.

Evidence: results/input_order.csv, tables/input_order_table.csv, tables/decision_guide_evidence.csv; workbook 4.3 Input order sheet.

**Q10. Bubble sort's worst-case arrangement among the four inputs, and why.**

Reverse order is bubble sort's worst case, because every pair of different values is out of order and each one has to be swapped. Each pass only moves one value to its final place, so it needs the most passes, and early termination never helps. Swaps are slightly fewer than n(n - 1)/2 because equal values in median_income are not swapped. Its comparisons are almost the same as random (1,999,000 against 1,998,594), so the difference shows in swaps (1,998,657 against 1,012,299), writes and passes.

Numbers: n = 2,000 reverse: 1,999,000 comparisons, 1,998,657 swaps, 3,997,314 writes, 1,999 passes, 290 ms (slowest of all orders; random 210 ms).

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

**Q11. Does early termination help much on nearly sorted input? Why a few out-of-place elements can still force many passes.**

Early termination helps only a little on nearly sorted input. Bubble sort moves a large value to the end quickly, but a small value near the end moves only one position towards the front per pass, so a few out-of-place values can force over a thousand passes. Runtime is about half of random because there are far fewer swaps, not because many passes are skipped.

Numbers: n = 2,000 nearly sorted (20 swaps): 1,542 passes, 1,894,347 comparisons, 24,683 swaps, 98.0 ms. Random: 1,971 passes, 1,998,594 comparisons, 1,012,299 swaps, 210 ms. Sorted: 1 pass.

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

## Repeated values (4.4)
**Q12. Comparisons, writes and runtimes across the three columns; which observations come from duplication and which from input order or implementation.**

The three columns give almost the same counts and runtimes, so duplication has only a small effect at n = 2,000. The differences have three causes. Duplication: bubble and selection sort never swap equal values, so more equal pairs means fewer swaps. Sample order: each column's sample is arranged differently, and this effect is larger than duplication; housing_median_age should need about 25,000 fewer bubble swaps than an average random arrangement, but its order added about 17,000, and the same median_income values needed about 20,700 more swaps when reshuffled. Implementation: selection sort always makes 1,999,000 comparisons and merge sort always makes 21,952 writes, whatever the duplicates.

Numbers: n = 2,000 (distinct values / equal pairs / bubble swaps / expected bubble swaps): median_income 1,785 / 343 / 991,628 / 999,328; housing_median_age 51 / 49,886 / 991,442 / 974,557; median_house_value 1,322 / 5,266 / 981,103 / 996,867. Merge comparisons: 19,371 / 19,186 / 19,250. Runtime (bubble / selection / merge): median_income 208 / 87.7 / 2.88 ms; housing_median_age 208 / 87.3 / 3.11 ms; median_house_value 206 / 88.3 / 2.91 ms. Same median_income values reshuffled: 1,012,299 bubble swaps.

Evidence: results/repeated_values.csv, tables/repeated_values_table.csv, plot repeated_values.png; workbook 4.4 Repeated values sheet.

## Decision guide (4.5)

| Situation | Best algorithm | Evidence from our results | Why |
|---|---|---|---|
| Large random input | Merge sort | n = 4,000: merge 6.28 ms, selection 352 ms, bubble 847 ms. All 20,640 values: merge 38.7 ms, bubble 22.9 s | 42,817 comparisons at n = 4,000, against about 8 million for bubble and selection |
| Very small list (n < 20) | Selection sort | Selection / bubble / merge: n = 5: 1.18 / 1.42 / 2.10 µs; n = 10: 3.53 / 4.14 / 5.34 µs; n = 20: 10.8 / 17.5 / 12.7 µs | No recursion or new lists, and the fewest writes (6, 16 and 32) |
| Already sorted input | Bubble sort | n = 2,000: bubble 0.103 ms (1 pass, 1,999 comparisons, 0 writes); merge 2.32 ms; selection 87.6 ms | Early termination stops it after one pass with no swaps |
| Nearly sorted input | Merge sort | n = 2,000: merge 2.49 ms; selection 87.4 ms; bubble 98.0 ms (1,542 passes) | Small values near the end move one place per pass, so bubble sort still needs many passes |
| Reverse-sorted input | Merge sort | n = 2,000: merge 2.32 ms (11,202 comparisons); selection 92.4 ms; bubble 290 ms (1,998,657 swaps, 1,999 passes) | Merge sort's work hardly changes with order; reverse is bubble sort's worst case |
| Many repeated values | Merge sort | housing_median_age (51 distinct values): merge 3.11 ms, selection 87.3 ms, bubble 208 ms. median_income: 2.88 / 87.7 / 208 ms | Duplicates change the counts only slightly (Q12); the algorithm matters far more |

## Reflection (4.6)
**Q13. Bubble and selection sort are both O(n²). Why can they behave differently on sorted input?**

Both sorts are O(n²), but bubble sort can stop early and selection sort cannot. On sorted input, bubble sort finds nothing to swap in its first pass, so early termination ends the sort after one pass. Selection sort still scans the whole unsorted part on every pass to find the minimum, so it makes all n - 1 passes and n(n - 1)/2 comparisons.

Numbers: n = 2,000 sorted: bubble 1 pass, 1,999 comparisons, 0.103 ms; selection 1,999 passes, 1,999,000 comparisons, 87.6 ms.

Evidence: results/input_order.csv, tables/input_order_table.csv; workbook 4.3 Input order sheet.

**Q14. One realistic reason someone might still choose selection or bubble sort.**

Selection sort is a sensible choice when writing to memory is expensive, such as on flash storage, because it makes at most n - 1 swaps. It was also the fastest of the three sorts on very small lists and needs no extra memory. Both simple sorts are short and easy to check.

Numbers: writes on random input, n = 2,000: selection 3,982, merge 21,952, bubble 2,024,598. Runtime at n = 5, 10 and 20: selection 1.18, 3.53 and 10.8 µs (fastest at each size). Peak memory at n = 2,000: selection 15.7 KiB, merge 48.8 KiB.

Evidence: results/input_order.csv, tables/scaling_small_n_table.csv, results/memory.csv; workbook 4.2 Scaling sheet.

**Q15. At least two reasons the measured slowdown when doubling n is not exactly 4x or 2x.**

The comparison ratios stay close to theory while the runtime ratios move further away, so most of the gap comes from the computer rather than the algorithm. First, runtime includes Python overhead and memory allocation, not only comparisons. Second, larger lists make less efficient use of the memory cache. Third, timings vary with other activity on the computer; the median of five runs reduces this but does not remove it. Lower-order terms (merge sort's theory ratio is 2.18 to 2.25, not 2) and a different random sample at each size also play a part.

Numbers: runtime ratios from n = 250 to 4,000: bubble 3.90 to 4.22, selection 4.00 to 4.15, merge 2.16 to 2.23. Comparison ratios: bubble 3.97 to 4.04, selection 4.00 to 4.01, merge 2.21 to 2.30. Theory: 4.00 for O(n²); 2.18 to 2.25 for O(n log n).

Evidence: tables/scaling_growth_factors_table.csv; workbook 4.2 Growth (Q3) sheet.

**Q16. How merge sort's additional memory requirement affects the choice of algorithm.**

Merge sort builds new lists while it merges, so it needs extra memory roughly in proportion to n, and our version also copies values when it slices the list. Bubble and selection sort work in place and need only a few extra variables. At n = 2,000 merge sort used about three times the peak memory of the other two, which is small, so its speed is worth it here; when memory is limited or the data is very large, an in-place sort may be the better choice.

Numbers: peak memory at n = 2,000 (tracemalloc): bubble 15.7 KiB, selection 15.7 KiB, merge 48.8 KiB.

Evidence: results/memory.csv; workbook Extras sheet.

**Q17. Why the same input and a consistent measurement method matter when comparing algorithms.**

A fair comparison needs every difference to come from the algorithm, not from the data or the timer. All three sorts received the same seed-42 sample, and the counts were identical in all five repeats, which measure.py checks. Loading was kept outside the timer, each timing is the median of five runs, and all official timings came from one computer. Even so, the same sample took 210 ms in one experiment and 208 ms in another, which shows why a single timing is not enough.

Numbers: seed 42; median of 5 runs; n ≤ 20 timed as a loop of 1,000 calls. Bubble sort on the n = 2,000 median_income sample: 1,998,220 comparisons and 991,628 swaps in both scaling.csv and repeated_values.csv, with runtimes of 210 ms and 208 ms. Official run: Python 3.14.7 on one computer.

Evidence: results/run_info.csv, results/scaling.csv, results/repeated_values.csv; workbook Run info sheet.
