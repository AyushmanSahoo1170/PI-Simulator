from time import perf_counter

from engine.reference import PI_DIGITS


def count_correct_decimals(estimate: str) -> int:
    if not estimate.startswith("3."):
        return 0
    correct = 0
    for given, true in zip(estimate[2:], PI_DIGITS[2:]):
        if given != true:
            break
        correct += 1
    return correct


def timed(func, *args, **kwargs):
    start = perf_counter()
    result = func(*args, **kwargs)
    return result, perf_counter() - start
