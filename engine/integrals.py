from decimal import Decimal

from engine.reference import set_precision


def simpson_arctan(decimals: int, max_intervals: int = 100_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    needed = int((0.534 * 10 ** (decimals + 1)) ** 0.25) + 2
    intervals = min(needed, max_intervals)
    if intervals % 2:
        intervals += 1
    h = Decimal(1) / intervals
    total = Decimal(6)
    for i in range(1, intervals):
        x = h * i
        weight = 4 if i % 2 else 2
        total += weight * Decimal(4) / (1 + x * x)
    return total * h / 3, intervals
