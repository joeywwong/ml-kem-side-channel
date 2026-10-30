# Research design (D0–D3)

See [literature audit](LITERATURE_REVIEW.md)
for the selection rationale and access limits. Goal: validate an analysis pipeline,
not assert a physical ML-KEM vulnerability or claim novel cryptanalysis.

## Two independent tracks

**Full scheme:** unmodified PQClean `ml-kem-512/clean`, pinned at
`0586a824fc0d49df0b6b6e9179d8d15d06d0974f`. It is standards-aligned ML-KEM core
arithmetic/encapsulation, not a legacy directory renamed Kyber. Validate full
key bytes, ciphertext bytes and shared secrets against pinned NIST ACVP outputs.
Some upstream comments/macros still say Kyber. Key validation is not exposed by
the low-level API: passing these tests is not certification or proof of complete
FIPS API conformance. PQClean is now archived; this is a fixed educational
baseline, not a recommendation for new production deployments. No core patches.

**Educational operation:** `uint16_t z = (uint32_t)a*s % 3329`, canonical inputs
and output, public `a`, fixed lab coefficient `s`. It is a surrogate for one
secret-dependent field multiplication, not an ML-KEM implementation.

## Inspected source and dataflow

All paths below are under
[`third_party/pqclean/crypto_kem/ml-kem-512/clean`](../third_party/pqclean/crypto_kem/ml-kem-512/clean).

1. `kem.c`, `PQCLEAN_MLKEM512_CLEAN_crypto_kem_dec` calls `indcpa_dec` with the
   ciphertext and secret key, then re-encrypts and performs implicit rejection.
2. `indcpa.c`, `PQCLEAN_MLKEM512_CLEAN_indcpa_dec` unpacks ciphertext into `b,v`
   and the secret key into `skpv`; transforms **public** `b` with `polyvec_ntt`;
   calls `polyvec_basemul_acc_montgomery(&mp, &skpv, &b)`; then inverse NTT,
   subtraction from `v`, reduction and message decoding.
3. `polyvec.c` accumulates products of the secret and ciphertext polynomial
   vectors. `poly.c`, `poly_basemul_montgomery` processes pairs with twiddles.
4. `ntt.c`, `basemul` computes products in `Z_q[X]/(X^2-zeta)` using `fqmul`;
   `fqmul` calls `montgomery_reduce((int32_t)a*b)` in `reduce.c`.

This is a real secret-dependent path before the inverse NTT, not an attack on
the public-only NTT. The toy exposes a single coefficient directly; the full
scheme's ciphertext packing/compression/NTT constrains which intermediates an
attacker can select. Direct control of our scalar `a` is a **stronger lab interface**,
not demonstrated arbitrary control of a full-scheme coefficient.

## Representation and correspondence

The reference uses signed 16-bit coefficients and Montgomery products congruent
to `a*s*R^-1 mod q`, `R=65536`; includes pair products, twiddle multiplication,
vector accumulation and lazy reductions. The toy uses a 32-bit unsigned product
(maximum 11,075,584) and canonical `% q` output, with none of those extra steps.
`test_reference_compatibility.py` checks the relation
`(reference_montgomery(a*s)*65536) mod q == toy(a,s)` independently of KATs.
It does **not** assert equal bit patterns or leakage. NTT-domain secret coefficients
are not restricted to the small original noise-sampling range; search all 3329
canonical residues. Centered/signed encodings would need different predictions.

## Predeclared simulation and analysis

- Public inputs uniform on 1..3328; exclude zero so multiplication of a uniform
  share is a permutation. Functional tests still cover zero.
- Reproducible public lab fixture is in `simulate_leakage.py`. Disclosure is
  intentional for this example; routine reports omit coefficient values.
- Seeds 101, 202, 303; counts 100, 500, 1000, 2000, always nested prefixes in
  generated order. No trace rejection, alignment, tuning or cherry-picking.
- 24 samples, Gaussian noise sigma=1, independent integer jitter -1/0/+1,
  pulse weights [0.5,1,0.5]. Baseline pulse center 6; share pulses 6 and 12;
  deliberately visible recombination pulse 18. Pulse positions are model choices,
  not measured instruction timing.
- Hypothesis is HW of **16-bit canonical reduced output**, equal to HW of its
  zero-extension in a 32-bit return register. Optimized host assembly is inspected
  in [assembly audit](ASSEMBLY_AUDIT.md); physical correspondence remains untested.
- CPA centers each hypothesis and sample, computes Pearson correlation, scores
  each guess by maximum absolute correlation over **all** 24 samples. All 3329
  hypotheses use the same window. This is a multiple search, not a p-value.
- Inference accepts only public inputs/traces/model; known secret is used in a
  separate scoring function. Report 1-based best/worst tied rank; verified recovery
  means unique rank 1 equals the known lab fixture. Constant predictors score zero.
  A zero secret produces a constant output, so this centered HW CPA cannot
  identify it; the declared recovery experiment uses a nonzero lab fixture.
- Candidate chunk size 128 bounds the N-by-candidate workspace; no N-by-q-by-T
  tensor. Wrong model uses HW32 of the unreduced product. Multiplication by powers
  of two can create identical HW predictions in this wrong model; preserve ties.
- Independent noise-only data, permuted input labels, wrong model, two additional
  test secrets/seeds, and all incorrect guesses are controls. Noise-only traces
  reuse the paired noise realization, which is generated independently of inputs.

Success criterion: deterministic correctness tests and baseline unique rank 1
at the final count for each declared seed, with weaker/no recovery in controls.
Sharing evaluation reports the observed ranks and correlations, even if recovery
occurs. Failure of CPA to recover is never proof that leakage is absent.

## Sharing model and failure window

Fresh uniform `r` in Z_q each execution; `s0=r`, `s1=(s-r) mod q`;
`y0=a*s0 mod q`, `y1=a*s1 mod q`. Thus
`(y0+y1) mod q = a*(r+s-r) mod q = a*s mod q` because **a is public**.
This does not mask a product of two secret values, compression, SHAKE, rejection,
or complete decapsulation. For a nonzero a each individual product share is uniform;
their joint distribution still carries the secret and can leak at higher order.

Prospective trigger: prepare/load shares before rising edge; measure only
`lab_masked_mul`; lower trigger before recombination and serial verification.
This exclusion is a hypothesis, not protection: a physical observer can acquire
outside the trigger, and registers/buses can carry transitions between shares.
Original-secret loading, splitting, reuse of a mask, memory traffic, spills,
compiler transformations, glitches, and visible recombination can invalidate it.
The failure dataset deliberately adds output HW at sample 18; recovery should
return. No claim is made that those omitted effects are absent on any MCU.

PCG64 supplies fresh simulated shares only. C takes a caller-provided share; it
contains no entropy source. A future lab host could supply fresh uniform shares
using rejection sampling from an OS CSPRNG, but this leaves the host in control
and is not validated on-board masking randomness. No physical PRNG is supplied.

## Fairness and overhead

All variants use identical public inputs, noise realization, jitter, counts and
sample grid. This pairing reduces comparison variance; it is not independent
physical measurement. Three independent seeds are reported, not just the best.
Host timing uses matching input arrays and alternating measurement order, excludes
one warmup batch per variant, reports minimum/median/stdev and all batches.
Precomputed shares, entropy, splitting and recombination are outside timing;
call/loop/checksum overhead stays inside. Report object text size and compiler
per-function stack estimates separately; these are not MCU firmware size or
measured maximum whole-call-chain stack. No constant-time claim, TVLA test, or
physical security assertion follows from these measurements.
