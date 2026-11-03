"""Read housing.csv with the csv module and return values for one column."""
import csv


def load_rows(path):
    """Return every row as a dict of column name to text, in file order.

    Uses csv.DictReader; open with newline="" and encoding="utf-8".
    If the file is missing, raise FileNotFoundError with a message pointing to the README.
    """
    try:
        with open(path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"housing.csv not found at: {path}. See README: Data."
        ) from None


def load_column(path, column):
    """Return (values, missing) for one column.

    values: list of floats, in file order.
    missing: count of blank or non-numeric entries, which are skipped.
    """
    rows = load_rows(path)

    # Check that the requested column exists.
    if rows and column not in rows[0]:
        raise KeyError(f"Column '{column}' not found in {path}.")

    values = []
    missing = 0

    for row in rows:
        value = (row.get(column) or "").strip()

        try:
            values.append(float(value))
        except ValueError:
            missing += 1

    return values, missing
