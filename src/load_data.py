"""Read housing.csv with the csv module and return values for one column."""
import csv


def load_rows(path):
    """Return every row as a dict of column name to text, in file order.

    Uses csv.DictReader; open with newline="" and encoding="utf-8".
    If the file is missing, raise FileNotFoundError with a message pointing to the README.
    """
    raise NotImplementedError


def load_column(path, column):
    """Return (values, missing) for one column.

    values: list of floats, in file order.
    missing: count of blank or non-numeric entries, which are skipped.
    """
    raise NotImplementedError
