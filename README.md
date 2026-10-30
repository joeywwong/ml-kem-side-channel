# ML-KEM arithmetic side-channel learning lab

A preliminary research-preparation project combining a **genuine host ML-KEM-512
correctness baseline** with a **separate educational modular-multiplication
surrogate** for studying leakage, correlation power analysis (CPA), and additive sharing.

**All side-channel traces are synthetic. No physical attack, full ML-KEM key
recovery, or secure masking implementation has been demonstrated.**

See [executed results](docs/RESULTS.md), [research design](docs/RESEARCH_DESIGN.md),
[progress](docs/PROGRESS.md), and [limitations](docs/LIMITATIONS.md).

## What this project demonstrates — short summary

- **ML-KEM-512 correctness on the host:** a pinned implementation checked against
  NIST ACVP vectors, round trips, and altered-ciphertext rejection behavior.
- **One-coefficient recovery in a synthetic model:** first-order correlation power
  analysis (CPA) recovers a fixed laboratory coefficient from simulated leakage
  of `y = (a*s) mod 3329` at 2000 traces for all three recorded seeds.
- **The effect and limits of additive sharing:** share-only synthetic leakage
  prevents recovery by this first-order attack in the recorded runs; exposing
  the recombined output restores recovery. This does not establish secure masking.
- **A reproducible evaluation workflow:** independent arithmetic checks,
  controlled leakage experiments, and limited host timing measurements, with
  physical capture and MCU firmware work still unfinished.

## Research question and methodology

Under an explicit Hamming-weight leakage model, can first-order CPA recover one
fixed laboratory coefficient, and how does fresh additive sharing change the
result when share outputs or recombination are visible?

The scalar target is `y = (a*s) mod 3329`, with a public nonzero input `a` and a
fixed canonical coefficient `s`. The simulator generates 24-sample traces with
reduced-output Hamming-weight pulses, Gaussian noise (sigma = 1), and integer
jitter of ±1 sample. Seeds 101, 202, and 303 each use nested prefixes of
100, 500, 1000, and 2000 traces. Pearson CPA searches **all 3329 candidates and all
24 samples**; the known fixture is used only to evaluate inference results.
Noise-only traces, permuted inputs, and an unreduced-product-HW model are controls.

The educational shared variant uses a fresh uniform simulated share `r`:

```text
s0 = r;                    s1 = (s - r) mod 3329
y0 = (a*s0) mod 3329;       y1 = (a*s1) mod 3329
(y0 + y1) mod 3329 = (a*s) mod 3329
```

Variants use identical inputs, noise, jitter, and sample grids. The share-only
model exposes separated share-output pulses while omitting setup/recombination
leakage; a failure variant also leaks the recombined output. C accepts
caller-provided shares and contains no RNG. Functional equivalence is tested
separately from the Python simulation: traces are **not measurements of C execution**.

## Recorded results

| Evidence | Recorded outcome | Scope |
|---|---|---|
| Host ML-KEM-512 | 25 keygen + 25 encapsulation + 10 decapsulation NIST ACVP cases; 25 deterministic and 100 OS-randomized round trips | Byte-for-byte vectors, altered-ciphertext checks, 9 adapter length rejections; not FIPS certification |
| Scalar C correctness | 11,082,241 canonical input pairs passed | Independent repeated-addition oracle |
| Shared C correctness | 11,082,241 `(s,r)` pairs with varying `a`, plus 119,844 boundary triples passed | Not exhaustive over all `3329^3` triples |
| Unprotected **synthetic** CPA, 2000 traces | Unique rank 1 for all three seeds | One laboratory fixture, not a full key |
| Share-only **synthetic** CPA, 2000 traces | Fixture ranks 729 / 3178 / 1567 | No recovery by this first-order attack in these runs; no masking-security conclusion |
| Visible-recombination **synthetic** CPA, 2000 traces | Unique rank 1 for all three seeds | Recombination leakage defeats the favorable model |
| Ryzen 7 7735U / MinGW host timing | Median 1.874 ns/call baseline; 4.349 ns/call shared (2.32×) | Excludes entropy, splitting, recombination; includes loop/call/checksum costs; not MCU timing or full countermeasure overhead |

