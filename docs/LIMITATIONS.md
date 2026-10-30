# Limits and outstanding work

- **SIMULATED:** all leakage traces and CPA outcomes. No electrical measurement,
  full ML-KEM side-channel attack, or real countermeasure effectiveness established.
- **PASS (bounded host scope):** full ML-KEM-512 KATs test keygen, encapsulation,
  decapsulation and implicit rejection. Low-level PQClean APIs do not check external
  key validity; 20 NIST key-check cases are explicitly excluded. Other parameter
  sets are retained in original vector files but not run. No FIPS certification.
- PQClean is an archived dependency. Source is pinned, hashed and unmodified;
  no ongoing upstream security support is assumed. The current FIPS 203 landing
  page also lists potential errata. These sample vectors are a concrete baseline,
  not a proof covering every interpretation or future revision of the standard.
- **PASS:** ASan and UBSan were run on the exhaustive kernel and full ML-KEM test
  adapter under WSL Ubuntu GCC 11.4. Windows MinGW cannot link those runtimes;
  see `results/sanitizers-windows.json` versus `results/sanitizers-linux.json`.
  Passing checks cover tested executions only, not proof of memory safety.
  [Hosted run 40989404872](https://github.com/joeywwong/ml-kem-side-channel/actions/runs/40989404872)
  succeeded: its sole `host` job ran `test`, `host-mlkem`,
  `sanitize`, a sanitizer-PASS assertion, and `attack-sim` on Ubuntu 24.04 /
  Python 3.13.17. It did not run benchmarking, report generation, or hardware tasks.
- **NOT RUN:** MCU cycles, heap/stack high-water measurement, power, flash/RAM
  identification, hardware revisions and Nano firmware. No hardware availability
  inferred from a failed USB query. Host timings include operating-system noise.
- **Unfinished hardware stages:** D4 has no implemented Nano firmware/serial/capture
  pipeline; D5 has no board-specific STM32F407 firmware build or external capture
  pipeline. Toolchain, startup/linker integration, board identification, and a safe
  analog interface remain outstanding. Guard commands do not implement these paths.
- Scalar `% 3329` canonical encoding differs from signed/lazy Montgomery basemul;
  mathematical conversion checks do not establish matching physical leakage.
- First-order HW at isolated output instants is deliberately limited. The shares
  jointly encode the secret. Recombination, setup, register reuse, bus activity,
  higher order and compiler effects remain open physical failure mechanisms.
- CPA uses a maximum over 3329 guesses and 24 time samples. Null maxima are
  expected to be nonzero. Three report seeds and two test fixtures are not a broad
  statistical security assessment. No formal confidence or no-leakage claim.
- C canonical input range is an interface precondition; it is not a hardened
  arbitrary-input API. Functional masks are exhaustively tested over (s,r) with
  a varying multiplier plus boundary triples, not all 3329 cubed triples.
- Literature audit retains UNKNOWNs for inaccessible code commits and some
  acquisition details. No publication-gap, exact reproduction, or novelty claim.
