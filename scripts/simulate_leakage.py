"""Synthetic traces only: explicit output HW, AWGN and discrete jitter."""
import argparse
import json
from pathlib import Path
import numpy as np
from common import ROOT

Q = 3329
DEFAULT_SECRET = 1234  # Public, reproducible LAB FIXTURE; never a deployment key.
SEEDS = (101, 202, 303)
COUNTS = (100, 500, 1000, 2000)


def generate(seed=101, n=2000, secret=DEFAULT_SECRET, samples=24, sigma=1.0, jitter=1):
    if not 0 <= secret < Q or n < 3 or samples < 24 or sigma < 0 or not 0 <= jitter <= 2:
        raise ValueError("invalid simulation configuration")
    # Separate RNG streams for inputs, fresh shares, jitter and noise.
    streams = [np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(4)]
    a = streams[0].integers(1,Q,n,dtype=np.int64)  # Nonzero public multipliers.
    r = streams[1].integers(0,Q,n,dtype=np.int64)
    shifts = streams[2].integers(-jitter,jitter+1,n)
    noise = streams[3].normal(0,sigma,(n,samples))
    # Generator uses a scalar bit_count implementation independent of CPA LUT.
    hw = lambda values: np.fromiter((int(x).bit_count() for x in values),float,count=n)
    y = (a * secret) % Q
    y0 = (a * r) % Q
    y1 = (a * ((secret-r) % Q)) % Q
    assert np.array_equal((y0+y1)%Q,y)

    def inject(traces, values, center):
        # Fixed predeclared pulse. No key-specific sample selection or alignment.
        values = hw(values)
        for offset, weight in [(-1,0.5),(0,1.0),(1,0.5)]:
            traces[np.arange(n),center+shifts+offset] += weight*values

    baseline = noise.copy()
    inject(baseline,y,6)
    masked = noise.copy()
    inject(masked,y0,6)
    inject(masked,y1,12)
    recombined = masked.copy()
    inject(recombined,y,18)
    metadata = {"status":"SIMULATED", "seed":seed, "n":n, "samples":samples,
        "sigma":sigma, "jitter_samples":jitter, "q":Q,
        "model":"HW16(canonical reduced output); zero-extended register has same HW",
        "public_distribution":"uniform integers 1..3328", "pulse_centers":[6,12,18],
        "rng":"NumPy PCG64; four SeedSequence streams; simulation only",
        "comparison":"identical inputs, count, noise realization, jitter and sample grid",
        "secret_disclosure":"public lab fixture in source; never production key material"}
    return a, {"baseline":baseline,"masked":masked,"recombined":recombined,"noise":noise}, metadata


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=ROOT/"local-results/simulated")
    p.add_argument("--seed",type=int,default=101)
    p.add_argument("--traces",type=int,default=2000)
    args=p.parse_args()
    a,variants,meta=generate(args.seed,args.traces)
    args.output.mkdir(parents=True,exist_ok=True)
    for name,traces in variants.items():
        np.savez_compressed(args.output/f"{name}-{args.seed}.npz",a=a,traces=traces,
                            metadata=json.dumps(meta))
    print(f"SIMULATED: {len(variants)} datasets, {args.traces} x 24, seed {args.seed}")


if __name__=="__main__":
    main()
