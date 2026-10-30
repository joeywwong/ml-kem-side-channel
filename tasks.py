"""Portable equivalent of make. Run: python tasks.py help"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from common import compile_c,kernel_sources,run,save

TASKS={'doctor':'doctor.py','sanitize':'sanitize.py','simulate':'simulate_leakage.py',
       'attack-sim':'evaluate_countermeasure.py','report':'plot_results.py',
       'host-mlkem':'host_mlkem.py','bench':'bench_host.py','nano-capture':'capture_nano.py'}


def task(name):
    if name=='help':
        print('python tasks.py <task>\nTasks: '+', '.join(['help','test',*TASKS,'stm32-build','all']))
    elif name=='test':
        exe=compile_c('test-kernel',[ROOT/'tests/test_kernel.c',*kernel_sources()],[ROOT/'src'])
        output=run([exe],capture_output=True,text=True).stdout.strip()
        print(output,flush=True)
        p=run([sys.executable,'-m','pytest','-q'],capture_output=True,text=True)
        print(p.stdout,flush=True)
        save('tests.json',{'status':'PASS','c':output,'python':p.stdout.strip()})
    elif name=='stm32-build':
        import shutil
        reason='arm-none-eabi-gcc unavailable' if not shutil.which('arm-none-eabi-gcc') else 'board revision, flash capacity, startup and linker layout unverified'
        print('BLOCKED: '+reason+'; no firmware built or flashed')
        raise SystemExit(2)
    elif name=='all':
        for item in ['doctor','test','host-mlkem','sanitize','simulate','attack-sim','bench','report']: task(item)
    else:
        run([sys.executable,ROOT/'scripts'/TASKS[name]])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('task',choices=['help','test',*TASKS,'stm32-build','all'],nargs='?',default='help')
    args=p.parse_args()
    try: task(args.task)
    except subprocess.CalledProcessError as e:
        print('FAIL:',e,file=sys.stderr)
        if e.stdout: print(e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout,file=sys.stderr)
        if e.stderr: print(e.stderr.decode(errors='replace') if isinstance(e.stderr,bytes) else e.stderr,file=sys.stderr)
        raise SystemExit(1)
