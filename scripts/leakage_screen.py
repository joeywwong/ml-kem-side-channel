"""First-order Welch fixed-vs-random screen. No exploitability/security claim."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def welch(waves, groups):
    w=np.asarray(waves,dtype=float);g=np.asarray(groups)
    if w.ndim!=2 or not w.shape[1] or g.shape!=(len(w),) or not np.isfinite(w).all():
        raise ValueError('Expected finite N-by-T waves and N group labels')
    if not np.isin(g,[0,1]).all() or min(np.sum(g==0),np.sum(g==1))<2:
        raise ValueError('Groups must be 0=fixed, 1=random, at least two each')
    a,b=w[g==0],w[g==1]
    delta=a.mean(axis=0)-b.mean(axis=0)
    v0=a.var(axis=0,ddof=1)/len(a);v1=b.var(axis=0,ddof=1)/len(b)
    den=np.sqrt(v0+v1);valid=den>0
    t=np.full(w.shape[1],np.nan);np.divide(delta,den,out=t,where=valid)
    return t, {'fixed_count':len(a),'random_count':len(b),'invalid_samples':int((~valid).sum()),
               'constant_unequal_samples':int(np.sum((~valid)&(delta!=0))),
               'threshold':4.5,'samples_exceeding':int(np.sum(np.abs(t[valid])>4.5)),
               'max_abs_t':float(np.max(np.abs(t[valid]))) if valid.any() else None,
               'interpretation':'screen only; correlated/multiple sample tests; threshold is not a calibrated family-wise p-value; no secret recovery inferred'}


def load_screen(path):
    with np.load(path,allow_pickle=False) as z:
        waves=z['waves'];groups=z['groups'];meta=json.loads(str(z['metadata']))
    if meta.get('status') not in ['SIMULATED','INSTRUMENTED_DEVICE','MEASURED_MLKEM']:
        raise ValueError('Explicit trace provenance required')
    if not meta.get('group_definition') or not meta.get('acquisition_order'):
        raise ValueError('Group definition and acquisition ordering required')
    return waves,groups,meta


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('dataset',type=Path);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();w,g,meta=load_screen(args.dataset);t,report=welch(w,g)
    args.out.mkdir(parents=True,exist_ok=False)
    report.update(metadata=meta,sha256=hashlib.sha256(args.dataset.read_bytes()).hexdigest())
    (args.out/'screen.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    np.savetxt(args.out/'welch.csv',np.column_stack([np.arange(len(t)),t]),delimiter=',',header='sample,t_statistic',comments='')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,4));ax.plot(t);ax.axhline(4.5,color='r',linestyle='--');ax.axhline(-4.5,color='r',linestyle='--')
    ax.set(xlabel='Sample index',ylabel='Welch t statistic',title=meta['status']+': fixed-vs-random screen; not key recovery')
    fig.tight_layout();fig.savefig(args.out/'welch.png',dpi=150);plt.close(fig)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
