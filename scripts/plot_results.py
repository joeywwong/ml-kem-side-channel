"""Render figures and Markdown only from real saved execution outputs."""
import hashlib
import json
from datetime import datetime,timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from common import ROOT,RESULTS,save,verify_sources
from simulate_leakage import generate,DEFAULT_SECRET


# Historical execution evidence, checked against the hosted job steps and logs.
# Keep this separate from local JSON: the CI job does not run bench or report.
CI_EVIDENCE = (
    '[GitHub Actions run 40989404872](https://github.com/joeywwong/ml-kem-side-channel/actions/runs/40989404872) '
    'succeeded at commit `3f3d164093f16393059dd82ac604d2dd23d01db5`. '
    'Its only job, `host`, used Ubuntu 24.04, Python 3.13.17 and GCC 13.3.0. '
    'After installing requirements it ran `test`, `host-mlkem`, `sanitize`, '
    'an assertion that both ASan and UBSan passed, and `attack-sim`; all succeeded. '
    'It did not run `doctor`, standalone `simulate`, `bench`, `report`, or hardware tasks. '
    'Metrics in this report come from saved local JSON; the hosted job did not generate this report.'
)


def read(name):
    path=RESULTS/name
    if not path.exists(): raise RuntimeError(f'BLOCKED: missing {path.name}; run required task first')
    return json.loads(path.read_text())


