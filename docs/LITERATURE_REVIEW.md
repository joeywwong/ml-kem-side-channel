# Literature audit and experiment selection

Audited before implementing the scalar target. This is a learning
project, not a novelty claim or replication of the papers' key recovery.
UNKNOWN means not established by the accessible source. Paper-era Kyber is not
silently treated as FIPS 203 ML-KEM. The matrix uses publisher records, accessible
author manuscripts, and the USENIX proceedings; ePrint is an access route, not a venue.

| Paper / venue | Scheme, target, code provenance | Hardware / modality | Attacker and model / objective | Countermeasure / criterion / artifacts |
|---|---|---|---|---|
| Shen et al., **Find the Bad Apples**, TCHES 2023(1), 89–112 (online 2022) | Kyber512, optimized PQM4; plaintext-checking oracle during decryption; precise implementation commit and line UNKNOWN in accessible publisher record | STM32F407G Cortex-M4, **EM**, not a Nano power capture | Chosen ciphertexts, imperfect PC oracle, detect and correct wrong recovered coefficients; full key recovery objective | Error correction of oracle outputs, rather than a masking defense; success is recovery under erroneous oracle responses. [Publisher](https://tches.iacr.org/index.php/TCHES/article/view/9948), [authors' artifact](https://github.com/7a17/Find-the-Bad-Apples). Exact acquisition equipment and reproduction not verified. |
| Rajendran et al., **Pushing the Limits of Generic Side-Channel Attacks**, TCHES 2023(2), 418–446 | Kyber and other LWE KEMs; parallel plaintext-checking oracles; exact code location and commit UNKNOWN | Exact acquisition setup UNKNOWN in this audit | Chosen ciphertexts, extracting multiple PC decisions to recover the key; not coefficient-HW CPA | Evaluate oracle efficiency/key recovery; no claim to replicate it here. [Publisher](https://tches.iacr.org/index.php/TCHES/article/view/10289). Artifact commit UNKNOWN. |
| Ravi et al., **Defeating Low-Cost Countermeasures**, TCHES 2024(2), 795–818 | CRYSTALS-Kyber decryption leakage/linear inequalities; exact source commit and line UNKNOWN | Hardware/acquisition specifics UNKNOWN in accessible excerpt | Chosen ciphertext attacks, including valid ciphertexts; improved inequality solver for key recovery | Attacks **ciphertext sanity checks and decapsulation failure checks**, not this lab's additive sharing; criterion is key recovery despite detection. [DOI](https://doi.org/10.46586/tches.v2024.i2.795-818), [manuscript](https://eprint.iacr.org/2023/1627). Full publisher PDF was access-blocked; no hardware replication claim. |
| Bos et al., **Masking Kyber**, TCHES 2021(4), 173–214 | Complete pre-standard Kyber masking, including one-bit compression and masked polynomial comparison; commit/line UNKNOWN | Cortex-M0+ and Cortex-M4F; experimental leakage assessment and performance | First- and higher-order protection; nonlinear operations and conversions need dedicated constructions | Security model and leakage evaluation exceed a scalar share split. [DOI](https://doi.org/10.46586/tches.v2021.i4.173-214), [author manuscript](https://joostrenes.nl/publications/maskingkyber.pdf). Study concepts; no implementation or formal-verification replication. |
| Rezaeezade et al., **Breaking the Blindfold**, USENIX Security 2025 | Kyber, AES, ASCON; DL blind SCA and multi-point cluster labeling; exact code commit UNKNOWN | **Kyber is STM32F3; STM32F4 is ASCON** (Table 1). Real traces | Blind input setting, neural/cluster inference, key recovery; different prerequisites from known-input CPA | Includes desynchronization study; success measured by key ranking/recovery. [Proceedings PDF](https://www.usenix.org/system/files/usenixsecurity25-rezaeezade.pdf), [publisher](https://www.usenix.org/conference/usenixsecurity25/presentation/rezaeezade). Do not infer a Kyber-on-F4 experiment from the abstract's list of platforms. |

The matching F407 board in *Bad Apples* motivates later study, but an EM probe,
an imperfect PC classifier, chosen-ciphertext construction, and full-scheme
firmware are additional prerequisites. A Nano's built-in F030 (16 KB flash,
4 KB RAM) and short capture buffer do not reproduce that setup. No such classifier
or oracle-correction algorithm is implemented in D0–D3.

Selected feasible experiment: canonical scalar multiplication modulo 3329,
motivated by one multiply in the secret/ciphertext basemul before inverse NTT.
Implement first-order known-input CPA and fresh additive sharing **in simulation**.
Study public-linear sharing and the danger of visible recombination; do not
attribute the scalar model to any of these papers. Independently test pinned
full ML-KEM-512 C against NIST ACVP vectors. This separation allows honest host
progress without Nano availability, an external probe, or an unverified linker map.

Access limits: publisher pages/abstracts were readable for the two 2023 papers;
some TCHES PDF endpoints denied access. Unknowns above are intentionally retained.
The author-hosted masking manuscript and USENIX full paper were accessible.
