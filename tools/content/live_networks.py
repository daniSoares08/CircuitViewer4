"""Runtime recipes for editable electrical figures, not static answer text."""
from content.live_solutions import recipe, power_summary

def node_at(topo,point):
    return next(k for k,points in topo['node_coord'].items() if point in points)

def opamp_constraints(ops,topo):
    result=[]
    for op in ops:
        if op[0]!='opamp':continue
        _,x,y,noninv=op
        top=node_at(topo,(x,y+13));bottom=node_at(topo,(x,y+37))
        result.append((node_at(topo,(x+62,y+29)),top if noninv else bottom,bottom if noninv else top))
    return result

def network_recipe(ex,template,topo,ops,cid):
    comps=template['comps'];key=ex['id'];ch=int(key.split('_')[0][1:])
    target=ex.get('engine',{}).get('target',255)
    rows=[];options={'flags':1,'opamps':opamp_constraints(ops,topo)}
    if key=='p11_95':
        return recipe(('w0','1/sqrt(c2*c4)','rad/s','Maximo: w0=1/sqrt(LC)'),
            ('f0','w0/(2*3.141592653589793)','Hz','f0=w0/(2pi)'),
            ('Z','z1+z2+z3+z4','ohm','Ztotal=Rfonte+ZC+Rcarga+ZL'),
            ('I','c0/Z','A','I=Vs/Ztotal',2),('Pcarga','abs(I)**2*c3','W','Pcarga=|I|^2 Rcarga'),
            ('Pmax','abs(c0)**2*c3/(c1+c3)**2','W','Em w0, ZC+ZL=0'))
    pa,pb=template['port_a'],template['port_b']
    if cid in (0,4,6):
        if pa==255 or pb==255:raise ValueError(key+': no live port')
        options.update(flags=2,port_a=pa,port_b=pb)
        if cid==6 and key in ('p11_14','p11_16','p11_18','p11_19','p11_20'):
            options['remove']=max(k for k,c in enumerate(comps) if c['kind'] in (0,3,4,8))
        rows += [('Zth','zth','ohm','Anule fontes; teste 1 A no porto'),
                 ('Vth','vth','V','Circuito aberto: Vth=Va-Vb',2)]
        if cid==0:rows += [('Yent','1/Zth','S','Yent=1/Zent')]
        if cid==4:rows += [('In','Vth/Zth','A','Norton: In=Vth/Zth',2)]
        if cid==6:
            real_load=key in ('p11_19','p11_20','p11_21')
            zload='abs(Zth)' if real_load else 'conj(Zth)'
            rows += [('ZLopt',zload,'ohm','RL=|Zth|' if real_load else 'ZLopt=conj(Zth)'),
                     ('ILopt','Vth/(Zth+ZLopt)','A','ILopt=Vth/(Zth+ZLopt)',2),
                     ('Pmax','abs(ILopt)**2*real(ZLopt)'+('/2' if template['flags2']&1 else ''),'W','Pmax=|ILpico|^2 RLopt/2' if template['flags2']&1 else 'Pmax=|ILrms|^2 RLopt')]
            if 'remove' in options:
                k=options['remove']
                rows += [('ILatual','Vth/(Zth+z%d)'%k,'A','ILatual=Vth/(Zth+ZL atual)',2),
                    ('PLatual','abs(ILatual)**2*real(z%d)'%k+('/2' if template['flags2']&1 else ''),'W','PLatual=|ILatual|^2 Re(ZL)')]
        return recipe(*rows,**options)
    # Display actual impedance substitutions before the solved quantities.
    for k,c in enumerate(comps):
        if c['kind'] in (3,4):rows.append(('Z%d'%k,'z%d'%k,'ohm','ZC=1/(jwC)' if c['kind']==3 else 'ZL=jwL'))
    for k in range(1,topo['n_nodes']):
        rows.append(('V%d'%k,'v%d'%k,'V','KCL: soma Y(Vno-Vviz)=Ifonte' if k==1 else '',2))
    for k,c in enumerate(comps):
        if c['kind'] in (7,):continue
        if k!=target and ch!=12 and c['kind'] not in (0,3,4,8):continue
        rows.append(('I%d'%k,'i%d'%k,'A','Ik: sentido na -> nb',2))
    if target<len(comps) and comps[target]['kind']!=7:
        c=comps[target];unit='V' if template['flags2']&2 else 'A'
        expr='v%d-v%d'%(c['na'],c['nb']) if unit=='V' else 'i%d'%target
        rows.append(('Alvo',expr,unit,'Alvo: tensao/corrente indicada',2))
    if options['opamps']:
        rows.append(('Vo','v%d'%options['opamps'][-1][0],'V','AOP ideal: V+=V-, I+=I-=0',2))
        src=next((k for k,c in enumerate(comps) if c['kind']==1),None)
        if src is not None:rows.append(('H','Vo/c%d'%src,'','H=Vo/Vs',2))
    if ch in (11,12):
        peak=bool(template['flags2']&1)
        if ch==11:
            for k,c in enumerate(comps):
                if c['kind'] in (1,2,5,6):
                    rows.append(('Sfonte%d'%k,'-s%d'%k+('/2' if peak else ''),'VA','Sfornecida=-V conj(I)'+('/2' if peak else '')))
        for k,c in enumerate(comps):
            if c['kind'] not in (0,3,4,8):continue
            rows.append(('S%d'%k,'s%d'%k+('/2' if peak else ''),'VA','Sk=Vk conj(Ik)'+('/2 (pico)' if peak else '')))
        terms=['s%d'%k for k,c in enumerate(comps) if c['kind'] in (0,3,4,8)]
        if terms:
            expr='+'.join(terms)
            rows += [('St','('+expr+')'+('/2' if peak else ''),'VA','St=soma das potencias absorvidas')]
            rows += power_summary('St')
    return recipe(*rows,**options)
