import random
from decimal import Decimal
from math import gcd, sqrt


def monte_carlo(samples: int) -> tuple[Decimal, int]:
    rand = random.random
    hits = 0
    for _ in range(samples):
        x = rand()
        y = rand()
        if x * x + y * y <= 1.0:
            hits += 1
    return Decimal(repr(4.0 * hits / samples)), samples


def buffon_needle(samples: int) -> tuple[Decimal, int]:
    rand = random.random
    crossings = 0
    for _ in range(samples):
        center = rand() * 0.5
        while True:
            u = rand()
            v = rand()
            norm = u * u + v * v
            if 0.0 < norm <= 1.0:
                break
        if center <= 0.5 * (v / sqrt(norm)):
            crossings += 1
    if crossings == 0:
        return Decimal(0), samples
    return Decimal(repr(2.0 * samples / crossings)), samples


def coprime_pairs(samples: int) -> tuple[Decimal, int]:
    randint = random.randint
    coprime = 0
    for _ in range(samples):
        if gcd(randint(1, 10_000_000), randint(1, 10_000_000)) == 1:
            coprime += 1
    if coprime == 0:
        return Decimal(0), samples
    return Decimal(repr(sqrt(6.0 * samples / coprime))), samples
