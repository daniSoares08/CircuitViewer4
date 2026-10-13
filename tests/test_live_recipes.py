"""Execute each live recipe in device float precision and compare every step.

The oracle uses Python complex/double and an independent complex nodal stamp.
Component, parameter, frequency, phase and source-polarity mutations are real
evaluations, never mere counts of available editor fields.
"""
import ctypes as C
import _ctypes
import cmath
import math
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import generate_cv4
from test_all_editable_routes import EditComp, component_array

class NStep(C.Structure):
    _fields_=[('text',C.c_char*40),('color',C.c_uint8)]
class Narration(C.Structure):
    _fields_=[('steps',NStep*64),('count',C.c_uint8),('impossible',C.c_bool),('reason',C.c_char*40)]
class Inputs(C.Structure):
    _fields_=[('comps',C.POINTER(EditComp)),('n_comps',C.c_uint8),('n_nodes',C.c_uint8),
              ('params',C.POINTER(C.c_float)),('n_params',C.c_uint8),('omega',C.c_float)]
class Value(C.Structure):
    _fields_=[('re',C.c_float),('im',C.c_float)]

# Fixed references derived from the scanned givens/KCL/integrals, independently
# of recipe expressions. These catch authoring mistakes, not just VM mistakes.
ANCHORS={
    'p9_49':{'Vs':-1-1j},'p9_51':{'Is':15-20j},
    'p9_52':{'Vi':4-6.92820323j},'p9_54':{'Vs':-6+6j},'p9_55':{'Z':2.8-16.4j},
    'p10_71':{'H':5.99950005-.049995j},'p10_73':{'H':-1j/3,'Zent':15000-15000j},
    'p10_75':{'H':-.125},'p10_79':{'Vo':32+16j},
    'p11_7':{'S6':160},'p11_9':{'P3':.0224264706},'p11_12':{'Pmax':4225.89466},
    'p11_22':{'Irms':math.sqrt(6)},'p11_25':{'Vrms':math.sqrt(32/3)},
    'p11_27':{'T':5,'Irms':5/math.sqrt(3)},'p11_28':{'P':64/15},
    'p11_29':{'P':3600,'T':20},'p11_30':{'Vrms':math.sqrt(7/6),'T':4},
    'p11_33':{'Irms':5/math.sqrt(3),'T':5},'p11_34':{'RMS':math.sqrt(20)},
    'p11_35':{'Vrms':math.sqrt(466.6666667)},
    'p11_52':{'S':4200-749.545417j},'p11_60':{'Vo':6000+3791.52561j},
    'p11_61':{'S':6614-277.138673j},'p11_62':{'Vs':120.0597324+.08203402j},
    'p11_63':{'S':43000+22986.893275j},'p11_64':{'Is':-16.21794872-10.25641026j},
    'p11_74':{'C':.00573743078},'p11_78':{'W':4.69046023},'p11_79':{'W':.05},
    'p11_80':{'W':1559.75031},'p11_90':{'Qc':968170.0494},
    'p11_92':{'S':80000+32915.02622j},'p11_93':{'S':7328.5+1196.375j},
    'p11_94':{'Saldo':17057.02829},
    'p12_66':{'W1':360,'W2':300,'W3':240,'P':900},
    'p12_71':{'W1':2590.68745,'W2':4807.712783},
    'p12_72':{'P':79753.84615},
    'p12_73':{'W1':2360.491898,'W2':-632.491898,'P':1728},
    'p12_74':{'P':576.8533333},
}

