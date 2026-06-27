from decimal import Decimal

from engine.reference import set_precision


def _threshold(decimals: int) -> Decimal:
    return Decimal(10) ** -(decimals + 5)


def nilakantha(decimals: int, max_terms: int = 12_000_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = _threshold(decimals)
    total = Decimal(3)
    sign = 1
    n = 1
    while n <= max_terms:
        term = Decimal(4) / (2 * n * (2 * n + 1) * (2 * n + 2))
        if term < threshold:
            break
        total += sign * term
        sign = -sign
        n += 1
    return total, n - 1


def zeta_even(k: int, decimals: int, max_terms: int) -> tuple[Decimal, int]:
    set_precision(decimals)
    if k == 2:
        needed = 10 ** (decimals + 1)
        scale, roots = 6, 1
    else:
        needed = int((10 ** (decimals + 1) / 3) ** (1 / 3)) + 1
        scale, roots = 90, 2
    terms = min(needed, max_terms)
    total = Decimal(0)
    for n in range(1, terms + 1):
        total += Decimal(1) / (n ** k)
    value = scale * total
    for _ in range(roots):
        value = value.sqrt()
    return value, terms


def euler_accelerated(decimals: int, max_terms: int = 100_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = _threshold(decimals)
    term = Decimal(1)
    total = Decimal(0)
    n = 0
    while term >= threshold and n < max_terms:
        total += term
        term = term * (n + 1) / (2 * n + 3)
        n += 1
    return 2 * total, n


def newton_arcsin(decimals: int, max_terms: int = 100_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = _threshold(decimals)
    term = Decimal(1) / 2
    total = Decimal(0)
    n = 0
    while term >= threshold and n < max_terms:
        total += term
        term = term * ((2 * n + 1) ** 2) / (8 * (n + 1) * (2 * n + 3))
        n += 1
    return 6 * total, n
