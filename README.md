# π Simulator

**All 50 database entries accounted for: 29 live engines you can run for 8, 16 or 32 decimal places, plus 21 reference entries (identities, proofs, fixed fractions, duplicates, and industrial pipelines that express π without estimating it). One question: can a formula earn the asked decimals — and at what cost?**

Every engine computes in Python's `decimal` arbitrary-precision arithmetic (no external math libraries), and the digits it shows are exactly the digits you asked for, each verified character-by-character against the reference: green as they match, the first wrong digit stamped red. PASS means all asked decimals are correct; any surplus accuracy is reported in the note, never in the display. Each tile has its own Run button, a Compute-all button runs every engine into a live leaderboard, and the UI ships with both the dark lab theme and a warm paper light theme (toggle, top-right, remembered across visits).

## Quickstart

```
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. On Windows, use `py app.py` if `python` isn't on PATH.

Run the full terminal audit (every engine, every target, ~30 s):

```
python run_audit.py
```

## Project structure

```
pi-simulator/
├── app.py                  Flask: page + 3 JSON endpoints
├── run_audit.py            full verification audit (the report's results section)
├── requirements.txt        flask only — the math is pure stdlib
├── engine/
│   ├── reference.py        π to 100 digits, precision control (target + 10 guards)
│   ├── accuracy.py         digit-by-digit verification, timing
│   ├── registry.py         single source of truth: all 29 engines + metadata
│   ├── arctan.py           one Taylor engine → Leibniz, Machin, Euler, Hutton,
│   │                       Störmer, Kanada, Sharp
│   ├── series.py           Nilakantha, ζ(2)/ζ(4), Euler-accelerated, Newton arcsin
│   ├── products.py         Viète, Wallis, Euler prime product (with sieve)
│   ├── iterative.py        Archimedes, Gauss–Legendre, Borwein quartic
│   ├── modern.py           Chudnovsky, Ramanujan, BBP, Bellard, spigot
│   ├── integrals.py        Simpson's rule on ∫₀¹ 4/(1+x²) dx
│   ├── cfracs.py           Brouncker + Ramanujan continued fractions
│   └── probabilistic.py    Monte Carlo, Buffon's needle, coprime pairs
├── templates/index.html
└── static/style.css, main.js
```

## Measured results (from `run_audit.py`)

### Instant tier — reach 32 decimals in under a millisecond

| Engine | Year | Work for 32 dp | Time |
|---|---|---|---|
| Borwein Quartic | 1984 | 3 iterations | 0.05 ms |
| Chudnovsky | 1988 | 4 terms | 0.02 ms |
| Gauss–Legendre | 1975 | 5 iterations | 0.05 ms |
| Ramanujan 1914 | 1914 | 6 terms | 0.02 ms |
| Bellard | 1997 | 13 terms | 0.06 ms |
| Kanada 4-term | 1982 | 28 terms | 0.04 ms |
| BBP | 1995 | 32 terms | 0.10 ms |
| Spigot | 1995 | 32 digits | 0.30 ms |
| Machin | 1706 | 33 terms | 0.03 ms |
| Störmer | 1896 | 38 terms | 0.04 ms |
| Newton Arcsin | 1666 | 56 terms | 0.05 ms |
| Hutton | 1776 | 58 terms | 0.06 ms |
| Archimedes | ~250 BCE | 61 doublings | 0.6 ms |
| Viète | 1593 | 63 factors | 0.5 ms |
| Sharp | 1699 | 73 terms | 0.08 ms |
| Euler Arctan | 1738 | 95 terms | 0.08 ms |
| Euler-Accel. Leibniz | 1755 | 120 terms | 0.08 ms |

### Medium tier — pass 8 and 16, structurally unable to reach 32

| Engine | 8 dp | 16 dp | 32 dp |
|---|---|---|---|
| Nilakantha | 17,099 terms · 15 ms | 7,937,004 terms · 8.5 s | FAIL — 21 correct at 12M-term cap (15 s) |
| Euler ζ(4) | 694 terms | 321,830 terms · 0.25 s | FAIL — 18 correct at 1M cap |
| Simpson ∫4/(1+x²) | 154 intervals | 15,204 intervals | FAIL — 30 correct at 100k cap |
| Ramanujan Fraction | depth 32,768 | depth 262,144 · 0.4 s | FAIL — 16 correct at depth cap |

### Slow tier — cannot even reach 8 at sane caps

Leibniz: 6 correct after 2,000,000 terms. Basel ζ(2): 6 after 2M terms. Euler Prime Product: 6 from all 78,498 primes below a million. Wallis: 5 after 500k factors. Brouncker: 3 at depth 100,000.

### Statistical tier — 1–2 digits, ever

Monte Carlo, Buffon's needle, and coprime pairs each achieved 1–2 correct decimals at 500,000 samples. This is not an implementation flaw; it is the 1/√N law (see below).

### The Leibniz wall

| Terms | Correct decimals |
|---|---|
| 1,000 | 2 |
| 10,000 | 3 |
| 100,000 | 4 |
| 1,000,000 | 5 |

One digit per tenfold work — the textbook signature of O(1/N) convergence, measured live.

## The accuracy story (assignment: "comment on the accuracy of the simulator")

**1. Floats have a hard ceiling at ~16 digits.** An IEEE-754 double carries 53 bits of significand ≈ 15.95 decimal digits. `math.pi` itself is only correct to 15 decimal places. Reaching 32 therefore *requires* arbitrary precision: every engine runs in `decimal` with `prec = target + 10`. The estimate travels through the JSON API **as a string**, because the moment JavaScript coerces it to a Number, digits 17+ become noise.

**2. Convergence order is destiny.** What kills a method is not "slowness" but the order of its error term. Leibniz (error ~ 1/N) pays 10× more work per digit, forever. Nilakantha (~1/N³) cruises to 16 but needs ~1.7×10¹² terms for 32 — about two weeks of looping, hence its honest FAIL at the cap. Chudnovsky earns ~14 digits per term and clears 32 in four. Gauss–Legendre doubles its digit count every iteration; Borwein quadruples it.

**3. Simulation is not computation.** The Monte Carlo standard error is ≈ 1.64/√N, so 8 correct decimals demands N ≈ 10¹⁷ darts — centuries of compute. The simulators in this project exist to *demonstrate* that law, and the audit confirms it: half a million samples buy one or two digits. Simulation is how you understand π; series and iterations are how you compute it.

**4. Guard digits are visibly doing work.** Notice `correct` almost always exceeds `target` (e.g. Machin at target 32 verifies 36): the engine computes 10 extra digits and stops series at threshold 10^−(target+5), so clean bonus digits ride along. The exception proves the rule: the spigot algorithm produces *exact* digits with integer arithmetic only, so its `correct` equals its target precisely. Guard digits also absorb catastrophic cancellation — Gauss–Legendre's update `t ← t − p(a−a′)²` subtracts nearly equal quantities, which would silently destroy leading digits at working precision.

**5. Buffon's needle, without cheating.** Simulating the needle requires a random angle — and the naive `θ = random()·π` smuggles π into the experiment that is supposed to discover it. This implementation rejection-samples a direction inside the unit quarter-disc instead, so the simulation is genuinely π-free.

## Errata found by verification

Verification culture pays. Three bugs were caught while building this project:

1. **Source database, entry S09 (Sharp).** Printed as π = 6·Σ(−1)ⁿ/((2n+1)·3ⁿ); that sum actually equals π√3 ≈ 5.44. The √3 is missing — the correct identity is π = 2√3·Σ, implemented here as 6·arctan(1/√3). Passes all targets.
2. **Source database, entry S08 (Euler-accelerated Leibniz).** Printed as π/4 = Σ n!·2ⁿ·n!/(2n+1)!, but the partial sums (1 + 1/3 + 2/15 + … → 1.5707…) converge to **π/2**. Implemented as 2·Σ. Passes all targets.
3. **This project's own first draft of Brouncker** applied the outer 1² numerator twice (a bottom-up off-by-one). The audit reported `correct=0`; the fix was a one-line range change. Trust the reference digits, not the author.

## API

```
GET  /api/methods                       → all 50 entries (29 runnable, 21 reference)
POST /api/estimate {"method": "chudnovsky", "decimals": 32}
POST /api/estimate {"method": "monte_carlo", "samples": 500000}
```

Estimate response: `value` is a **string truncated to exactly the asked decimals** (10 for statistical engines); `correct` is the total verified count against the internal 100-digit reference (kept full-length server-side — it costs 100 bytes and lets the note report bonus accuracy); `bonus` = correct − target; `passed` is true only when every asked decimal is correct. Reference-only entries return 400 with an explanation. The "Compute all" leaderboard is driven client-side by calling this endpoint once per engine, streaming rows as they finish.

## Viva crib sheet

- **Why can't floats reach 32 decimals?** 53-bit significand ≈ 15.95 decimal digits; it's a representation limit, not a rounding habit.
- **Why guard digits?** Intermediate rounding (millions of additions) and cancellation (Gauss–Legendre's subtraction) eat trailing digits; 10 spare digits absorb the damage so the promised digits stay clean.
- **Why is the API value a string?** JSON numbers become IEEE doubles in JavaScript — instant truncation to ~16 digits.
- **Why does Monte Carlo fail at 8 decimals?** Error ∝ 1/√N ⇒ N ≈ 10¹⁷ samples. Statistical error, unfixable by precision.
- **Why does Kanada beat Machin per term?** Each arctan(1/q) term buys 2·log₁₀(q) digits; Kanada's smallest q is 57 vs Machin's 5.
- **Why does the spigot need no `decimal`?** It manipulates exact integer state and emits digits one at a time — a different paradigm entirely.
- **How do you stop a series without hardcoding term counts?** Alternating series error ≤ first omitted term, so loop while `term ≥ 10^−(target+5)`. 8/16/32 are inputs, never separate functions.

## Ideas for v2

Convergence chart (error vs work, log–log) per engine · BBP hexadecimal digit-extraction endpoint · Borwein nonic via Newton cube roots · export audit as CSV · deploy with gunicorn.

---

Python 3.9+ · Flask is the only dependency · math is 100% standard library `decimal`, `math`, `random`.
