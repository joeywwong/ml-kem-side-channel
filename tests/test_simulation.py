import numpy as np
from simulate_leakage import generate
from attack_cpa import cpa,summarize


def test_reproducibility_and_independent_seeds():
    a,t,m=generate(7,n=100)
    b,u,n=generate(7,n=100)
    assert m==n and m['status']=='SIMULATED'
    assert np.array_equal(a,b)
    for key in t: np.testing.assert_array_equal(t[key],u[key])
    assert not np.array_equal(a,generate(8,n=100)[0])


def test_unseen_secrets_recovery_and_controls():
    # Separate from report fixture and seeds; inference never receives the secret.
    for secret,seed in [(77,17),(2501,29)]:
        a,v,_=generate(seed,n=1200,secret=secret)
        def analyze(a,t,model='output_hw'):
            s,c=cpa(a,t,model)
            return summarize(s,c,secret)
        base=analyze(a,v['baseline'])
        assert base['verified_recovery']
        assert analyze(a,v['recombined'])['verified_recovery']
        for name in ['noise','masked']:
            ctrl=analyze(a,v[name])
            assert ctrl['true_abs_corr']<base['true_abs_corr']/2
            assert not ctrl['verified_recovery']
        perm=analyze(np.random.default_rng(seed+1).permutation(a),v['baseline'])
        assert perm['true_abs_corr']<base['true_abs_corr']/2
        wrong=analyze(a,v['baseline'],'product_hw')
        assert wrong['true_abs_corr']<base['true_abs_corr']
