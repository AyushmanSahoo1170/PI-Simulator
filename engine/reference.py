from decimal import getcontext

PI_DIGITS = (
    "3."
    "14159265358979323846264338327950288419716939937510"
    "58209749445923078164062862089986280348253421170679"
)

GUARD_DIGITS = 10


def set_precision(decimals: int) -> None:
    getcontext().prec = decimals + GUARD_DIGITS


def reference_pi(decimals: int) -> str:
    return PI_DIGITS[: decimals + 2]