![SIMULATED CPA rank and correlation comparison](results/figures/comparison.png)

The [full results](docs/RESULTS.md) retain controls, tied ranks, correlations,
benchmark dispersion, and sanitizer evidence. Six Python tests check C/Python
arithmetic, the Montgomery relation, simulation reproducibility, CPA against
NumPy, and additional fixtures/controls. Searching candidates and samples produces
nonzero null maxima; these runs are not a statistical no-leakage assessment.

## Relationship to ML-KEM and limitations

The unmodified, pinned PQClean `ml-kem-512/clean` baseline implements the full KEM
operations tested by the [host adapter and vector runner](scripts/host_mlkem.py).
Decapsulation calls `indcpa_dec`, then `polyvec_basemul_acc_montgomery` on secret
and ciphertext-derived polynomial data before the inverse NTT. The scalar target
is motivated by an individual secret-dependent multiplication along that path.

Actual basemul uses signed coefficients, Montgomery scaling, paired products,
twiddles, and accumulation. The toy uses canonical unsigned residues and `% 3329`.
Tests check `(montgomery_reduce(a*s)*65536) mod 3329 == toy(a,s)`, **not equal
representations or leakage**. Direct scalar-input control does not establish
equivalent control through ML-KEM ciphertexts.

The low-level API does not expose external key-validation entry points: 20 ACVP
key-check cases are excluded, and ML-KEM-768/1024 are not tested. Host checks are
neither complete FIPS API validation nor evidence of side-channel resistance.
Additive sharing has **not been validated as secure masking**. Setup,
register/bus transitions, compiler effects, randomness, higher-order leakage, and
recombination remain unresolved. This learning prototype makes no novelty or
paper-replication claim. See the [threat model](docs/THREAT_MODEL.md) and
[literature audit](docs/LITERATURE_REVIEW.md).

## Evidence stages and unfinished hardware work

| Stage | Status | Evidence or remaining work |
|---|---|---|
| D0: Research setup | Complete within documented scope | Pinned sources, protocol, literature audit, environment probe |
| D1: ML-KEM software baseline | PASS, host scope | NIST vectors, round trips, implicit rejection; Linux ASan/UBSan |
| D2: Scalar arithmetic and CPA | SIMULATED | C correctness and synthetic traces/controls |
| D3: Sharing and evaluation | SIMULATED; host cost measured | Functional shares, paired comparison, recombination failure |
| D4: Nano onboard capture | NOT RUN (NO HARDWARE) | Firmware, serial protocol, and capture pipeline are not implemented |
| D5: STM32F407 firmware / external capture | BLOCKED / unfinished | No board-specific firmware build; toolchain, startup/linker integration, board identification, and safe external analog interface outstanding |

Next: identify the Nano revision, complete a stock onboard sanity capture, then
port only the isolated kernel and inspect its ARM assembly. Full-scheme F407
firmware is a separate task. Nano-to-F407 capture feasibility is unverified;
see the [hardware checklist](docs/HARDWARE_SETUP_CHECKLIST.md).

## Reproduce the host work

Use **CPython 3.13** and GCC (MinGW-w64 on Windows, GCC on Linux); GNU binutils
provide object/disassembly reports. Windows Python 3.13.7 and Ubuntu CI Python
3.13.17 are verified environments. Pinned NumPy 2.5.3 requires Python >=3.12,
Matplotlib 3.11.2 >=3.11, and pytest 9.1.1 >=3.10. Their combined minimum is 3.12;
a full Python-version matrix has not been tested.

From the repository root, Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python tasks.py all
```

Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tasks.py all
```

