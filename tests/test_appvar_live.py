#!/usr/bin/env python3
"""Actual C Flash loader -> editor APIs -> resolution AND result pages.

Host rendering is stubbed, never calculation or pagination. This test uses
the exact v2r3 chunks/compiled metadata and the same sources as CIRCVIE4.
"""
import ctypes as C
import _ctypes
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import generate_cv4 as gen
from test_all_editable_routes import EditComp

class Line(C.Structure):
    _fields_=[('text',C.c_char_p),('x',C.c_int),('y',C.c_int),('color',C.c_uint8)]
class Page(C.Structure):
    _fields_=[('title',C.c_char_p),('subtitle',C.c_char_p),('lines',C.POINTER(Line)),
             ('count',C.c_uint8),('result',C.c_char_p),('result_y',C.c_uint8),('body',C.c_void_p)]
class Exercise(C.Structure):
    _fields_=[('title',C.c_char_p),('pages',C.POINTER(Page)),('count',C.c_uint8)]

def build_library(temp,rows,chunk_count,capture_wires=False):
    gen.rec_chunk_count[0]=chunk_count
    (temp/'metadata.c').write_text(gen.generate_c(rows,gen.read_content_flags()),encoding='ascii')
    header=(ROOT/'src/cv3.h').read_text()
    declarations=re.findall(r'void\s+(?:draw_\w+|ui_\w+|prn)\s*\([^;]*?\);',header,re.S)
    stubs='\n'.join(s[:-1]+' {}' for s in declarations
        if not capture_wires or not re.match(r'void\s+draw_wire\s*\(',s))
    if capture_wires:stubs+='''
static int wire_values[4096][4];static unsigned wire_count;
void draw_wire(int x1,int y1,int x2,int y2){
 if(wire_count<4096){int *w=wire_values[wire_count++];w[0]=x1;w[1]=y1;w[2]=x2;w[3]=y2;}}
void test_wire_clear(void){wire_count=0;}
unsigned test_wire_count(void){return wire_count;}
int test_wire_value(unsigned i,unsigned j){return wire_values[i][j];}
'''
    (temp/'stubs.c').write_text('''#include "cv3.h"
#include "fileioc.h"
static unsigned char *data[8];static size_t sizes[8];
void test_chunk(unsigned char k,unsigned char *p,size_t n){data[k]=p;sizes[k]=n;}
uint8_t ti_Open(const char *s,const char *mode){unsigned k=s[6]-'0';(void)mode;return k<8&&data[k]?k+1:0;}
void *ti_GetDataPtr(uint8_t h){return data[h-1];}
size_t ti_GetSize(uint8_t h){return sizes[h-1];}
void ti_Close(uint8_t h){(void)h;}
'''+stubs,encoding='ascii')
    names=['appvar.c','mna.c','engine.c','fmt.c','narrate.c','narrate_ac.c','narrate_power.c','live_recipe.c']
    target=temp/'appvar.dll'
    subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Wno-unused-parameter','-DMNA_FORCE_FLOAT','-shared',
        '-I',str(ROOT/'tests/host'),'-I',str(ROOT/'src'),*[str(ROOT/'src'/n) for n in names],
        str(temp/'metadata.c'),str(temp/'stubs.c'),'-lm','-o',str(target)],check=True)
    return target

def snapshot(lib,index):
    ptr=lib.exercise_load(index)
    if not ptr:raise AssertionError('loader rejected exercise %d'%index)
    return current(ptr)

def current(ptr):
    ex=ptr.contents
    assert 0<ex.count<=32,ex.count
    pages=[]
    for n in range(ex.count):
        p=ex.pages[n];title=p.title.decode();lines=[]
        assert p.count<=8,(title,p.count)
        for i in range(p.count):
            l=p.lines[i];s=l.text.decode()
            assert len(s)<=38,(title,'too wide',s)
            assert 0<=l.x and l.x+8*len(s)<=320 and 36<=l.y<=200,(title,s,l.x,l.y)
            assert not re.search(r'(?i)(?<![a-z])(nan|inf)(?![a-z])',s),(title,s)
            lines.append((s,l.color))
        pages.append(dict(title=title,subtitle=p.subtitle.decode(),lines=lines))
    res=[s for p in pages if p['title']=='Resolucao' for s,_ in p['lines']]
    results=[s for p in pages if p['title']=='Resultados atuais' for s,_ in p['lines']]
    assert res and results,(ex.title,pages)
    if any('IMPOSSIVEL' in s for s in res):return pages,False
    reds=[s for p in pages if p['title']=='Resolucao' for s,c in p['lines'] if c==5]
    assert set(reds)<=set(results),('result pagination lost values',reds,results)
    return pages,True

