"""Probe ASan/UBSan separately, run real tests when the runtime is available."""
import json
import os
import platform
import subprocess
from common import ROOT,BUILD,compile_c,kernel_sources,build_mlkem,run,save
from host_mlkem import check_vectors


def main():
    BUILD.mkdir(exist_ok=True)
    probe=BUILD/'sanitizer_probe.c'
    probe.write_text('int main(void) { return 0; }\n')
    results={}
    host={'os':platform.platform(),'python':platform.python_version(),
          'compiler':run([os.environ.get('CC','gcc'),'--version'],capture_output=True,text=True).stdout.splitlines()[0]}
    failed=False
    for name in ['address','undefined']:
        flags=[f'-fsanitize={name}','-fno-sanitize-recover=all','-fno-omit-frame-pointer']
        try:
            exe=compile_c('probe-'+name,[probe],flags=flags)
            run([exe],capture_output=True)
        except subprocess.CalledProcessError as e:
            results[name]={'status':'NOT RUN','reason':'sanitizer compiler/runtime probe unavailable',
                           'diagnostic':(e.stderr or b'').decode(errors='replace')[-2500:]}
            continue
        try:
            kernel=compile_c('kernel-'+name,[ROOT/'tests/test_kernel.c',*kernel_sources()],[ROOT/'src'],flags)
            output=run([kernel],capture_output=True,text=True).stdout.strip()
            kem=check_vectors(build_mlkem(flags,'-'+name))
            results[name]={'status':'PASS','kernel':output,'mlkem':kem}
        except subprocess.CalledProcessError as e:
            failed=True
            results[name]={'status':'FAIL','diagnostic':str(e.stderr)}
        except AssertionError as e:
            failed=True
            results[name]={'status':'FAIL','diagnostic':repr(e)}
    for outcome in results.values(): outcome['host']=host
    save('sanitizers.json',results)
    save('sanitizers-'+platform.system().lower()+'.json',results)
    print(json.dumps(results,indent=2))
    if failed: raise SystemExit(1)


if __name__=='__main__':main()
