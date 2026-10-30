import numpy as np
import pytest
from attack_cpa import cpa,summarize
from simulate_leakage import generate


def test_pearson_against_numpy_and_chunk_invariance():
    a,traces,_=generate(9,n=150,secret=171)
    scores,corr=cpa(a,traces['baseline'],chunk=333)
    s2,c2=cpa(a,traces['baseline'],chunk=47)
    np.testing.assert_allclose(corr,c2,atol=1e-12)
    h=np.array([int(x*171%3329).bit_count() for x in a])
    expected=np.corrcoef(h,traces['baseline'][:,6])[0,1]
    assert corr[171,6]==pytest.approx(expected,abs=1e-12)
    assert np.all(corr[0]==0)
    np.testing.assert_allclose(scores,s2,atol=1e-12)


def test_degenerate_and_invalid():
    s,c=cpa(np.ones(5,dtype=int),np.ones((5,3)))
    assert np.all(s==0) and summarize(s,c,123)['rank_worst']==3329
    for a,t in [(np.array([1,2]),np.zeros((2,3))),
                (np.array([1,2,3329]),np.zeros((3,3))),
                (np.array([1,2,3]),np.full((3,2),np.nan))]:
        with pytest.raises(ValueError): cpa(a,t)
