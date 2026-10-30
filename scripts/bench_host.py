"""Host wall time, compiler object size/stack; never MCU cycles or power."""
import csv
import hashlib
import io
import json
import os
import shutil
import statistics
from common import ROOT,BUILD,FLAGS,compile_c,kernel_sources,run,save


def main():
    exe=compile_c('bench', [ROOT/'tests/bench_kernel.c',*kernel_sources()],
                  [ROOT/'src'], ['-D_POSIX_C_SOURCE=200809L'])
    raw=run([exe,'20261030'],capture_output=True,text=True).stdout
    (BUILD/'bench.csv').write_text(raw)
    rows=list(csv.DictReader(io.StringIO(raw)))
    summaries={}
    for variant in ['baseline','masked']:
        # First observation per variant is warmup; retained in raw CSV but excluded.
        times=[1e9*float(r['seconds'])/int(r['iterations']) for r in rows if r['variant']==variant][1:]
        summaries[variant]={'n':len(times),'min_ns':min(times),'median_ns':statistics.median(times),
                            'max_ns':max(times),'stdev_ns':statistics.stdev(times)}
    cc=os.environ.get('CC','gcc')
    object_reports={}
    for src in kernel_sources():
        obj=BUILD/(src.stem+'.o')
        run([cc,*FLAGS,'-fstack-usage','-Isrc','-c',src,'-o',obj],capture_output=True)
        run([cc,*FLAGS,'-Isrc','-S',src,'-o',BUILD/(src.stem+'.s')],capture_output=True)
        report={"stack_usage":(BUILD/(src.stem+'.su')).read_text()}
        for tool,args in [('size',[]),('nm',['-S','--size-sort']),('objdump',['-d'])]:
            if shutil.which(tool):
                report[tool]=run([tool,*args,obj],capture_output=True,text=True).stdout
            else: report[tool]='NOT RUN: tool unavailable'
        (BUILD/(src.stem+'-disassembly.txt')).write_text(report['objdump'])
        object_reports[src.name]=report
    result={'status':'PASS','kind':'HOST TIMING','flags':FLAGS,'seed':20261030,
            'compiler':run([cc,'--version'],capture_output=True,text=True).stdout.splitlines()[0],
            'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),
            'measurement':'wall time, 10 million calls per batch; alternating order; first batch per variant excluded',
            'scope':'precomputed input/share arrays; excludes entropy, splitting, recombination; loop/call/checksum costs included; no MCU extrapolation',
            'summaries':summaries,'raw_batches':rows,'object_reports':object_reports}
    save('benchmark.json',result)
    print(json.dumps(summaries,indent=2))


if __name__=='__main__': main()
