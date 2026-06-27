from decimal import Decimal

from engine.reference import set_precision


def archimedes(decimals: int, max_iterations: int = 300) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    upper = 2 * Decimal(3).sqrt()
    lower = Decimal(3)
    iterations = 0
    while upper - lower > threshold and iterations < max_iterations:
        upper = 2 * upper * lower / (upper + lower)
        lower = (upper * lower).sqrt()
        iterations += 1
    return (upper + lower) / 2, iterations


def gauss_legendre(decimals: int, max_iterations: int = 30) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    a = Decimal(1)
    b = 1 / Decimal(2).sqrt()
    t = Decimal(1) / 4
    p = Decimal(1)
    iterations = 0
    while abs(a - b) > threshold and iterations < max_iterations:
        a_next = (a + b) / 2
        b = (a * b).sqrt()
        t -= p * (a - a_next) ** 2
        p *= 2
        a = a_next
        iterations += 1
    return (a + b) ** 2 / (4 * t), iterations


def borwein_quartic(decimals: int, max_iterations: int = 15) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    sqrt2 = Decimal(2).sqrt()
    y = sqrt2 - 1
    a = 6 - 4 * sqrt2
    estimate = 1 / a
    iterations = 0
    while iterations < max_iterations:
        fourth_root = (1 - y ** 4).sqrt().sqrt()
        y = (1 - fourth_root) / (1 + fourth_root)
        a = a * (1 + y) ** 4 - Decimal(1 << (2 * iterations + 3)) * y * (
            1 + y + y * y
        )
        iterations += 1
        new_estimate = 1 / a
        if abs(new_estimate - estimate) < threshold:
            return new_estimate, iterations
        estimate = new_estimate
    return estimate, iterations