def main():
    bank,rows,_=gen.process_all();payloads,placement=gen.pack_chunks(bank,rows)
    for r,place in zip(rows,placement):r['placement']=place
    failures=[];runs=0;unchanged=[];dump=[]
    with tempfile.TemporaryDirectory(prefix='cv4-appvar-') as td:
        temp=Path(td);lib=C.CDLL(str(build_library(temp,rows,len(payloads))))
        lib.test_chunk.argtypes=[C.c_uint8,C.POINTER(C.c_ubyte),C.c_size_t]
        lib.exercise_load.argtypes=[C.c_uint16];lib.exercise_load.restype=C.POINTER(Exercise)
        lib.exercise_comp.argtypes=[C.c_uint8];lib.exercise_comp.restype=C.POINTER(EditComp)
        lib.exercise_set_param.argtypes=[C.c_uint8,C.c_float]
        lib.exercise_set_frequency.argtypes=[C.c_float]
        lib.appvar_available.restype=C.c_bool
        buffers=[(C.c_ubyte*len(p)).from_buffer_copy(p) for p in payloads]
        def restore_chunks():
            for i,b in enumerate(buffers):lib.test_chunk(i,b,len(b))
            lib.appvar_init();assert lib.appvar_available(),'valid catalog rejected'
        restore_chunks()
        for idx,row in enumerate(rows):
            d=row['data'];t=bank.templates[d['template_id']] if d['template_id'] is not None else {'comps':[],'omega':0}
            variants=[('default',None)]
            for i,c in enumerate(t['comps']):
                if c['kind']==7:continue
                variants.append(('component%d'%i,('c',i)))
                if c['kind'] in (1,2,5,6):variants.append(('flip%d'%i,('flip',i)))
                if c['kind'] in (1,2,8):variants.append(('phase%d'%i,('phase',i)))
            variants.extend(('param%d'%i,('p',i)) for i in range(len(d['params'])))
            dc_source={'p10_46':5,'p10_47':5,'p10_48':4}.get(row['id'])
            if dc_source is not None:variants.append(('DC phase 180',('phase180',dc_source)))
            if t['omega']>0:variants.append(('frequency',('w',0)))
            base=None
            for name,change in variants:
                try:
                    ptr=lib.exercise_load(idx);assert ptr
                    if change:
                        kind,i=change
                        if kind in ('c','flip','phase','phase180'):
                            c=lib.exercise_comp(i).contents
                            if kind=='flip':c.flags^=1
                            elif kind=='phase':
                                v=complex(c.value,c.value_im)*complex(math.cos(.17),math.sin(.17));c.value=v.real;c.value_im=v.imag
                            elif kind=='phase180':
                                c.value=-abs(complex(c.value,c.value_im));c.value_im=abs(c.value)*1e-7
                            elif c.value or c.value_im:c.value*=1.1;c.value_im*=1.1
                            else:c.value=.1
                            lib.exercise_apply_edit()
                        elif kind=='p':lib.exercise_set_param(i,d['params'][i][1]*1.1 if d['params'][i][1] else .1)
                        else:lib.exercise_set_frequency(t['omega']*1.1)
                    pages,valid=current(ptr);runs+=1
                    if name=='default':
                        assert valid,'default marked impossible'
                        base=pages;dump.append(dict(id=row['id'],pages=pages))
                    elif pages==base:unchanged.append((row['id'],name))
                    # Execute each page's draw function too: live label buffers
                    # and scalar window selection are part of the actual route.
                    for n in range(ptr.contents.count):
                        p=ptr.contents.pages[n];lib.exercise_set_page(n)
                        if p.body:C.CFUNCTYPE(None)(p.body)()
                except (AssertionError,UnicodeDecodeError) as err:failures.append((row['id'],name,str(err)))
        # Wrong revision, truncated transfers, corrupt counts and offsets are
        # rejected *before* ENTER can dereference Flash beyond the AppVar.
        original=payloads[0]
        bads=[original[:n] for n in (0,1,5,9,20,len(original)-1)]
        for pos in (5,6,8):
            bad=bytearray(original);bad[pos]=255;bads.append(bytes(bad))
        for bad in bads:
            b=(C.c_ubyte*max(1,len(bad)))();C.memmove(b,bad,len(bad))
            lib.test_chunk(0,b,len(bad));lib.appvar_init();assert not lib.appvar_available(),'accepted corrupt catalog'
        restore_chunks()
        # Invalid edits must replace ALL old answers with an explanatory error.
        invalid_cases=[('p11_52','p',1,1.2),('p10_24','all',0,0)]
        for exid,kind,i,value in invalid_cases:
            idx=next(j for j,r in enumerate(rows) if r['id']==exid)
            ptr=lib.exercise_load(idx)
            if kind=='all':
                for k in range(len(rows[idx]['data']['params'])):lib.exercise_set_param(k,0)
            else:lib.exercise_set_param(i,value)
            pages,valid=current(ptr)
            if valid:failures.append((exid,'invalid edit','invalid edit accepted'))
            if any(c==5 and 'IMPOSSIVEL' not in s for p in pages if p['title']=='Resolucao' for s,c in p['lines']):
                failures.append((exid,'invalid edit','old answers remain'))
        h=lib._handle;del lib
        (_ctypes.FreeLibrary if sys.platform=='win32' else _ctypes.dlclose)(h)
    out=ROOT/'tmp/live-qa';out.mkdir(parents=True,exist_ok=True)
    (out/'runtime-pages.json').write_text(json.dumps(dump,indent=2),encoding='utf8')
    (out/'unchanged-edits.json').write_text(json.dumps(unchanged,indent=2),encoding='utf8')
    for item in failures[:80]:print('FAIL',item)
    print('AppVar/editor:',len(rows),'exercises;',runs,'scenarios;',len(unchanged),'invariant/rounded edits;',len(failures),'failures')
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
