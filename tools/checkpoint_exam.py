"""Validate one newly authored occurrence, build, then preserve its package.

Never deletes an older checkpoint. bin/ may be mid-build when interrupted;
releases/provas/<sequence>-<occurrence>/ remains the last approved package.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from content import exams

def run(*args):
    print('>', ' '.join(args), flush=True)
    subprocess.run(args,cwd=str(ROOT),check=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clean',action='store_true')
    args=parser.parse_args()
    item=exams.OCCURRENCES[-1]
    if args.clean:run('make','clean')
    run(sys.executable,'tools/generate_cv4.py')
    run(sys.executable,'tests/test_catalog.py')
    run(sys.executable,'tests/test_exam_coverage.py')
    run(sys.executable,'tests/test_all_editable_routes.py')
    if any(ex['id']=='e_l25_01' for ex in exams.EXERCISES):
        run(sys.executable,'tests/test_exam_diagram.py')
    run(sys.executable,'tools/render_catalog.py','--ids',item['id'])
    run('make')
    # Record intentional changes only after the tests and successful build.
    # No regeneration here: test_baseline.snapshot() would invalidate mtime.
    import test_baseline
    manifest={'exercises_c':test_baseline._sha(ROOT/'src/exercises.c')}
    for path in sorted((ROOT/'bin').glob('CV4DAT*.bin')):
        manifest[path.name]=test_baseline._sha(path)
        manifest[path.name+'.size']=path.stat().st_size
    (ROOT/'tests/baseline_manifest.json').write_text(json.dumps(manifest,indent=1,sort_keys=True)+'\n',encoding='ascii')
    destination=ROOT/'releases/provas'/('%03d-%s-q%02d'%(len(exams.OCCURRENCES),item['document'].lower(),item['question']))
    if destination.exists():
        n=2
        while destination.with_name(destination.name+'-r%d'%n).exists():n+=1
        destination=destination.with_name(destination.name+'-r%d'%n)
    destination.mkdir(parents=True)
    files=[ROOT/'bin/CIRCVIE4.8xp',*sorted((ROOT/'bin').glob('CV4DAT*.8xv'))]
    for source in files:shutil.copy2(str(source),str(destination/source.name))
    shutil.copy2(str(ROOT/'tools/content/exams.py'),str(destination/'exams.py'))
    report=dict(occurrences=len(exams.OCCURRENCES),new_entries=len(exams.EXERCISES),
        book_references=len(exams.BOOK_REFERENCES),
        item=item,package=str(destination),files={p.name:dict(bytes=p.stat().st_size,
        sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files},
        hardware_tested=False)
    (destination/'checkpoint.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    (ROOT/'.ai-tasks/exams-progress.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('CHECKPOINT APPROVED:',destination,flush=True)

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tests'))
    main()