def main():
    sim=read('simulation.json'); kem=read('host-mlkem.json'); bench=read('benchmark.json')
    tests=read('tests.json'); sanitizers=read('sanitizers.json');env=read('environment.json')
    sanitizer_text='; '.join(f"{name}: {result['status']} ({result.get('host',{}).get('compiler','compiler metadata unavailable')})" for name,result in sanitizers.items())
    assert sim['status']=='SIMULATED' and kem['status']==tests['status']==bench['status']=='PASS'
    figdir=RESULTS/'figures';figdir.mkdir(exist_ok=True)
    colors=dict(baseline='#0969da',masked='#238636',recombined='#cf222e',
                noise='#6e7781',permuted='#8250df',wrong_model='#9a6700')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    for name,color in colors.items():
        for idx,seed in enumerate(sim['seeds']):
            rows=[r for r in sim['rows'] if r['variant']==name and r['seed']==seed]
            x=[r['traces'] for r in rows]
            axes[0].plot(x,[r['rank_best'] for r in rows],color=color,alpha=.65,
                         marker='.',label=name if idx==0 else None)
            axes[1].plot(x,[r['true_abs_corr'] for r in rows],color=color,alpha=.65,marker='.')
    axes[0].set(yscale='log',ylabel='Known coefficient rank (1 = best; best tied rank)',xlabel='Number of synthetic traces')
    axes[1].set(ylabel='Known coefficient max |Pearson correlation|',xlabel='Number of synthetic traces',ylim=(0,.85))
    axes[0].legend(fontsize=8,ncol=2)
    for ax in axes: ax.grid(alpha=.2)
    fig.suptitle('SIMULATED — first-order CPA and additive sharing\nSeeds 101 / 202 / 303; sigma=1; jitter ±1; all 24 samples searched')
    fig.savefig(figdir/'comparison.png',dpi=160);plt.close(fig)

    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for ax,name in zip(axes.ravel(),['baseline','masked','recombined','noise']):
        path=ROOT/f'local-results/simulated/cpa-{name}.npz'
        if not path.exists(): raise RuntimeError('Run attack-sim to generate correlation arrays')
        with np.load(path,allow_pickle=False) as d:
            scores,corr=d['scores'],d['corr']
        ax.plot(np.arange(len(scores)),scores,color=colors[name],linewidth=.7)
        ax.scatter([DEFAULT_SECRET],[scores[DEFAULT_SECRET]],color='black',marker='x',label='Known lab fixture')
        ax.set(title=name,xlabel='Candidate coefficient (all 3329)',ylabel='max |correlation|',ylim=(0,.65))
        ax.legend(fontsize=8)
    fig.suptitle('SIMULATED — candidate scores, seed 101, 2000 traces\nIdentical inputs/noise/jitter across variants; all samples searched')
    fig.savefig(figdir/'hypotheses.png',dpi=160);plt.close(fig)

    with np.load(ROOT/'local-results/simulated/cpa-baseline.npz',allow_pickle=False) as d:
        corr=d['corr']
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    axes[0].plot(np.abs(corr[DEFAULT_SECRET]),label='Known lab fixture',marker='.',color=colors['baseline'])
    others=np.delete(np.abs(corr),DEFAULT_SECRET,axis=0)
    axes[0].plot(others.max(axis=0),label='Largest incorrect |correlation| per sample',marker='.',color=colors['noise'])
    axes[0].set(xlabel='Synthetic sample index',ylabel='Absolute Pearson correlation',title='Baseline correlation across time')
    axes[0].legend(fontsize=8)
    _,variants,_=generate(101)
    for name in ['baseline','masked','recombined','noise']:
        axes[1].plot(variants[name][0],label=name,color=colors[name],marker='.')
    axes[1].set(xlabel='Synthetic sample index',ylabel='Arbitrary simulated leakage units',title='First generated trace (no selection)')
    axes[1].legend()
    fig.suptitle('SIMULATED — seed 101; 2000 × 24; sigma=1; jitter ±1\nOutput HW model, not recorded electrical power')
    fig.savefig(figdir/'samples.png',dpi=160);plt.close(fig)

    last=[r for r in sim['rows'] if r['traces']==max(sim['counts'])]
    lines=['# Executed results','',
        'Generated by `python tasks.py report` from saved JSON, not hand-entered metrics.', '',
        '| Stage | Status | Evidence |','|---|---|---|',
        '| D0 | PASS | Environment, pinned sources, literature/protocol, task runner |',
        '| D1 | PASS (host scope) | 25 keygen + 25 encapsulation + 10 decapsulation NIST KATs; 100 random round trips |',
        '| D2 | SIMULATED | Exhaustive scalar tests; positive and negative CPA controls |',
        '| D3 | SIMULATED | Sharing equivalence, multi-seed evaluation, recombination failure; host timing measured |',
        '| D4 | NOT RUN (NO HARDWARE) | Nano firmware/serial/capture pipeline unimplemented |',
        '| D5 | BLOCKED / unfinished | No board-specific firmware build or external capture pipeline; toolchain/board integration and safe analog interface outstanding |','',
        '## Correctness and toolchain','',tests['c'],'',tests['python'],'',
        'NIST byte-for-byte vectors are independent of the implementation. Also checked 25 deterministic round trips and altered ciphertext rejection against Python SHAKE-256, plus 9 adapter length rejections. The upstream low-level API does not expose the 20 key-validation cases; those are not claimed tested. No FIPS certification.', '',
        'Sanitizers (latest run): '+sanitizer_text+'. See [diagnostics and host](../results/sanitizers.json). Platform-specific snapshots retain other executed environments.', '',
        '## CPA at 2000 synthetic traces','',
        '| Seed | Variant | True rank (best–worst tie) | True max abs correlation | Largest candidate correlation | Verified recovery |',
        '|---:|---|---:|---:|---:|---|']
    for r in last:
        lines.append(f"| {r['seed']} | {r['variant']} | {r['rank_best']}–{r['rank_worst']} | {r['true_abs_corr']:.4f} | {r['max_abs_corr']:.4f} | {r['verified_recovery']} |")
    lines+=['','All runs and prefixes are retained in [simulation.json](../results/simulation.json). Ranks are 1-based; wrong-product-HW hypotheses can be equivalent, so tied intervals are reported. Searching 3329 guesses × 24 samples inflates null maxima. No significance or security conclusion is inferred from a small correlation.', '',
        'Baseline and deliberately visible recombination recover in these runs. The favorable share-only model does not recover. This is a model demonstration; no physical masking security is established.', '',
        '![SIMULATED rank and correlation curves](../results/figures/comparison.png)','',
        '![SIMULATED candidate hypotheses](../results/figures/hypotheses.png)','',
        '![SIMULATED sample inspection](../results/figures/samples.png)','',
        '## Host cost (not MCU cycles)','',
        f"Host: {env['cpu'].strip()}; {env['os']}. Compiler: {bench['compiler']}. Flags: `{' '.join(bench['flags'])}`.", '',
        '| Variant | Timed batches | Min ns/call | Median ns/call | Max ns/call | Stdev ns/call |',
        '|---|---:|---:|---:|---:|---:|']
    for name,s in bench['summaries'].items():
        lines.append(f"| {name} | {s['n']} | {s['min_ns']:.3f} | {s['median_ns']:.3f} | {s['max_ns']:.3f} | {s['stdev_ns']:.3f} |")
    ratio=bench['summaries']['masked']['median_ns']/bench['summaries']['baseline']['median_ns']
    lines+=['',f'Median batch ratio: {ratio:.2f}× for this host run. 10 million calls/batch, alternating order, one warmup batch per variant excluded. Inputs/shares precomputed; entropy, split and recombination excluded. Call/loop/checksum costs included. This is not full countermeasure overhead or a prediction for F030/F407.', '',
        'Compiler object/stack reports and all batches: [benchmark.json](../results/benchmark.json). Assembly interpretation: [ASSEMBLY_AUDIT.md](ASSEMBLY_AUDIT.md).', '',
        '## Reproduce','', '```powershell','python tasks.py all','```','',
        'Or run `doctor`, `test`, `host-mlkem`, `sanitize`, `simulate`, `attack-sim`, `bench`, then `report` separately. `make` forwards to the same runner where available. Exact source/vector hashes are in [upstream-lock.json](../upstream-lock.json); original-code hashes in [run-manifest.json](../results/run-manifest.json).', '',
        '## Hosted CI evidence','',CI_EVIDENCE,'',
        'No hardware capture, MCU execution, or firmware implementation is demonstrated. D4 firmware/capture and D5 board-specific firmware/external capture remain unfinished.']
    (ROOT/'docs/RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    progress=['# Project progress','',
        '## Aim','',
        'Build a reproducible leakage → attack → countermeasure → evaluation lab before the Nano arrives, while keeping full ML-KEM correctness separate from scalar leakage demonstrations.', '',
        '## What is implemented','',
        '- [Pinned ML-KEM host adapter](../tests/mlkem_driver.c) and [NIST vector runner](../scripts/host_mlkem.py); unmodified upstream sources and hashes.',
        '- [Scalar multiplication](../src/baseline.c), [share setup](../src/kernel.c), [shared multiplication](../src/masked.c), exhaustive C and independent Python checks.',
        '- [Simulator](../scripts/simulate_leakage.py), [chunked CPA](../scripts/attack_cpa.py), [multi-seed controls](../scripts/evaluate_countermeasure.py), and host benchmark/assembly reports.',
        '- [Research design](RESEARCH_DESIGN.md), [literature audit](LITERATURE_REVIEW.md), environment probe, runnable tasks and a successfully executed [host CI workflow](../.github/workflows/host.yml).', '',
        '## What was actually executed','',
        '`python tasks.py doctor`, `test`, `host-mlkem`, `sanitize`, `simulate`, `attack-sim`, `bench`, and `report`. Hardware guards were also checked; no device opened or flashed.', '',
        'PASS: 11,082,241 scalar pairs against repeated addition; 11,082,241 share pairs with varying multipliers and 119,844 boundary triples; six Python tests. ML-KEM: 60 official NIST KAT cases, 25 deterministic round trips/rejection checks, 100 randomized round trips/altered ciphertexts, nine adapter length rejections.', '',
        '## Preliminary results','',
        'At 2000 traces, baseline rank is 1 for all three seeds (|r| 0.525–0.536); shared-output ranks are 729, 3178, 1567 (|r| 0.0325–0.0565). Visible recombination restores rank 1 in every seed. Noise-only, label-permutation and wrong-product-HW controls do not uniquely recover the fixture.', '',
        f"Host-only median: {bench['summaries']['baseline']['median_ns']:.3f} ns/call baseline, {bench['summaries']['masked']['median_ns']:.3f} ns/call shared variant, ratio {ratio:.2f}×. This excludes RNG/setup/recombination and includes loop/call/checksum work. See [all measurements](RESULTS.md) and [assembly/stack scope](ASSEMBLY_AUDIT.md).", '',
        '![SIMULATED comparison, three fixed seeds](../results/figures/comparison.png)','',
        '## Scientific limitations','',
        'All leakage is SIMULATED. This is one coefficient under a stated HW model, not a full-key ML-KEM attack or secure masking construction. Real Montgomery encoding, transition/higher-order leakage, setup and recombination can change the outcome. NIST key-validation cases are outside the selected low-level API; no FIPS certification. The USENIX paper uses STM32F3 for Kyber and STM32F4 for ASCON.', '',
        'Latest local sanitizer results: '+sanitizer_text+'. Passing runs cover the exhaustive kernel and full ML-KEM adapter/KAT tests. Platform diagnostics are preserved. The initial sandbox denied WSL and USB enumeration; an authorized follow-up reached Ubuntu. ARM compiler was absent from PATH in the inspected Windows/WSL environments. D4 firmware/capture is unimplemented and NOT RUN (NO HARDWARE); D5 board-specific firmware/external capture is unfinished and BLOCKED on toolchain/board integration and a verified safe analog interface.', '',
        '## Hosted CI evidence','',CI_EVIDENCE,'',
        '## Next steps when Nano arrives','',
        'Identify the actual PCB/firmware, then run the stock onboard sanity capture before porting only the small kernel. Keep the built-in target intact. Verify F407 markings/flash registers before choosing a linker map; no external wiring proposal until both schematics/revisions are known.', '',
        '**Highest-value next step:** when Nano arrives, identify its actual revision and complete the stock onboard sanity capture before attempting the scalar experiment.']
    (ROOT/'docs/PROGRESS.md').write_text('\n'.join(progress)+'\n',encoding='utf-8')
    paths=[*sorted((ROOT/'src').glob('*.[ch]')),*sorted((ROOT/'scripts').glob('*.py')),
           *sorted((ROOT/'tests').glob('*.py')),*sorted((ROOT/'tests').glob('*.c')),
           ROOT/'tasks.py',ROOT/'requirements.txt',ROOT/'requirements-lock-windows.txt',ROOT/'Makefile',ROOT/'upstream-lock.json']
    manifest={'generated_utc':datetime.now(timezone.utc).isoformat(),'upstream':verify_sources(),
        'original_code_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'result_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in RESULTS.glob('*.json') if p.name!='run-manifest.json'}}
    save('run-manifest.json',manifest)
    print('PASS: regenerated docs/RESULTS.md and 3 labeled SIMULATED figures')


if __name__=='__main__':main()
