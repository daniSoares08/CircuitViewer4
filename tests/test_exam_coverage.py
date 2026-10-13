"""Authorized source coverage, aliases, numerical routes and provenance."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import content
from content import exams

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--complete',action='store_true')
    args=parser.parse_args()
    subjects,circuits,items=content.load()
    by_id={x['id']:x for x in items}
    seen=set()
    for o in exams.OCCURRENCES:
        pair=(o['document'],o['question'])
        assert pair not in seen,pair
        seen.add(pair)
        filename,total=exams.DOCUMENTS[o['document']]
        assert (ROOT/'PROVAS/NOVAS_PROVAS'/filename).is_file(),filename
        assert 1<=o['question']<=total and o['pdf_page']>=1,o
        assert o['id'] in by_id,o
        assert by_id[o['id']]['priority']<0,o
    for ex in exams.EXERCISES:
        assert ex['live_recipe'] and (ex['params'] or ex['id'] in circuits),ex['id']
        assert ex['exam_anchors'],'No independent default reference: '+ex['id']
        keys={s[0] for s in ex['live_recipe']['steps']}
        assert set(ex['exam_anchors'])<=keys,ex['id']
        assert len(ex['title'])<=37 and ex['subject'] in subjects
    if args.complete:
        expected={(doc,q) for doc,(_,n) in exams.DOCUMENTS.items() for q in range(1,n+1)}
        assert seen==expected,('Missing',sorted(expected-seen))
    expected_books={'9.35','9.37','9.43','9.44','9.56','10.1','10.7','10.26',
        '11.1','11.8','11.15','11.38','11.41','11.53','11.69','12.7','12.14','12.25'}
    assert {ref['problem'] for ref in exams.BOOK_REFERENCES}==expected_books
    assert len(exams.BOOK_REFERENCES)==18
    for ref in exams.BOOK_REFERENCES:
        assert ref['document']=='L25' and ref['pdf_page']==1
        expected=['p11_41a','p11_41b'] if ref['problem']=='11.41' else ['p'+ref['problem'].replace('.','_')]
        assert ref['ids']==expected
        for key in ref['ids']:
            assert key in by_id and by_id[key]['priority']<0,(ref,key)
    print('EXAM COVERAGE:',len(seen),'of',sum(n for _,n in exams.DOCUMENTS.values()),
        'occurrences;',len(exams.EXERCISES),'new canonical entries; 18 book references')

if __name__=='__main__':main()
