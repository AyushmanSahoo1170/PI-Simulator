from decimal import Decimal

from engine.reference import set_precision


def brouncker(decimals: int, depth: int = 100_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    acc = Decimal(2)
    for k in range(depth, 1, -1):
        acc = 2 + Decimal((2 * k - 1) ** 2) / acc
    return 4 / (1 + 1 / acc), depth


def ramanujan_cf(decimals: int, max_depth: int = 200_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)

    def evaluate(depth: int) -> Decimal:
        acc = Decimal(6)
        for k in range(depth - 1, 0, -1):
            acc = 6 + Decimal((2 * k + 1) ** 2) / acc
        return 3 + 1 / acc

    depth = 64
    previous = evaluate(depth)
    while depth < max_depth:
        depth *= 2
        current = evaluate(depth)
        if abs(current - previous) < threshold:
            return current, depth
        previous = current
    return previous, depth
