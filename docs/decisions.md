# Decision record

Every decision that affects more than one file or the report, with the reason. A decision that is not written down gets argued again; a decision without its reason cannot be defended in the report or Q&A.

Format:

```
## Dxx: Short title
**Decision:** what was agreed.
**Why:** the reason.
**Report:** what the report must say, if anything.
```

| # | Decision | Status |
|---|---|---|
| D01 | housing.csv committed in the repository root | Proposed |
| D02 | Seed 42 for every random step | Proposed |
| D03 | Sample sizes | Proposed |
| D04 | Sort values only, not full records | Proposed |
| D05 | total_bedrooms not used | Proposed |
| D06 | Counting choices beyond Section 4.1 | Proposed |
| D07 | Duplication statistic definitions | Proposed |
| D08 | Optional record lookup extension | Proposed |

Change a status to **Agreed** at the kickoff meeting.

## D01: housing.csv committed in the repository root
**Decision:** `housing.csv` sits next to `main.py` and is committed.
**Why:** The brief says to place it in the same folder as the code. Committing it (1.4 MB) means everyone uses the identical file. The README still gives the download link.
**Report:** Source URL and that the file is included.

## D02: Seed 42 for every random step
**Decision:** `SEED = 42` in `src/config.py`. Each random step creates a fresh `random.Random(SEED)`.
**Why:** Reproducibility (brief Section 7): the same samples and orders on every run and computer.
**Report:** State the seed and how samples and orders were generated.

## D03: Sample sizes
**Decision:** Scaling: 5, 10, 20, 250, 500, 1,000, 2,000, 4,000. Input order and repeated values: n = 2,000.
**Why:** The sizes suggested in the brief; small sizes support the "n < 20" decision-guide row; 2,000 shows differences while bubble and selection sort still finish quickly.
**Report:** List the sizes.

## D04: Sort values only, not full records
**Decision:** The experiments sort a list of floats from one column. Full rows are never reordered.
**Why:** Brief Section 3, step 4. Keeps counting rules simple and identical to other groups.
**Report:** One sentence.

## D05: total_bedrooms not used
**Decision:** The column is not analysed. Blank or non-numeric values in any column are counted as missing and skipped.
**Why:** Not required (brief Section 3, step 3). The column has blanks. Forward or back fill would be wrong because rows are independent census block groups, not a time series; a sound fill would use the same row's total_rooms or households.
**Report:** A short paragraph on missing values and why fill methods were not applied.

## D06: Counting choices beyond Section 4.1
**Decision:** The initial copy of the input is not counted as writes. Merge sort leftovers placed into the output count as writes. Bubble sort passes shorten by one each time. Swaps are reported separately.
**Why:** Section 4.1 asks us to state additional implementation choices.
**Report:** State each choice in the implementation section.

## D07: Duplication statistic definitions
**Decision:** "Values that occur more than once" = number of distinct values with a count above 1. We also report the total entries belonging to those values.
**Why:** The brief's wording can be read two ways; reporting both avoids ambiguity.
**Report:** State the definition with the 4.4 table.

## D08: Optional record lookup extension
**Decision:** `src/record_lookup.py` sorts row numbers using a column as the key, so original records can be looked up. Off by default (`RUN_RECORD_LOOKUP = False`), and run after the timed experiments only.
**Why:** Useful for reporting individual records; merge sort with `<=` keeps equal values in their original order (stability). Not part of the required experiments.
**Report:** Mention only if used, and explain the key-based implementation (brief Section 3, step 4).
