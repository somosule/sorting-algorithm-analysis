"""Dataset inspection required by Section 3, and duplication statistics for Section 4.4."""


def profile_dataset(path):
    """Print and save results/dataset_summary.csv.

    Total rows and columns; for each selected column: missing values, distinct values,
    min and max; the median_house_value cap and how many rows equal it.
    """
    raise NotImplementedError


def duplication_stats(values):
    """Return a dict with distinct_values, most_frequent_value, most_frequent_count,
    values_repeated (distinct values appearing more than once) and
    elements_in_repeats (entries belonging to those values)."""
    raise NotImplementedError