`requirements.txt` pins the three direct dependencies; transitive versions can
differ. For the original Windows dependency closure, install
`requirements-lock-windows.txt` instead. It is not a Linux lockfile. Vendored
sources/vectors allow offline runs after dependency installation; builds verify
their hashes. No `make` is required; the Makefile forwards to the same task runner.

`all` runs `doctor`, `test`, `host-mlkem`, `sanitize`, `simulate`, `attack-sim`,
`bench`, and `report`. It writes local outputs and regenerates committed summaries
and reports; timings/environment metadata vary. Windows MinGW lacked sanitizer
runtimes: **NOT RUN** is reported without preventing `all` from finishing.
ASan/UBSan passed in recorded WSL and CI runs. Reports use the latest
`results/sanitizers.json`; platform snapshots retain earlier evidence.

The standalone sanitizer runner uses only Python's standard library and also ran
on Ubuntu Python 3.10.12. This does **not** establish Python 3.10 support for the
NumPy-based pipeline. From a Linux/WSL shell in the checkout:

```bash
python3 scripts/sanitize.py
# Regenerate reports afterwards in the Python 3.13 environment:
python tasks.py report
```

[GitHub Actions run 40989404872](https://github.com/joeywwong/ml-kem-side-channel/actions/runs/40989404872)
succeeded at commit `3f3d164093f16393059dd82ac604d2dd23d01db5`.
Its only job, `host` (Ubuntu 24.04, Python 3.13.17), installed requirements and ran
`test`, `host-mlkem`, `sanitize`, an assertion that both sanitizers passed, and
`attack-sim`. It did **not** run `doctor`, standalone `simulate`, `bench`, `report`,
or hardware tasks. See the [workflow](.github/workflows/host.yml).

Useful individual commands:

```bash
python tasks.py help
python -m pytest tests/test_cpa.py -q
python scripts/attack_cpa.py local-results/simulated/baseline-101.npz --known-secret 1234
python scripts/capture_nano.py --inspect-only
python tasks.py stm32-build
```

Run `simulate` before the standalone CPA example; 1234 is an intentionally public
synthetic fixture. `capture_nano.py --inspect-only` prints deferred status without
opening a device. Ordinary `nano-capture` and `stm32-build` fail explicitly:
these are guards, not working capture or firmware paths. On a fresh checkout,
run `attack-sim` then `report` to regenerate plots/Markdown from saved summaries
and the required ignored correlation arrays.

## Repository map, provenance, and references

- `src/`, `tests/`, `scripts/`: scalar C routines, host ML-KEM adapter, independent checks, simulation, CPA, and reporting.
- `third_party/`, [upstream-lock.json](upstream-lock.json): exact commits, URLs, and SHA-256 digests; unmodified upstream cryptographic sources.
- `results/`, `docs/`: summaries, labeled synthetic plots, protocol, and limitations. `results/run-manifest.json` records hashes for the original saved run.
- `build/`, `local-results/`: ignored build products, raw synthetic data, and local metadata.
- `firmware/`: deferred-stage notes only.

PQClean ML-KEM retains its [CC0/public-domain license](third_party/pqclean/crypto_kem/ml-kem-512/clean/LICENSE);
common files retain individual header notices. NIST vectors retain the
[upstream notice](third_party/acvp/UPSTREAM_README.md). Exact provenance and
licenses are in [REFERENCES.md](docs/REFERENCES.md). `scripts/fetch_upstream.py`
explicitly refreshes from fixed commits over the network; ordinary runs do not fetch.

Research anchors: [NIST FIPS 203](https://csrc.nist.gov/pubs/fips/203/final),
[*Find the Bad Apples* (TCHES 2023)](https://doi.org/10.46586/tches.v2023.i1.89-112),
and [*Masking Kyber* (TCHES 2021)](https://doi.org/10.46586/tches.v2021.i4.173-214).
The [literature matrix](docs/LITERATURE_REVIEW.md) explains their different settings
and unresolved details. This lab does not reproduce their physical attacks or
complete masking constructions.

**Research-learning prototype only; not production cryptographic code.**
