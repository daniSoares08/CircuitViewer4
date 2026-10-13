"""Compile restricted scalar/complex expressions into the portable Flash VM.

No Python evaluation occurs on the calculator. Angles of trig/polar operations
are degrees, omega remains rad/s. The compiler rejects unresolved inputs.
"""
import ast
import struct

OPS = {'add':20,'sub':21,'mul':22,'div':23,'neg':24,'pow':25,
       'abs':30,'arg':31,'real':32,'imag':33,'conj':34,'sqrt':35,
       'sin':36,'cos':37,'tan':38,'acos':39,'atan':40,'exp':41,'log':42,
       'polar':43,'complex':44,'min':45,'max':46,'csqrt':47,'solve':48,'guard':49}
REFS = {'p':2,'c':3,'z':4,'v':5,'i':6,'s':7,'r':8}
SPECIAL = {'omega':9,'vth':10,'zth':11}

def cstr(s):
    if '\0' in s: raise ValueError('NUL in live text')
    return s.encode('ascii')+b'\0'

def compile_expr(expr, params, variables):
    def walk(n):
        if isinstance(n, ast.Constant) and isinstance(n.value,(int,float)):
            return bytes([1])+struct.pack('<f',n.value)
        if isinstance(n, ast.Name):
            if n.id == 'pi':return bytes([1])+struct.pack('<f',3.141592653589793)
            if n.id in params:return bytes([2,params.index(n.id)])
            if n.id in variables:return bytes([8,variables.index(n.id)])
            if n.id in SPECIAL:return bytes([SPECIAL[n.id]])
            if len(n.id)>1 and n.id[0] in REFS and n.id[1:].isdigit():
                return bytes([REFS[n.id[0]],int(n.id[1:])])
            raise ValueError('unregistered live input: '+n.id)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op,ast.USub):
            return walk(n.operand)+bytes([24])
        if isinstance(n, ast.BinOp):
            op={ast.Add:20,ast.Sub:21,ast.Mult:22,ast.Div:23,ast.Pow:25}.get(type(n.op))
            if op is None:raise ValueError('unsupported operation')
            return walk(n.left)+walk(n.right)+bytes([op])
        if isinstance(n,ast.Compare) and len(n.ops)==1:
            if isinstance(n.ops[0],(ast.Gt,ast.GtE)):
                # Same VM operations: a>b is b<a, a>=b is b<=a.
                op=51 if isinstance(n.ops[0],ast.Gt) else 52
                return walk(n.comparators[0])+walk(n.left)+bytes([op])
            op={ast.Eq:50,ast.Lt:51,ast.LtE:52}.get(type(n.ops[0]))
            if op is None:raise ValueError('unsupported comparison')
            return walk(n.left)+walk(n.comparators[0])+bytes([op])
        if isinstance(n,ast.BoolOp) and isinstance(n.op,ast.And):
            return walk(n.values[0])+b''.join(walk(v)+bytes([53]) for v in n.values[1:])
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in OPS:
            arity=2 if n.func.id in ('polar','complex','min','max','solve') else 1
            if len(n.args)!=arity or n.keywords:raise ValueError('wrong function arity')
            return b''.join(walk(a) for a in n.args)+bytes([OPS[n.func.id]])
        raise ValueError('unsupported expression: '+ast.dump(n))
    code=walk(ast.parse(expr,mode='eval').body)
    pos=depth=peak=0
    binary={20,21,22,23,25,43,44,45,46,48,50,51,52,53}
    while pos<len(code):
        op=code[pos];pos+=1
        if op<20:
            depth+=1
            if op==1:pos+=4
            elif op not in (9,10,11):pos+=1
        elif op in binary:depth-=1
        if depth<1:raise ValueError('invalid expression stack')
        peak=max(peak,depth)
    if depth!=1 or peak>24:raise ValueError('expression exceeds runtime stack')
    return code

def compile_recipe(recipe,params,n_comps=16,n_nodes=9):
    steps=recipe['steps'];variables=[]
    if len(steps)>64:raise ValueError('more than 64 live variables')
    flags=recipe.get('flags',0);extras=recipe.get('opamps',[])
    if len(params)>64 or len(set(params))!=len(params):raise ValueError('invalid parameter bank')
    if len(extras)>4 or any(any(n>=n_nodes for n in nodes) for nodes in extras):raise ValueError('invalid opamp nodes')
    if flags&~3:raise ValueError('invalid recipe flags')
    rendered=sum((bool(s[4])+1) for s in steps if s[5])
    if not rendered or rendered>64:raise ValueError('resolution exceeds narration capacity')
    out=bytearray([flags,recipe.get('port_a',255),recipe.get('port_b',255),
                   recipe.get('remove',255),len(extras)])
    for output,plus,minus in extras:out+=bytes([output,plus,minus])
    out+=bytes([len(steps)])
    for key,label,expr,unit,formula,mode in steps:
        for name in (n.id for n in ast.walk(ast.parse(expr,mode='eval')) if isinstance(n,ast.Name)):
            if name in params or name in variables or name in SPECIAL or name=='pi':continue
            if len(name)>1 and name[0] in REFS and name[1:].isdigit():
                limit={'p':len(params),'c':n_comps,'z':n_comps,'v':n_nodes,'i':n_comps,'s':n_comps,'r':len(variables)}[name[0]]
                if int(name[1:])>=limit:raise ValueError('live reference outside data: '+name)
        code=compile_expr(expr,params,variables)
        for text,limit in ((label,34),(formula,37)):
            if len(text)>limit:raise ValueError('live text too wide: '+text)
        if len(unit)>8 or mode not in (0,1,2):raise ValueError('invalid live presentation')
        out+=cstr(label)+cstr(formula)+cstr(unit)+bytes([mode])+struct.pack('<H',len(code))+code
        if key in variables:raise ValueError('duplicate live variable '+key)
        variables.append(key)
    return bytes(out)

def step(key,expr,unit='',formula='',mode=1,label=None):
    return (key,label or key,expr,unit,formula,mode)
