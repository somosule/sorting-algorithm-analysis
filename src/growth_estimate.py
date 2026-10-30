"""Section 4.2 steps 3 and 4: growth factors when n doubles, and the bubble sort estimate."""


def write_growth_factors():
    """Write results/growth_factors.csv from results/scaling.csv.

    For each algorithm and doubling (250 to 500 ... 2000 to 4000): measured runtime ratio,
    comparisons ratio, and theoretical ratio (4.0 for bubble and selection;
    2 * log2(2n) / log2(n) for merge).
    """
    raise NotImplementedError


def write_bubble_estimate():
    """Write results/bubble_estimate.csv: t(n) * (FULL_SIZE / n) ** 2 for several n, plus the average."""
    raise NotImplementedError
