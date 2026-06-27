from decimal import Decimal
from math import factorial

from engine.reference import set_precision


def bbp(decimals: int, max_terms: int = 10_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    total = Decimal(0)
    power = Decimal(1)
    n = 0
    while n < max_terms:
        total += power * (
            Decimal(4) / (8 * n + 1)
            - Decimal(2) / (8 * n + 4)
            - Decimal(1) / (8 * n + 5)
            - Decimal(1) / (8 * n + 6)
        )
        power /= 16
        n += 1
        if 4 * power < threshold:
            break
    return total, n


def bellard(decimals: int, max_terms: int = 10_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    total = Decimal(0)
    power = Decimal(1)
    sign = 1
    n = 0
    while n < max_terms:
        total += sign * power * (
            Decimal(-32) / (4 * n + 1)
            - Decimal(1) / (4 * n + 3)
            + Decimal(256) / (10 * n + 1)
            - Decimal(64) / (10 * n + 3)
            - Decimal(4) / (10 * n + 5)
            - Decimal(4) / (10 * n + 7)
            + Decimal(1) / (10 * n + 9)
        )
        sign = -sign
        power /= 1024
        n += 1
        if 4 * power < threshold:
            break
    return total / 64, n


def chudnovsky(decimals: int) -> tuple[Decimal, int]:
    set_precision(decimals)
    terms = decimals // 14 + 2
    c = 640320
    c_cubed = c ** 3
    total = Decimal(0)
    for n in range(terms):
        numerator = factorial(6 * n) * (13591409 + 545140134 * n)
        denominator = factorial(3 * n) * factorial(n) ** 3 * c_cubed ** n
        if n % 2:
            numerator = -numerator
        total += Decimal(numerator) / Decimal(denominator)
    return Decimal(c) * Decimal(c).sqrt() / (12 * total), terms


def ramanujan(decimals: int) -> tuple[Decimal, int]:
    set_precision(decimals)
    terms = decimals // 8 + 2
    total = Decimal(0)
    for n in range(terms):
        numerator = factorial(4 * n) * (1103 + 26390 * n)
        denominator = factorial(n) ** 4 * 396 ** (4 * n)
        total += Decimal(numerator) / Decimal(denominator)
    return Decimal(9801) / (2 * Decimal(2).sqrt() * total), terms


def spigot(decimals: int) -> tuple[Decimal, int]:
    digits = []
    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3
    while len(digits) <= decimals:
        if 4 * q + r - t < n * t:
            digits.append(n)
            q, r, t, k, n, l = (
                10 * q,
                10 * (r - n * t),
                t,
                k,
                (10 * (3 * q + r)) // t - 10 * n,
                l,
            )
        else:
            q, r, t, k, n, l = (
                q * k,
                (2 * q + r) * l,
                t * l,
                k + 1,
                (q * (7 * k + 2) + r * l) // (t * l),
                l + 2,
            )
    return Decimal("3." + "".join(str(d) for d in digits[1:])), decimals
