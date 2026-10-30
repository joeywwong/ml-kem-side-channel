"""Chunked first-order Pearson CPA; inference has no known-secret argument."""
import argparse
import json
from pathlib import Path
import numpy as np

Q=3329
HW=np.array([i.bit_count() for i in range(256)],dtype=np.uint8)


def hamming_weight(values):
    x=np.asarray(values,dtype=np.uint32)
    return sum(HW[(x >> shift) & 255].astype(np.float64) for shift in (0,8,16,24))


def cpa(a,traces,model="output_hw",chunk=128):
    a=np.asarray(a)
    t=np.asarray(traces,dtype=np.float64)
    if a.ndim!=1 or t.ndim!=2 or len(a)!=len(t) or len(a)<3 or t.shape[1]<1:
        raise ValueError("expected matching N public inputs and NxT traces, N>=3")
    if not np.issubdtype(a.dtype,np.integer) or np.any((a<0)|(a>=Q)) or not np.isfinite(t).all():
        raise ValueError("noncanonical inputs or nonfinite traces")
    if model not in ("output_hw","product_hw") or chunk<1:
        raise ValueError("invalid model or chunk")
    centered=t-t.mean(axis=0)
    norms=np.sqrt(np.sum(centered**2,axis=0))
    corr=np.zeros((Q,t.shape[1]))
    for lo in range(0,Q,chunk):
        guesses=np.arange(lo,min(lo+chunk,Q),dtype=np.int64)
        products=a.astype(np.int64)[:,None]*guesses[None,:]
        h=hamming_weight(products%Q if model=="output_hw" else products)
        h-=h.mean(axis=0)
        denom=np.sqrt(np.sum(h*h,axis=0))[:,None]*norms[None,:]
        np.divide(h.T@centered,denom,out=corr[lo:lo+len(guesses)],where=denom>0)
    # Search over ALL samples for EVERY guess. Report this multiple search openly.
    scores=np.max(np.abs(corr),axis=1)
    return scores,corr


def summarize(scores,corr,known_secret):
    if not 0<=known_secret<Q:
        raise ValueError("invalid known lab secret")
    score=float(scores[known_secret])
    tied=np.isclose(scores,score,rtol=1e-12,atol=1e-12)
    better=(scores>score)&~tied
    rank=1+int(better.sum())
    rank_worst=rank+int(tied.sum())-1
    # Do not report guessed or known coefficients in routine output.
    return {"rank_best":rank,"rank_worst":rank_worst,"true_abs_corr":score,
            "max_abs_corr":float(scores.max()),
            "true_peak_sample":int(np.argmax(np.abs(corr[known_secret]))),
            "verified_recovery":bool(rank==1 and rank_worst==1)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("dataset",type=Path)
    p.add_argument("--known-secret",type=int,required=True,help="lab fixture, used only to score the result")
    p.add_argument("--model",choices=["output_hw","product_hw"],default="output_hw")
    args=p.parse_args()
    with np.load(args.dataset,allow_pickle=False) as d:
        scores,corr=cpa(d["a"],d["traces"],args.model)
        meta=json.loads(str(d["metadata"]))
    print(json.dumps({"dataset_status":meta["status"],"model":args.model,
                      **summarize(scores,corr,args.known_secret)},indent=2))


if __name__=="__main__":
    main()
