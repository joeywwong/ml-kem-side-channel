"""Legacy D4 guard. External target interface is unverified; no device opened."""
import argparse
import importlib.metadata
import json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inspect-only',action='store_true')
    p.add_argument('--variant',choices=['baseline','masked'],default='baseline')
    p.add_argument('--samples',type=int,default=2000)
    p.add_argument('--traces',type=int,default=100)
    args=p.parse_args()
    if not 1<=args.samples<=50000 or args.traces<1: p.error('invalid Nano sample/trace count')
    try: version=importlib.metadata.version('chipwhisperer')
    except importlib.metadata.PackageNotFoundError: version='NOT INSTALLED'
    print(json.dumps({'status':'BLOCKED: EXTERNAL MEASUREMENT INTERFACE','chipwhisperer':version,
        'reason':'Nano onboard AES acquisition verified separately on 2026-11-01. ML-KEM needs reviewed analog wiring, GPIO trigger and target transport adapter. See docs/pqc_hardware_feasibility.md and scripts/pilot_capture.py. No device opened.'}))
    if not args.inspect_only: raise SystemExit(2)


if __name__=='__main__':main()