def network(comps,n_nodes,w,extras=(),mask=65535,remove=255,test_port=None):
    cs=[c for c in comps if c.kind!=7];kinds=[];ys=[];values=[]
    for index,c in enumerate(comps):
        if c.kind==7:continue
        value=complex(c.value,c.value_im)*(-1 if c.flags&1 else 1)
        kind=c.kind
        if index==remove:kind=2;value=0
        elif kind in (1,2) and not(mask&(1<<index)):value=0
        if kind in (0,3,4,8):
            z=complex(c.value,c.value_im) if kind in (0,8) else (complex(0,w*c.value) if kind==4 else (1/complex(0,w*c.value) if w*c.value else None))
            if z==0:kind=1;value=0;y=0
            elif z is None:y=0
            else:y=1/z
        else:y=0
        kinds.append(kind);ys.append(y);values.append(value)
    if test_port is not None:
        for i,k in enumerate(kinds):
            if k in (1,2):values[i]=0
    vids={i:n_nodes-1+k for k,i in enumerate(i for i,k in enumerate(kinds) if k in (1,5))}
    dim=n_nodes-1+len(vids)+len(extras)
    A=np.zeros((dim,dim),dtype=complex);b=np.zeros(dim,dtype=complex)
    def stamp(row,col,value):
        if row and col:A[row-1,col-1]+=value
    def rhs(row,value):
        if row:b[row-1]+=value
    def control(row,c,gain):
        if c.ctrl==255:
            stamp(row,c.ctrl_a,gain);stamp(row,c.ctrl_b,-gain)
        elif c.ctrl in vids:stamp(row,vids[c.ctrl]+1,gain)
        else:
            cc=cs[c.ctrl];stamp(row,cc.na,gain*ys[c.ctrl]);stamp(row,cc.nb,-gain*ys[c.ctrl])
    for i,c in enumerate(cs):
        k=kinds[i];v=values[i];y=ys[i]
        if k in (0,3,4,8):
            stamp(c.na,c.na,y);stamp(c.nb,c.nb,y);stamp(c.na,c.nb,-y);stamp(c.nb,c.na,-y)
        elif k==2:rhs(c.na,-v);rhs(c.nb,v)
        elif k in (1,5):
            row=vids[i]+1;stamp(row,c.na,1);stamp(row,c.nb,-1)
            stamp(c.na,row,1);stamp(c.nb,row,-1)
            if k==1:rhs(row,v)
            else:control(row,c,-v)
        elif k==6:control(c.na,c,v);control(c.nb,c,-v)
    for i,(out,plus,minus) in enumerate(extras):
        row=n_nodes+len(vids)+i
        stamp(row,plus,1);stamp(row,minus,-1);stamp(out,row,1)
    if test_port is not None:rhs(test_port[0],1);rhs(test_port[1],-1)
    x=np.linalg.solve(A,b);vs=[0]+list(x[:n_nodes-1]);currents=[]
    for i,c in enumerate(cs):
        if i in vids:cur=x[vids[i]]
        elif kinds[i] in (0,3,4,8):cur=(vs[c.na]-vs[c.nb])*ys[i]
        elif kinds[i]==2:cur=values[i]
        elif kinds[i]==6:
            if c.ctrl==255:cur=values[i]*(vs[c.ctrl_a]-vs[c.ctrl_b])
            elif c.ctrl in vids:cur=values[i]*x[vids[c.ctrl]]
            else:
                cc=cs[c.ctrl];cur=values[i]*(vs[cc.na]-vs[cc.nb])*ys[c.ctrl]
        else:cur=0
        currents.append(cur)
    return vs,currents

def oracle(spec,comps,params,nodes,w):
    env={'pi':math.pi,'omega':w,'complex':complex,'abs':abs,'min':min,'max':max,
         'real':lambda x:complex(x).real,'imag':lambda x:complex(x).imag,'conj':lambda x:complex(x).conjugate(),
         'arg':lambda x:math.degrees(cmath.phase(x)),'csqrt':cmath.sqrt,'sqrt':lambda x:math.sqrt(complex(x).real),
         'polar':lambda a,d:a*cmath.exp(1j*math.radians(d)),
         'sin':lambda d:math.sin(math.radians(d)),'cos':lambda d:math.cos(math.radians(d)),
         'tan':lambda d:math.tan(math.radians(d)),'acos':lambda x:math.degrees(math.acos(x)),
         'atan':lambda x:math.degrees(math.atan(x)),'exp':math.exp,'log':math.log,
         'guard':lambda x:1 if x else (_ for _ in ()).throw(ValueError('domain'))}
    def solve(wave,mask):
        vs,cs=network(comps,nodes,wave,spec.get('opamps',()),int(mask),spec.get('remove',255))
        for i,v in enumerate(vs):env['v%d'%i]=v
        for i,c in enumerate(comps):
            if c.kind==7:continue
            env['i%d'%i]=cs[i]
            env['s%d'%i]=(vs[c.na]-vs[c.nb])*cs[i].conjugate()
        return wave
    env['solve']=solve
    for i,c in enumerate(comps):
        env['c%d'%i]=complex(c.value,c.value_im)*(-1 if c.flags&1 else 1)
        if c.kind in (0,8):env['z%d'%i]=complex(c.value,c.value_im)
        elif c.kind==4:env['z%d'%i]=complex(0,w*c.value)
        elif c.kind==3 and w*c.value:env['z%d'%i]=1/complex(0,w*c.value)
    for i,(name,value) in enumerate(params):env[name]=env['p%d'%i]=value
    if spec.get('flags',0)&3:solve(w,65535)
    if spec.get('flags',0)&2:
        pa,pb=spec['port_a'],spec['port_b'];env['vth']=env['v%d'%pa]-env['v%d'%pb]
        vs,_=network(comps,nodes,w,spec.get('opamps',()),remove=spec.get('remove',255),test_port=(pa,pb))
        env['zth']=vs[pa]-vs[pb]
    result=[]
    for key,label,expr,unit,formula,mode in spec['steps']:
        v=eval(expr,{'__builtins__':{}},env);result.append(complex(v))
        if key not in dict(params):env[key]=v
    return result

