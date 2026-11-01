"""Transport-independent pilot acquisition. No default device/wiring/flash action.

Supply a reviewed target adapter after the hardware gate is satisfied. Existing
STM32 validation firmware has no capture command protocol; it is not an adapter.
"""
from datetime import datetime,timezone
import json
from pathlib import Path
import numpy as np


def capture_pilot(scope, target, cases, output, metadata, samples):
    """target.prepare(case), target.execute(), target.read_and_verify(case).

    read_and_verify MUST independently check the returned operation result; it
    returns True only after validation. cases are public test-case identifiers.
    Caller owns connection lifecycle. The function never configures power or IO.
    """
    required=('firmware_sha256','target_revision','measurement_point','sample_rate_hz','trigger_window','hardware_review')
    if any(not metadata.get(k) for k in required) or metadata['hardware_review']!='APPROVED':
        raise ValueError('Hardware feasibility review and acquisition metadata required')
    if metadata.get('status') not in ('INSTRUMENTED_DEVICE','MEASURED_MLKEM'):
        raise ValueError('Physical acquisition status required')
    if not isinstance(samples,int) or not 2<=samples<=50000 or not cases:
        raise ValueError('Invalid pilot size')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    waves=[];accepted=[];failure=None
    try:
        for case in cases:
            target.prepare(case)  # all inputs transferred outside trigger
            scope.arm()
            target.execute()  # must return promptly; scope was armed first
            if scope.capture():raise TimeoutError('Scope timed out')
            if target.read_and_verify(case) is not True:raise ValueError('Target result verification failed')
            wave=np.asarray(scope.get_last_trace(),dtype=float)
            if wave.shape!=(samples,) or not np.isfinite(wave).all():raise ValueError('Invalid waveform')
            waves.append(wave.copy());accepted.append(case)
    except Exception as e:
        failure=type(e).__name__+': '+str(e)
    record={**metadata,'created_utc':datetime.now(timezone.utc).isoformat(),'requested':len(cases),
            'captured':len(waves),'outcome':'FAILED' if failure else 'COMPLETE','error':failure,'cases':accepted}
    if waves:
        with (out/('partial.npz' if failure else 'pilot.npz')).open('xb') as f:
            np.savez_compressed(f,waves=np.stack(waves),metadata=json.dumps(record))
    (out/'pilot.json').write_text(json.dumps(record,indent=2)+'\n')
    if failure:raise RuntimeError(failure)
    return record
