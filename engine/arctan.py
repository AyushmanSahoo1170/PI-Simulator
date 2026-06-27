from decimal import Decimal

from engine.reference import set_precision

FORMULAS = {
    "machin": [(4, 5), (-1, 239)],
    "euler": [(1, 2), (1, 3)],
    "hutton": [(2, 3), (1, 7)],
    "stormer": [(6, 8), (2, 57), (1, 239)],
    "kanada": [(44, 57), (7, 239), (-12, 682), (24, 12943)],
}


def arctan_taylor(
    x: Decimal, threshold: Decimal, max_terms: int
) -> tuple[Decimal, int]:
    x_squared = x * x
    power = x
    total = Decimal(0)
    sign = 1
    terms = 0
    while terms < max_terms:
        term = power / (2 * terms + 1)
        if term < threshold:
            break
        total += sign * term
        sign = -sign
        power *= x_squared
        terms += 1
    return total, terms


def machin_like(
    spec: list[tuple[int, int]], decimals: int, max_terms: int = 10_000_000
) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    pi_over_4 = Decimal(0)
    total_terms = 0
    for coefficient, denominator in spec:
        value, terms = arctan_taylor(
            Decimal(1) / Decimal(denominator), threshold, max_terms
        )
        pi_over_4 += coefficient * value
        total_terms += terms
    return 4 * pi_over_4, total_terms


def leibniz(decimals: int, max_terms: int = 2_000_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    value, terms = arctan_taylor(Decimal(1), threshold, max_terms)
    return 4 * value, terms


def sharp(decimals: int, max_terms: int = 10_000_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    x = Decimal(1) / Decimal(3).sqrt()
    value, terms = arctan_taylor(x, threshold, max_terms)
    return 6 * value, terms
