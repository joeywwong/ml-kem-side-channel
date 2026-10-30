"""Predeclared multi-seed comparison, including a visible-recombination failure."""
import json
import numpy as np
from attack_cpa import cpa,summarize
from simulate_leakage import generate,SEEDS,COUNTS,DEFAULT_SECRET
from common import ROOT,save


def main():
    rows=[]
    out=ROOT/"local-results/simulated"
    out.mkdir(parents=True,exist_ok=True)
    for seed in SEEDS:
        a,variants,meta=generate(seed,n=max(COUNTS))
        # Permutation RNG is separate from generator streams.
        permuted=np.random.default_rng(seed+10000).permutation(a)
        for name in ["baseline","masked","recombined","noise","permuted","wrong_model"]:
            traces=variants["baseline" if name in ("permuted","wrong_model") else name]
            inputs=permuted if name=="permuted" else a
            model="product_hw" if name=="wrong_model" else "output_hw"
            for count in COUNTS:
                scores,corr=cpa(inputs[:count],traces[:count],model)
                rows.append({"seed":seed,"variant":name,"traces":count,"model":model,
                             **summarize(scores,corr,DEFAULT_SECRET)})
            if seed==SEEDS[0]:
                np.savez_compressed(out/f"cpa-{name}.npz",scores=scores,corr=corr)
        print(f"SIMULATED: evaluated all controls for seed {seed}",flush=True)
    result={"status":"SIMULATED","protocol":meta,"seeds":SEEDS,"counts":COUNTS,
            "search":"all 3329 guesses x all 24 samples; rank is 1-based with tie interval",
            "rows":rows}
    save("simulation.json",result)
    for row in rows:
        if row["traces"]==max(COUNTS):
            print(json.dumps(row))


if __name__=="__main__":
    main()
