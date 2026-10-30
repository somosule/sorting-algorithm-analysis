# Evidence notes

For each question: the answer in 2-4 sentences, the exact numbers, and the table or plot that shows them. Sarah writes the final report answers from these notes.

## Scaling (4.2)
**Q1. Sample sizes and seed; why very small sizes are included.**

**Q2. Runtime, comparisons and writes for each algorithm and size; counts identical across repeats?**

**Q3. Observed runtime growth factor when n doubles vs theory (about 4x for O(n²), a little over 2x for O(n log n)); why they differ.**

**Q4. Bubble sort estimate for 20,640 values: calculation, assumptions, why approximate (and the actual time, if the optional check was run).**

**Q5. Input size at which merge sort's advantage becomes apparent; why the difference is less visible for very small inputs.**

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