def build_library(path):
    names=['mna.c','engine.c','fmt.c','narrate.c','live_recipe.c']
    subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-DMNA_FORCE_FLOAT','-shared','-I',str(ROOT/'src'),
                    *[str(ROOT/'src'/n) for n in names],'-lm','-o',str(path)],check=True)

def main():
    b,rows,_=generate_cv4.process_all();failures=[];runs=0;covered=0
    authored_by_id={ex['id']:ex for ex in generate_cv4.content.load()[2]}
    with tempfile.TemporaryDirectory(prefix='cv4-live-') as tmp:
        path=Path(tmp)/'live.dll';build_library(path);lib=C.CDLL(str(path))
        lib.live_recipe_run.argtypes=[C.POINTER(C.c_uint8),C.c_uint16,C.POINTER(Inputs),C.POINTER(Narration)]
        lib.live_recipe_run.restype=C.c_bool
        lib.live_recipe_value.argtypes=[C.c_uint8,C.POINTER(Value)];lib.live_recipe_value.restype=C.c_bool
        for row in rows:
            d=row['data'];spec=d.get('live_spec')
            if not spec:continue
            covered+=1;t=b.templates[d['template_id']] if d['template_id'] is not None else {'comps':[],'n_nodes':0,'omega':0}
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
            for label,variant in variants:
                comps=component_array(t);params=list(d['params']);w=t['omega']
                if variant:
                    kind,i=variant
                    if kind=='c':
                        if comps[i].value or comps[i].value_im:comps[i].value*=1.1;comps[i].value_im*=1.1
                        else:comps[i].value=0.1
                    elif kind=='flip':comps[i].flags^=1
                    elif kind=='phase':
                        v=complex(comps[i].value,comps[i].value_im)*cmath.exp(1j*0.17)
                        comps[i].value=v.real;comps[i].value_im=v.imag
                    elif kind=='phase180':
                        comps[i].value=-abs(complex(comps[i].value,comps[i].value_im))
                        comps[i].value_im=abs(comps[i].value)*1e-7
                    elif kind=='p':params[i]=(params[i][0],params[i][1]*1.1 if params[i][1] else 0.1)
                    elif kind=='w':w*=1.1
                pa=(C.c_float*len(params))(*[v for _,v in params]);inp=Inputs(comps,len(comps),t['n_nodes'],pa,len(params),w)
                code=(C.c_uint8*len(d['live'])).from_buffer_copy(d['live']);nar=Narration();runs+=1
                try:expected=oracle(spec,comps,[(n,float(pa[i])) for i,(n,_) in enumerate(params)],t['n_nodes'],float(inp.omega))
                except (ValueError,ZeroDivisionError,np.linalg.LinAlgError):expected=None
                ok=lib.live_recipe_run(code,len(code),C.byref(inp),C.byref(nar))
                if not ok:
                    if label=='default' or expected is not None:failures.append((row['id'],label,bytes(nar.reason).decode()))
                    continue
                if expected is None:failures.append((row['id'],label,'C accepted invalid domain'));continue
                for i,exp in enumerate(expected):
                    got=Value();assert lib.live_recipe_value(i,C.byref(got));actual=complex(got.re,got.im)
                    angular=spec['steps'][i][3]=='deg'
                    difference=abs(((actual.real-exp.real+180)%360)-180) if angular else abs(actual-exp)
                    # Absolute tolerance scales with surrounding voltages/power
                    # for near-zero cancellation at device float precision.
                    scale=max([1]+[abs(v) for v in expected])
                    if difference>max(5e-5,scale*2e-6,abs(exp)*0.002):
                        failures.append((row['id'],label,spec['steps'][i][0],actual,exp));break
                    anchors=authored_by_id[row['id']].get('exam_anchors',{}) or ANCHORS.get(row['id'],{})
                    anchor=anchors.get(spec['steps'][i][0]) if label=='default' else None
                    if anchor is not None and abs(actual-anchor)>max(2e-5,abs(anchor)*.001):
                        failures.append((row['id'],'book reference',spec['steps'][i][0],actual,anchor))
                if not nar.count or nar.count>=64:failures.append((row['id'],label,'empty/truncated resolution'))
        handle=lib._handle;del lib
        (_ctypes.FreeLibrary if sys.platform=='win32' else _ctypes.dlclose)(handle)
    for item in failures[:150]:print('FAIL',item)
    print('Live recipes:',covered,'runs:',runs,'failures:',len(failures))
    if failures:raise SystemExit(1)
if __name__=='__main__':main()
