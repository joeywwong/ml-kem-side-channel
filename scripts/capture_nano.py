"""D4 guard, not a capture implementation. Hardware is not available yet."""
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
    print(json.dumps({'status':'NOT RUN (NO HARDWARE)','chipwhisperer':version,
        'reason':'D4 deferred: actual revision, stock sanity capture, firmware and explicit flashing authorization required. No device opened.'}))
    if not args.inspect_only: raise SystemExit(2)


if __name__=='__main__':main()
