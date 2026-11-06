# Contributing

DATA 5010 - Project 2: Sorting Algorithm Analysis

Read this and `docs/decisions.md` before starting a task. The team plan (Excel) gives each person's tasks in detail.

## Pull requests

- Every change reaches `main` through a pull request. Nobody pushes to `main` directly.
- One task = one branch = one pull request.
- **One approval before merging** (D26), always from someone other than the author:

| Author | Approved by |
|---|---|
| Patrick | Sarah |
| Henrietta | Sarah |
| Sarah | Patrick or Henrietta |

- The other teammate is welcome to comment, and should look at any pull request their own work builds on.

- The description says what changed, which task and brief section it covers, and how it was tested.
- Review within 24 hours. Request changes with the exact line and the fix.
- Say in the title if the pull request changes a shared file: `src/config.py`, `src/sorts.py` function names or return format, or the results CSV columns.

## Branches and commits

Branch: `<name>/<task-id>-<short-description>`, lowercase with hyphens, e.g. `patrick/p2-sorts`, `henrietta/h2-tests`.
Commit: `<TASK-ID>: <what changed>`, e.g. `P2: add bubble sort counters`.
Pull `main` before starting each task. Delete a branch after it is merged.

## Code rules

- Standard library only for loading data and the algorithms. `tests/test_structure.py` fails if pandas, NumPy, scikit-learn, SciPy or heapq is imported.
- No `sorted()` or `.sort()` except in `src/measure.py` (verification) and in tests. `tests/test_structure.py` checks this.
- Every fixed setting lives in `src/config.py`. No hard-coded seeds, sizes or paths elsewhere.
- Do not change shared function names, return formats or CSV columns without team agreement. Record the change in `docs/decisions.md`.
- Helper functions used only inside one file start with an underscore (`_merge`).
- Comments: short and clear; explain every line that adds to a counter. No team member names or task IDs in code comments.
- `snake_case` for files, functions and variables; `UPPER_SNAKE` for constants.

## Data and results

- `housing.csv` is never edited. Do not open and re-save it in Excel.
- Results are produced only by running `python main.py`. Never edit a results file by hand.
- Commit results only from a full run of the current `main`.

## Before opening a pull request

```bash
python -m unittest discover -v
```

All tests must pass.

## Quick reference

```
BRANCH   patrick/p2-sorts
COMMIT   P2: add bubble sort counters
REVIEW   one approval, never your own (Sarah for Patrick and Henrietta)
SETTINGS src/config.py only
TESTS    python -m unittest discover -v
RUN      python main.py
```
