from engine import METHODS, count_correct_decimals, reference_pi, timed
from engine.arctan import leibniz

TIER_TARGETS = {
    "instant": (8, 16, 32),
    "medium": (8, 16, 32),
    "slow": (8,),
}
SAMPLE_SIZES = (10_000, 100_000, 500_000)


def report(label, target, value, work, work_label, seconds):
    correct = count_correct_decimals(str(value))
    status = "PASS" if correct >= target else "FAIL"
    print(
        f"  {label:<26} target={target:<3} correct={correct:<3} "
        f"{work_label}={work:<9} {seconds * 1000:9.2f} ms  {status}"
    )


def main():
    print(f"reference pi (32 dp): {reference_pi(32)}")
    print()
    for tier in ("instant", "medium", "slow"):
        print(f"=== {tier} tier ===")
        for meta in METHODS.values():
            if meta["tier"] != tier:
                continue
            for target in TIER_TARGETS[tier]:
                (value, work), seconds = timed(meta["run"], target)
                report(meta["label"], target, value, work, meta["work_label"], seconds)
        print()

    print("=== statistical tier (digits achieved, never promised) ===")
    for meta in METHODS.values():
        if meta["tier"] != "statistical":
            continue
        for samples in SAMPLE_SIZES:
            (value, work), seconds = timed(meta["run"], samples)
            correct = count_correct_decimals(str(value))
            print(
                f"  {meta['label']:<26} samples={samples:<9} "
                f"correct={correct:<3} {seconds * 1000:9.2f} ms"
            )
    print()

    print("=== the leibniz wall (one digit per 10x work) ===")
    for cap in (1_000, 10_000, 100_000, 1_000_000):
        (value, terms), seconds = timed(leibniz, 8, cap)
        correct = count_correct_decimals(str(value))
        print(f"  terms={terms:<9} correct decimals={correct}   ({seconds:.2f} s)")


if __name__ == "__main__":
    main()
