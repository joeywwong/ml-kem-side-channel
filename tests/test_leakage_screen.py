import json
import numpy as np
import pytest
from leakage_screen import welch,load_screen
from pilot_capture import capture_pilot


def test_welch_matches_scalar_formula_and_detects_injected_mean():
    rng=np.random.default_rng(42);w=rng.normal(size=(400,30));g=np.arange(400)%2
    w[g==0,9]+=2
    t,r=welch(w,g);a=w[g==0,9];b=w[g==1,9]
    assert t[9]==pytest.approx((a.mean()-b.mean())/np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b)))
    assert abs(t[9])>4.5 and r['fixed_count']==200
    assert np.max(np.abs(t[np.arange(30)!=9]))<4.5


def test_invalid_screen_samples_and_metadata(tmp_path):
    t,r=welch(np.ones((10,4)),np.arange(10)%2)
    assert np.isnan(t).all() and r['invalid_samples']==4 and r['max_abs_t'] is None
    with pytest.raises(ValueError):welch(np.ones((10,4)),np.zeros(10))
    with pytest.raises(ValueError):welch(np.full((10,4),np.inf),np.arange(10)%2)
    path=tmp_path/'x.npz';np.savez(path,waves=np.ones((10,4)),groups=np.arange(10)%2,metadata=json.dumps({'status':'SIMULATED'}))
    with pytest.raises(ValueError):load_screen(path)


def test_pilot_order_validation_and_preserve_partial(tmp_path):
    events=[]
    class Scope:
        def arm(self):events.append('arm')
        def capture(self):events.append('capture');return False
        def get_last_trace(self):return np.arange(4)
    class Target:
        def prepare(self,c):events.append('prepare')
        def execute(self):events.append('execute')
        def read_and_verify(self,c):events.append('verify');return c==0
    meta=dict(firmware_sha256='test-only',target_revision='test-only',measurement_point='test-only',sample_rate_hz=1,trigger_window='test-only',hardware_review='APPROVED',status='INSTRUMENTED_DEVICE')
    # Mocks test ordering only: these artifacts are temporary fixtures, not measurements.
    with pytest.raises(RuntimeError):capture_pilot(Scope(),Target(),[0,1],tmp_path/'run',meta,4)
    report=json.loads((tmp_path/'run/pilot.json').read_text());assert report['outcome']=='FAILED' and report['captured']==1
    assert events[:5]==['prepare','arm','execute','capture','verify']
    assert (tmp_path/'run/partial.npz').exists()
    with pytest.raises(FileExistsError):capture_pilot(Scope(),Target(),[0],tmp_path/'run',meta,4)
    with pytest.raises(ValueError):capture_pilot(Scope(),Target(),[0],tmp_path/'bad',{},4)
