# Threat model

Only synthetic data and the user's own deliberately instrumented development
boards are in scope. D0–D3 perform no physical acquisition or hardware attack.

The simulation adversary knows/chooses a public nonzero scalar modulo 3329,
observes a noisy HW16 reduced-product signal, and searches one fixed canonical
secret coefficient. The evaluator knows the lab fixture only to check results.
Inference does not know the fixture, random shares or noise realization.

This recovers at most one toy coefficient, not an ML-KEM decapsulation key.
It omits real chosen-ciphertext feasibility, key lifetime limits, timing alignment,
analog bandwidth, instruction-dependent leakage, and secret distributions of
complete implementations. Full-scheme host correctness is an independent result.

For sharing, the favorable first-order model exposes each share at separate
sample times and hides initial loading, share setup and recombination. The failure
model exposes recombination too. Physical attackers are not bound to a digital
trigger window. The benchmark's precomputed mask data is not a security mechanism.
No claim covers higher-order combination, transition leakage, faults, glitches,
mask reuse, or a hostile host.

No networking targets, real deployment secrets, firmware updates, flashing,
soldering, power modifications, or external-target wiring are authorized here.
