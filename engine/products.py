from decimal import Decimal
from math import isqrt

from engine.reference import set_precision


def viete(decimals: int, max_iterations: int = 300) -> tuple[Decimal, int]:
    set_precision(decimals)
    threshold = Decimal(10) ** -(decimals + 5)
    a = Decimal(2).sqrt()
    product = a / 2
    estimate = 2 / product
    iterations = 1
    while iterations < max_iterations:
        a = (2 + a).sqrt()
        product *= a / 2
        new_estimate = 2 / product
        iterations += 1
        if abs(new_estimate - estimate) < threshold:
            return new_estimate, iterations
        estimate = new_estimate
    return estimate, iterations


def wallis(decimals: int, max_terms: int = 500_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    product = Decimal(1)
    for n in range(1, max_terms + 1):
        square = 4 * n * n
        product *= Decimal(square) / (square - 1)
    return 2 * product, max_terms


def prime_product(decimals: int, limit: int = 1_000_000) -> tuple[Decimal, int]:
    set_precision(decimals)
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    product = Decimal(1)
    primes = 0
    for p in range(2, limit + 1):
        if sieve[p]:
            primes += 1
            square = p * p
            product *= Decimal(square) / (square - 1)
    return (6 * product).sqrt(), primes
