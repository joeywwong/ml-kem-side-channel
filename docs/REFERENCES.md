# Sources, versions and licenses

See [literature matrix](LITERATURE_REVIEW.md) for claims and unknowns.

| Source | Version / use | License / handling |
|---|---|---|
| [NIST FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) | Final published 2024-08-13; landing page notes potential errata. Standard definition, not our implementation certificate | Linked; publication not copied |
| [PQClean](https://github.com/PQClean/PQClean/tree/0586a824fc0d49df0b6b6e9179d8d15d06d0974f) | `0586a824fc0d49df0b6b6e9179d8d15d06d0974f`, only `ml-kem-512/clean`, META and five common files; archived upstream | ML-KEM code CC0/public domain per included LICENSE; common SHAKE/random/compat files preserve individual header notices. No core modifications |
| [NIST ACVP Server](https://github.com/usnistgov/ACVP-Server/tree/975de31eb83d87039ec88934fdc47d8c312b892d) | `975de31eb83d87039ec88934fdc47d8c312b892d`; `ML-KEM-keyGen-FIPS203`, `ML-KEM-encapDecap-FIPS203`, prompt + expectedResults | Preserve complete upstream README/license notice. US NIST employee software not subject to US copyright; read upstream notice for full terms |
| [PQM4](https://github.com/mupq/pqm4) | Surveyed for future M4 baseline; not vendored, built or selected. Historical paper Kyber is not automatically ML-KEM | No code copied; verify exact implementation/license/board support if later used |
| [Nano hardware docs](https://chipwhisperer.readthedocs.io/en/latest/Capture/ChipWhisperer-Nano.html) | Constraint/feasibility reference; actual revision UNKNOWN | Linked, no firmware copied |
| [Nano scope API](https://chipwhisperer.readthedocs.io/en/latest/scope-api.html) | For future version-specific D4 implementation | Not executed |

PQClean META identifies upstream algorithm source
`pq-crystals/kyber` commit `10b478fc3cc4ff6215eb0b6a11bd758bf0929cbd` via
`mkannwischer/package-pqclean` `85197ff`. This origin name alone does not establish
standard conformance: this lab separately checks the selected ML-KEM directory
against independent FIPS203 vectors. PQClean's legacy `nistkat-sha256` metadata
is not used as an independent oracle here.

Selected peer-reviewed anchors:

1. Shen, Cheng, Zhang, Guo, Jiang. *Find the Bad Apples*. TCHES 2023(1), 89–112.
   [DOI](https://doi.org/10.46586/tches.v2023.i1.89-112).
2. Rajendran, Ravi, D'Anvers, Bhasin, Chattopadhyay. *Pushing the Limits of Generic
   Side-Channel Attacks on LWE-based KEMs*. TCHES 2023(2), 418–446.
   [DOI](https://doi.org/10.46586/tches.v2023.i2.418-446).
3. Ravi, Paiva, Jap, D'Anvers, Bhasin. *Defeating Low-Cost Countermeasures*.
   TCHES 2024(2), 795–818. [DOI](https://doi.org/10.46586/tches.v2024.i2.795-818).
4. Bos, Gourjon, Renes, Schneider, van Vredendaal. *Masking Kyber: First- and
   Higher-Order Implementations*. TCHES 2021(4), 173–214.
   [DOI](https://doi.org/10.46586/tches.v2021.i4.173-214).
5. Rezaeezade, Yap, Jap, Bhasin, Picek. *Breaking the Blindfold: Deep Learning-based
   Blind Side-channel Analysis*. USENIX Security 2025.
   [Publisher and paper](https://www.usenix.org/conference/usenixsecurity25/presentation/rezaeezade).

These papers are studied for experimental framing, not reproduced. In particular,
the two PC-oracle papers do not substantiate ordinary scalar-output CPA, and the
low-cost-countermeasure paper is not a study of this lab's additive-sharing scheme.
