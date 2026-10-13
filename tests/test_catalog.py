#!/usr/bin/env python3
"""Guard editable/live coverage, defaults, packing and absence of legacy data."""
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import content
import generate_cv4 as gen
import pack_v2
import topology
import cv4_ops
from content import exams

def main():
    subjects, circuits, catalog = content.load()
    bank, rows, stats = gen.process_all()
    total = 374 + len(exams.EXERCISES)
    assert subjects and len(rows) == len(catalog) == total
    assert len({r['id'] for r in rows}) == total
    for chapter, count in ((9,93),(10,96),(11,98),(12,87)):
        assert sum(r['id'].startswith('p%d_' % chapter) for r in rows) == count
    for r in rows:
        d=r['data']; tid=d['template_id']
        t=bank.templates[tid] if tid is not None else {'comps':[]}
        assert t['comps'] or d['params'], r['id']
        assert d.get('live') or d['content_id'] in range(9), r['id']
        assert not d['tail'], (r['id'], 'frozen answer forbidden')
        assert len(d['params'])<=64 and len({n for n,v in d['params']})==len(d['params'])
        assert all(len(n)<=12 and math.isfinite(v) for n,v in d['params'])
        assert len(t['comps'])<=16, r['id']
        if t['comps']:
            assert all(0<=c['na']<t['n_nodes'] and 0<=c['nb']<t['n_nodes'] for c in t['comps'])
        if d.get('live'):
            assert d.get('live_spec') and len(d['live'])<65536
    assert cv4_ops.solve_nodes('vsrc_v',True,1,2)==(2,1)
    assert topology.derive_topology(circuits['p10_26'],'p10_26')['n_nodes']==4
    ids={r['id']:r['data']['template_id'] for r in rows}
    assert ids['p9_35']!=ids['p9_37'], 'distinct defaults cannot merge by geometry'
    payloads,placement=gen.pack_chunks(bank,rows)
    assert len(placement)==total
    packed=0
    for p in payloads:
        assert len(p)<60000 and p[:6]==b'CV4A\x02\x03'
        nt,ne=pack_v2.sim_parse_chunk(p);packed+=ne
        assert not any(marker in p for marker in (b'CV3A',b'Prova01',b'Rec01',b'p1_q'))
    assert packed==total
    saved=sorted((ROOT/'bin').glob('CV4DAT*.bin'))
    assert [p.read_bytes() for p in saved]==payloads, 'regenerate catalog first'
    print('CATALOG OK:',packed,'live/editable;',len(bank.templates),'templates;',
          len(payloads),'AppVars v2r3;',sum(len(r['data']['params']) for r in rows),'parameters')
if __name__=='__main__':main()
