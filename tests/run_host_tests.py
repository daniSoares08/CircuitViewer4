#!/usr/bin/env python3
"""Compile/run C regressions with warnings in double and device float."""
import subprocess
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    common=['mna.c','engine.c','narrate.c','narrate_ac.c','narrate_power.c','fmt.c','live_recipe.c']
    with tempfile.TemporaryDirectory(prefix='cv4-c-tests-') as td:
        for name in ('test_fmt','test_fmt_ac','test_mna','test_narrate_ac','test_new_catalog','test_editable_routes'):
            # Legacy MNA assertions intentionally use double/1e-9 tolerance.
            for precision in (['double'] if name=='test_mna' else ['double','float']):
                target=Path(td)/(name+'-'+precision+'.exe')
                cmd=['gcc','-std=c11','-Wall','-Wextra','-I',str(ROOT/'src')]
                if precision=='float':cmd+=['-DMNA_FORCE_FLOAT']
                cmd += [str(ROOT/'tests'/(name+'.c')),*[str(ROOT/'src'/n) for n in common],'-lm','-o',str(target)]
                subprocess.run(cmd,check=True)
                result=subprocess.run([str(target)],capture_output=True,text=True)
                print(name,precision,':',result.stdout.strip().splitlines()[-1])
                if result.returncode:
                    print(result.stdout,result.stderr);raise SystemExit(result.returncode)
    print('ALL HOST C REGRESSIONS OK')
if __name__=='__main__':main()
