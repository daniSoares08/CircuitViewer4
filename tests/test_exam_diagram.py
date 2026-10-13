"""Execute the actual Flash-loaded phasor drawing after parameter edits."""
import ctypes as C
import _ctypes
from contextlib import ExitStack
import tempfile
from pathlib import Path
from test_appvar_live import build_library, Exercise, ROOT
from test_live_recipes import Value
import generate_cv4 as gen

def main():
    bank,rows,_=gen.process_all();payloads,placements=gen.pack_chunks(bank,rows)
    for row,place in zip(rows,placements):row['placement']=place
    index=next(i for i,row in enumerate(rows) if row['id']=='e_l25_01')
    cases=[(4,-5),(-4,5),(4,0),(0,5),(0,0),(1e-9,-1e-9),(1e20,-1e20)]
    with tempfile.TemporaryDirectory(prefix='cv4-phasor-') as td, ExitStack() as stack:
        lib=C.CDLL(str(build_library(Path(td),rows,len(payloads),capture_wires=True)))
        stack.callback(_ctypes.FreeLibrary,lib._handle)
        lib.test_chunk.argtypes=[C.c_uint8,C.POINTER(C.c_ubyte),C.c_size_t]
        lib.exercise_load.argtypes=[C.c_uint16];lib.exercise_load.restype=C.POINTER(Exercise)
        lib.exercise_set_param.argtypes=[C.c_uint8,C.c_float]
        buffers=[(C.c_ubyte*len(p)).from_buffer_copy(p) for p in payloads]
        for i,b in enumerate(buffers):lib.test_chunk(i,b,len(b))
        lib.appvar_init()
        endpoints=[]
        for re,asin in cases:
            ex=lib.exercise_load(index)
            lib.exercise_set_param(0,re);lib.exercise_set_param(1,asin)
            n=next(i for i in range(ex.contents.count)
                if ex.contents.pages[i].title==b'Circuito')
            lib.exercise_set_page(n);lib.test_wire_clear()
            C.CFUNCTYPE(None)(ex.contents.pages[n].body)()
            wires=[tuple(lib.test_wire_value(i,j) for j in range(4))
                for i in range(lib.test_wire_count())]
            assert len(wires)==(5 if re or asin else 2),wires
            for x1,y1,x2,y2 in wires:
                assert 50<=x1<=270 and 60<=y1<=210 and 50<=x2<=270 and 60<=y2<=210,wires
            if re or asin:
                vector=wires[2];assert vector[:2]==(160,136)
                norm=max(abs(re)/86,abs(asin)/58)
                expected=(int(160+re/norm),int(136+asin/norm))
                assert all(abs(a-b)<=1 for a,b in zip(vector[2:],expected)),(vector,expected)
                endpoints.append(vector[2:])
        assert len(set(endpoints))>=4,'drawing stayed frozen after edits'
        # Same phase must be purely resistive, not spurious micro-VAR.
        row_index=next(i for i,row in enumerate(rows) if row['id']=='e_l25_28')
        q_index=next(i for i,s in enumerate(rows[row_index]['data']['live_spec']['steps']) if s[0]=='Q')
        lib.live_recipe_value.argtypes=[C.c_uint8,C.POINTER(Value)]
        lib.live_recipe_value.restype=C.c_bool
        lib.exercise_load(row_index);value=Value()
        assert lib.live_recipe_value(q_index,C.byref(value)) and value.re==0
        lib.exercise_set_param(1,-10)
        assert lib.live_recipe_value(q_index,C.byref(value)) and abs(value.re+41.67556264)<.001
        lib.exercise_set_param(1,-20)
        assert lib.live_recipe_value(q_index,C.byref(value)) and value.re==0
    print('LIVE PHASOR DIAGRAM OK: 7 cases, actual C drawing, bounded in every quadrant')
    print('WAVE POWER FLOAT OK: zero Q -> phase edit -> zero Q, actual C loader')

if __name__=='__main__':main()
