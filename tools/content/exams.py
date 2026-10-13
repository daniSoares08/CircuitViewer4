"""Only the eight PDFs explicitly authorized in PROVAS/NOVAS_PROVAS.

OCCURRENCES maps document questions to canonical entries. Exact repetitions
share an entry; changed givens or requested quantities are separate variants.
Append one verified item, validate and checkpoint before appending the next.
"""
from content.live_solutions import recipe, power_summary

DOCUMENTS = {
    'L25': ('Lista-de-exercicios_2025-1.pdf', 40),
    'R1A': ('P1-Rec_2025-05-15_versaoA_com-resolucao.pdf', 5),
    'P1B': ('P1_2025-05-07_versaoB_com-resolucao.pdf', 6),
    'R2A': ('P2-Rec_2025-06-25_versaoA_com-resolucao.pdf', 6),
    'P2A': ('P2_2025-06-18_versaoA_com-resolucao.pdf', 5),
    'P2B': ('P2_2025-06-18_versaoB_com-resolucao.pdf', 5),
    'P22': ('Prova2_2022-11_Voldi_CA_versaoA.pdf', 4),
    'T26': ('Teste1_2026_com-resposta-do-professor.pdf', 4),
}
SUBJECTS = []
CIRCUITS = {}
EXERCISES = []
OCCURRENCES = []
BOOK_REFERENCES = [dict(document='L25',pdf_page=1,problem=p,
    ids=['p11_41a','p11_41b'] if p=='11.41' else ['p'+p.replace('.','_')])
    for p in ('9.35','9.37','9.43','9.44','9.56','10.1','10.7','10.26',
              '11.1','11.8','11.15','11.38','11.41','11.53','11.69','12.7','12.14','12.25')]

def add(doc, number, page, subject, statement, params=(), live=None, ops=None,
        engine=None, anchors=None, notes=''):
    key='e_%s_%02d' % (doc.lower(), number)
    title='%s Q%d' % (doc, number)
    source='%s, PDF p.%d, Q%d' % (DOCUMENTS[doc][0], page, number)
    EXERCISES.append(dict(id=key,title=title,subject=subject,priority=0,
        source=source,statement=statement,params=list(params),live_recipe=live,
        engine=engine or {},exam_anchors=anchors or {},source_notes=notes))
    if ops is not None:CIRCUITS[key]=ops
    if subject not in SUBJECTS:SUBJECTS.append(subject)
    OCCURRENCES.append(dict(document=doc,question=number,pdf_page=page,id=key,notes=notes))
    return key

def alias(doc, number, page, key, notes='Identico ao exercicio canonico.'):
    OCCURRENCES.append(dict(document=doc,question=number,pdf_page=page,id=key,notes=notes))

def sinusoid(amplitude, omega, phase, sine=False, unit='V', time=.01):
    params=[('Amplitude',amplitude),('w_rad_s',omega),('phi_deg',phase),('t_s',time)]
    shift='-90' if sine else ''
    live=recipe(('dom','guard(w_rad_s>0)','','',0),
        ('X','polar(Amplitude,phi_deg%s)'%shift,unit,
        'sen(x)=cos(x-90deg)' if sine else 'Referencia fasorial: cosseno',2),
        ('A','abs(X)',unit,'Amplitude positiva=|X|'),
        ('fase','arg(X)','deg','Fase equivalente em cosseno'),
        ('w','w_rad_s','rad/s'),('f','w/(2*pi)','Hz','f=w/(2pi)'),
        ('T','2*pi/w','s','T=2pi/w'),
        ('x_t','A*cos(w*t_s*180/pi+fase)',unit,'x(t)=A cos(wt+fase)'))
    return params,live

def rated_load(voltage, apparent, pf, sign=1):
    params=[('S_VA',apparent),('FP',pf),('Q_sinal',sign)]
    live=recipe(('dom','guard(S_VA>=0 and FP>0 and FP<=1 and Q_sinal**2==1)','','',0),
        ('phi','Q_sinal*acos(FP)','deg','phi>0: atraso; phi<0: avanco'),
        ('S','polar(S_VA,phi)','VA','S=|S| /_ acos(FP)'),*power_summary(),
        ('I','conj(S/c0)','A','S=V conj(I) -> I=conj(S/V)',2),
        ('Ipico','sqrt(2)*abs(I)','A','Ipico=sqrt(2) Irms'),
        ('Z','c0/I','ohm','Z=Vrms/Irms (sem conjugado)'),
        ('Zpolar','Z','ohm','Carga vista pela fonte',2))
    ops=[('vsrc_v',40,90,195,'%gV'%voltage),('wire',40,90,265,90),
        ('wire',40,195,265,195),('term',265,90,'a'),('term',265,195,'b'),
        ('lbl','Carga nominal S/FP',104,135),('lbl','RMS',145,158),('gnd',40,195)]
    return params,live,ops,{'omega':1}

def motor(power, voltage, current):
    params=[('P_W',power),('VL_V',voltage),('IL_A',current)]
    live=recipe(('S','sqrt(3)*VL_V*IL_A','VA','|S|=sqrt(3) VL IL (RMS)'),
        ('FP','P_W/S','','FP=P/|S|'),
        ('dom','guard(FP>=0 and FP<=1)','','',0),
        ('phi','acos(FP)','deg','Motor indutivo: atraso'),
        ('Q','sqrt(S**2-P_W**2)','VAR','Q=sqrt(|S|^2-P^2)'))
    return params,live

def three_delta(vline, zlabel, phase=0):
    import math
    amp=vline/math.sqrt(3)
    ops=[('wire',32,90,32,196)]
    # Source registers are grouped first, followed by the three delta loads.
    for y,ang in ((90,phase-30),(143,phase-150),(196,phase+90)):
        ops += [('vsrc_h',32,y,85,'%.8g/_%gV'%(amp,ang)),('wire',85,y,190,y)]
    ops += [('imp_v',190,90,143,zlabel),('imp_v',190,143,196,zlabel),
        ('imp_v',285,90,196,zlabel),('wire',190,90,285,90),
        ('wire',190,196,285,196),('gnd',32,196)]
    live=recipe(('Vab','c0-c1','V','Fonte Y equivalente: Vab=Va-Vb',2),
        ('Vbc','c1-c2','V','Vbc=Vb-Vc',2),('Vca','c2-c0','V','Vca=Vc-Va',2),
        ('Iab','Vab/z3','A','Delta: Iab=Vab/Zab',2),
        ('Ibc','Vbc/z4','A','Ibc=Vbc/Zbc',2),('Ica','Vca/z5','A','Ica=Vca/Zca',2),
        ('Iac','-Ica','A','Ramo A -> C: Iac=-Ica',2),
        ('Ia','Iab-Ica','A','KCL: Ia=Iab-Ica',2),
        ('Ib','Ibc-Iab','A','Ib=Ibc-Iab',2),('Ic','Ica-Ibc','A','Ic=Ica-Ibc',2),
        ('S','Vab*conj(Iab)+Vbc*conj(Ibc)+Vca*conj(Ica)','VA','S=soma das potencias de fase'),
        *power_summary(),('check','guard(abs(Ia+i0)<max(abs(Ia),1e-30)*1e-3)','','',0),flags=1)
    return [],live,ops,{'omega':1}

def three_y(voltage, loads, sequence=1, phase=0):
    ops=[('wire',32,90,32,196),('wire',286,90,286,196)]
    for y,ang in ((90,phase),(143,phase-120*sequence),(196,phase+120*sequence)):
        ops += [('vsrc_h',32,y,85,'%g/_%gV'%(voltage,ang)),('wire',85,y,180,y)]
    for y,z in zip((90,143,196),loads):
        ops += [('imp_h',180,y,255,z),('wire',255,y,286,y)]
    ops += [('wire',32,196,32,214),('wire',32,214,286,214),('wire',286,196,286,214)]
    live=recipe(('Ia','c0/z3','A','Neutro ligado: Ia=Van/Za',2),
        ('Ib','c1/z4','A','Ib=Vbn/Zb',2),('Ic','c2/z5','A','Ic=Vcn/Zc',2),
        ('In','-(Ia+Ib+Ic)','A','In=-(Ia+Ib+Ic), N -> fonte',2),
        ('Sa','c0*conj(Ia)','VA','Sk=Vkn conj(Ik), RMS'),
        ('Sb','c1*conj(Ib)','VA'),('Sc','c2*conj(Ic)','VA'),
        ('S','Sa+Sb+Sc','VA','S=Sa+Sb+Sc'),*power_summary(),flags=1)
    return [],live,ops,{'omega':1}

def parallel_power(voltage, first_r=124):
    live=recipe(('S1','abs(c0)**2/conj(z1)','VA','Sk=|Vrms|^2/conj(Zk)'),
        ('S2','abs(c0)**2/conj(z2)','VA'),('S3','abs(c0)**2/conj(z3)','VA'),
        ('A1','abs(S1)','VA','Potencia aparente de cada ramo'),
        ('A2','abs(S2)','VA'),('A3','abs(S3)','VA'),
        ('S','S1+S2+S3','VA','Potencia complexa total: soma Sk'),
        *power_summary(),('phi','arg(S)','deg','Q<0: FP adiantado; nao negativo'))
    ops=[('vsrc_h',32,90,95,'%gV'%voltage),('res_h',110,90,260,str(first_r)),
        ('imp_h',110,143,260,'20-j25'),('imp_h',110,196,260,'90+j80'),
        ('wire',95,90,110,90),('wire',110,90,110,196),
        ('wire',260,90,286,90),('wire',260,143,286,143),('wire',260,196,286,196),
        ('wire',286,90,286,214),('wire',32,90,32,214),('wire',32,214,286,214),('gnd',32,214)]
    return [],live,ops,{'omega':1}

def wave_power(vamp, vphase, iamp, iphase, omega):
    params=[('Vp_V',vamp),('phiV_deg',vphase),('Ip_A',iamp),
        ('phiI_deg',iphase),('w_rad_s',omega),('t_s',.01)]
    live=recipe(('dom','guard(w_rad_s>0 and Vp_V>0 and Ip_A>0)','','',0),
        ('V','polar(Vp_V,phiV_deg)','V','Fasor de pico, referencia cosseno',2),
        ('I','polar(Ip_A,phiI_deg)','A','I entra no terminal positivo',2),
        ('Vrms','abs(V)/sqrt(2)','V','Vrms=Vpico/sqrt(2)'),
        ('Irms','abs(I)/sqrt(2)','A','Irms=Ipico/sqrt(2)'),
        ('Sraw','V*conj(I)/2','VA','',0),
        # Device float can invent micro-VAR for identical V/I phases.
        # Discard only relative sub-epsilon residues, never small SI values.
        ('S','complex(real(Sraw)*(abs(real(Sraw))>abs(Sraw)*1e-7)+0,imag(Sraw)*(abs(imag(Sraw))>abs(Sraw)*1e-7)+0)',
         'VA','Fasores de pico: S=V conj(I)/2'),
        *power_summary(),('phi','arg(S)','deg','phi=phiV-phiI; Q<0: avanco'),
        ('Z','abs(V)**2/(2*conj(S))','ohm','Z=V/I=Vp^2/(2 conj(S))',2),
        ('p_t','real(S)+abs(S)*cos(2*w_rad_s*t_s*180/pi+arg(V)+arg(I))','W',
         'p(t)=P+|S|cos(2wt+phiV+phiI)'))
    return params,live

def wave_load(vamp,vphase,iamp,iphase,omega):
    params,live=wave_power(vamp,vphase,iamp,iphase,omega)
    params=[p for p in params if p[0] not in ('Vp_V','phiV_deg','w_rad_s')]
    live['steps']=[(key,label,'c0' if key=='V' else expr.replace('w_rad_s','omega').replace('Vp_V','abs(c0)'),unit,formula,mode)
        for key,label,expr,unit,formula,mode in live['steps']]
    # Unknown equivalent load: ports, not an invented editable impedance.
    ops=[('vsrc_v',40,90,195,'%g/_%gV'%(vamp,vphase)),
        ('wire',40,90,265,90),('wire',40,195,265,195),
        ('term',265,90,'a'),('term',265,195,'b'),
        ('lbl','Carga: Z=V/I',116,137),('lbl','I entra em a',116,177),('gnd',40,195)]
    return params,live,ops,{'omega':omega,'peak':True}

def y_three_wire(voltage,zload,zline=None,phase=0):
    ops=[('wire',32,90,32,196),('wire',292,90,292,196)]
    ys=(90,143,196)
    for y,ang in zip(ys,(phase,phase-120,phase+120)):
        ops += [('vsrc_h',32,y,85,'%.8g/_%gV'%(voltage,ang)),
            ('wire',85,y,118 if zline else 212,y)]
    if zline:
        for y in ys:ops += [('imp_h',118,y,178,zline),('wire',178,y,212,y)]
    for y in ys:ops += [('imp_h',212,y,278,zload),('wire',278,y,292,y)]
    ops += [('gnd',32,196)]
    za,zb,zc=('z3+z6','z4+z7','z5+z8') if zline else ('z3','z4','z5')
    load=(6,7,8) if zline else (3,4,5)
    rows=[('Za',za,'ohm','Impedancia total do ramo A'),
        ('Zb',zb,'ohm','Impedancia total do ramo B'),('Zc',zc,'ohm','Impedancia total do ramo C'),
        ('Vn','(c0/Za+c1/Zb+c2/Zc)/(1/Za+1/Zb+1/Zc)','V','Neutro flutuante: KCL em N',2),
        ('Ia','(c0-Vn)/Za','A','Ia=(Va-Vn)/Za',2),
        ('Ib','(c1-Vn)/Zb','A','Ib=(Vb-Vn)/Zb',2),
        ('Ic','(c2-Vn)/Zc','A','Ic=(Vc-Vn)/Zc',2),
        ('IN','Ia+Ib+Ic','A','Tres fios: soma das correntes=0'),
        ('Scarga','z%d*abs(Ia)**2+z%d*abs(Ib)**2+z%d*abs(Ic)**2'%load,'VA','Scarga=soma Zk |Ik RMS|^2'),
        ('Pcarga','real(Scarga)','W','Potencia ativa na carga'),
        ('Qcarga','imag(Scarga)','VAR','Potencia reativa na carga')]
    if zline:rows += [('Slinha','z3*abs(Ia)**2+z4*abs(Ib)**2+z5*abs(Ic)**2','VA','Slinha=soma Zlinha |Ik RMS|^2'),
        ('Plinha','real(Slinha)','W'),('Qlinha','imag(Slinha)','VAR')]
    rows += [('S','c0*conj(Ia)+c1*conj(Ib)+c2*conj(Ic)','VA','Fonte: S=soma Vk conj(Ik)'),
        *power_summary(),('check','guard(abs(Ia+i0)<max(abs(Ia),1e-30)*1e-3 and abs(Ib+i1)<max(abs(Ib),1e-30)*1e-3 and abs(Ic+i2)<max(abs(Ic),1e-30)*1e-3)','','',0)]
    return [],recipe(*rows,flags=1),ops,{'omega':1}

def delta_with_lines(voltage,zline,zload,phase=0):
    ops=[('wire',32,90,32,196)]
    for y,ang in zip((90,143,196),(phase,phase-120,phase+120)):
        ops += [('vsrc_h',32,y,85,'%.8g/_%gV'%(voltage,ang)),('wire',85,y,115,y)]
    for y in (90,143,196):ops += [('imp_h',115,y,175,zline),('wire',175,y,190,y)]
    ops += [('imp_v',190,90,143,zload),('imp_v',190,143,196,zload),
        ('imp_v',285,90,196,zload),('wire',190,90,285,90),
        ('wire',190,196,285,196),('gnd',32,196)]
    live=recipe(('Iab','i6','A','KCL em A,B,C: solver nodal da rede',2),
        ('Ibc','i7','A','Ramo B -> C',2),('Ica','-i8','A','Ramo C -> A',2),
        ('Ia','Iab-Ica','A','Ia=Iab-Ica',2),('Ib','Ibc-Iab','A','Ib=Ibc-Iab',2),
        ('Ic','Ica-Ibc','A','Ic=Ica-Ibc',2),
        ('Vab','z6*Iab','V','Tensao na carga: Vab=Zab Iab',2),
        ('Vbc','z7*Ibc','V','Vbc=Zbc Ibc',2),('Vca','z8*Ica','V','Vca=Zca Ica',2),
        ('Scarga','s6+s7+s8','VA','Scarga=soma Vk conj(Ik) na delta'),
        ('Pcarga','real(Scarga)','W'),('Qcarga','imag(Scarga)','VAR'),
        ('Slinha','s3+s4+s5','VA','Slinha=soma Zlinha |Ik|^2'),
        ('S','-(s0+s1+s2)','VA','Sfornecida=Scarga+Slinha'),*power_summary(),flags=1)
    return [],live,ops,{'omega':1}

# Completed items: every addition has its own validated build checkpoint.
p,r=sinusoid(-180,377,30,True)
add('T26',1,1,'Impedancia AC',[
    'Converta v(t)=-180 sen(377t+30deg) V para fasor polar.',
    'Referencia: cosseno. Amplitude negativa equivale a somar 180deg.'
],p,r,anchors={'X':complex(-90,180*3**.5/2)})

add('T26',2,1,'Impedancia AC',[
    'Determine Yeq e Zeq em forma polar. Calcule as admitancias dos ramos.',
    'Ramos: 5-j2 ohm, 3+j1 ohm e -j4 ohm; todos em paralelo.'
],live=recipe(('Z1','z0+z1','ohm','R e reatancia em serie'),
    ('Z2','z2+z3','ohm'),('Z3','z4','ohm'),
    ('Y1','1/Z1','S','Admitancia de cada ramo: Yk=1/Zk'),
    ('Y2','1/Z2','S'),('Y3','1/Z3','S'),
    ('Yeq','Y1+Y2+Y3','S','Paralelo: Yeq=Y1+Y2+Y3',2),
    ('Zeq','1/Yeq','ohm','Zeq=1/Yeq',2)),ops=[
    ('term',40,85,'a'),('term',40,195,'b'),
    ('wire',40,85,270,85),('wire',40,195,270,195),
    ('res_v',95,85,140,'5'),('imp_v',95,140,195,'-j2'),
    ('res_v',175,85,140,'3'),('imp_v',175,140,195,'j1'),
    ('imp_v',270,85,195,'-j4'),('gnd',40,195)
],engine={'omega':1},anchors={'Zeq':1.742448330683625-0.807631160572337j})

add('T26',3,2,'Analise Nodal AC',[
    'Use analise nodal para Vo e Io (polar). Vs1=10 cos(t-45deg) V;',
    'Vs2=5 sen(t+30deg) V. R=3 ohm, L=1 H, C=1 F.',
    'Io aponta para baixo no capacitor. Fasores de pico em cosseno.'
],live=recipe(('V1','c0','V','V1=10/_-45; cosseno',2),
    ('V2','c3','V','Seno -> fase menos 90 graus',2),
    ('ZL','z2','ohm','ZL=jwL'),('ZC','z4','ohm','ZC=1/(jwC)'),
    ('Y','1/z1+1/ZL+1/ZC','S','KCL: (V1-Vo)/R+(V2-Vo)/ZL'),
    ('Vo','(V1/z1+V2/ZL)/Y','V','Vo=(V1/R+V2/ZL)/Y',2),
    ('Io','Vo/ZC','A','Io=Vo/ZC (para baixo)',2)),ops=[
    ('vsrc_v',40,90,195,'10/_-45V'),('res_h',40,90,150,'3'),
    ('ind_h',150,90,265,'1H'),('vsrc_v',265,90,195,'5/_-60V'),
    ('cap_v',150,90,195,'1F'),('wire',40,195,265,195),
    ('lbl','Vo',143,68),('arr_v',132,135,180,'Io',False),('gnd',150,195)
],engine={'omega':1},anchors={'Vo':-5.91931324490131-14.5710678118655j})

add('T26',4,3,'Thevenin AC',[
    'Determine Thevenin e Norton nos terminais a-b.',
    'Fonte=120/_45 V; R1=30, R2=60, ZL=j10, ZC=-j5 ohm.',
    'Porto a-b esta sobre ZC, que permanece no circuito.'
],live=recipe(('Zserie','z3+z4','ohm','Zserie=ZL+ZC'),
    ('Zp','1/(1/z2+1/Zserie)','ohm','Zp=R2||(ZL+ZC)'),
    ('Vtop','c0*Zp/(z1+Zp)','V','Divisor: Vtop=Vs Zp/(R1+Zp)',2),
    ('Vth','Vtop*z4/Zserie','V','Vth=Vtop ZC/(ZL+ZC)',2),
    ('Roff','1/(1/z1+1/z2)','ohm','Fonte V anulada: Roff=R1||R2'),
    ('Zth','1/(1/(Roff+z3)+1/z4)','ohm','Zth=(Roff+ZL)||ZC'),
    ('ZthPolar','Zth','ohm','Z Norton = Z Thevenin',2),
    ('In','Vth/Zth','A','In=Vth/Zth; sentido a -> b',2)),ops=[
    ('vsrc_v',40,85,195,'120/_45V'),('res_h',40,85,145,'30'),
    ('res_v',145,85,195,'60'),('wire',145,85,240,85),
    ('imp_v',240,85,140,'j10'),('imp_v',240,140,195,'-j5'),
    ('wire',40,195,285,195),('wire',240,140,285,140),
    ('term',285,140,'a'),('term',285,195,'b'),('gnd',145,195)
],engine={'omega':1},anchors={'Vth':9.982683969692435-16.63780661615406j,
    'Zth':1.176470588235294-5.2941176470588225j})

alias('P22',1,1,'e_t26_02','Mesmos valores, tres ramos em paralelo; solicita Zeq.')

add('P22',2,1,'Analise Nodal AC',[
    'Vs=16 sen(4t-10deg) V. L=1 H, C=0.25 F, R=1 ohm.',
    'Fonte dependente 0.5 Ix para cima. Ix: esquerda -> direita em L.',
    'Ache ZL, ZC, fasor Vs, Ix e Vo (positivo no topo de R).'
],live=recipe(('Vs','c0','V','Seno: 16/_-100 V',2),
    ('ZL','z1','ohm','ZL=jwL'),('ZC','z2','ohm','ZC=1/(jwC)'),
    ('Zvia','z2+z4','ohm','Zvia=ZC+R'),
    ('Ix','c0/(z1+(1+c3)*Zvia)','A','KVL: Vs=ZL Ix+Zvia(1+g)Ix',2),
    ('Ic','(1+c3)*Ix','A','KCL: Ic=Ix+g Ix',2),
    ('Vo','Ic*z4','V','Vo=Ic R',2),
    ('check','guard(abs(Ix-i1)<max(abs(Ix),1e-30)*1e-3)','','',0),flags=1),
    ops=[('vsrc_v',40,100,195,'16/_-100V'),('ind_h',40,100,155,'1H'),
         ('cap_h',155,100,265,'0.25F'),('dis_v',155,100,195,'0.5Ix',True),
         ('res_v',265,100,195,'1'),('wire',40,195,265,195),
         ('arr_h',62,70,119,'Ix',True),('vo',297,100,195,'Vo'),('gnd',155,195)],
    engine={'omega':4,'dep_resolve':{3:{'kind':'current','branch_op_index':1}}},
    anchors={'Ix':-5.124690162881723-1.9634657606606798j},
    notes='Fonte dependente injeta 0.5 Ix no no superior; KCL: Ic=1.5 Ix.')

add('P22',3,1,'Analise Malhas AC',[
    'Calcule I1 e I2 por malhas, ambas no sentido horario.',
    'Vs1=40/_30 V, Vs2=50/_0 V (positivo no topo).',
    'Ramos superiores j10 e 40 ohm; ramo comum -j20 ohm.'
],live=recipe(('A','z1+z2','ohm','Malha 1: (Z1+Zc)I1-Zc I2=Vs1'),
    ('D','z3+z2','ohm','Malha 2: -Zc I1+(R+Zc)I2=-Vs2'),
    ('Det','A*D-z2**2','ohm2','Det=(Z1+Zc)(R+Zc)-Zc^2'),
    ('I1','(c0*D-z2*c4)/Det','A','Cramer: I1=(Vs1 D-Zc Vs2)/Det',2),
    ('I2','(z2*c0-A*c4)/Det','A','Cramer: I2=(Zc Vs1-A Vs2)/Det',2),
    ('Ic','I1-I2','A','Ramo comum: Ic=I1-I2',2),
    ('check','guard(abs(I1-i1)<max(abs(I1),1e-30)*1e-3)','','',0),flags=1),ops=[
    ('vsrc_v',40,90,195,'40/_30V'),('imp_h',40,90,150,'j10'),
    ('imp_v',150,90,195,'-j20'),('res_h',150,90,265,'40'),
    ('vsrc_v',265,90,195,'50V'),('wire',40,195,265,195),
    ('arr_h',60,68,115,'I1',True),('arr_h',185,68,240,'I2',True),('gnd',150,195)
],engine={'omega':1},anchors={'I1':-.42871870788979577+4.678460969082652j,
    'I2':.7856406460551018+.6071796769724489j})

add('P22',4,1,'Potencia AC',[
    'Fonte de pico 16/_45 V. Rserie=2 ohm, ramos 10-j5 e 8+j6 ohm.',
    'Ache Zin, I, fator de potencia, |S| e Q da carga.',
    'S=V conj(I)/2: fasores de pico. Q>0: atraso; Q<0: avanco.'
],live=recipe(('Z1','z2+z3','ohm','Ramo 1: R1+ZC'),('Z2','z4+z5','ohm','Ramo 2: ZL+R2'),
    ('Zp','1/(1/Z1+1/Z2)','ohm','Zp=Z1||Z2'),('Zin','z1+Zp','ohm','Zin=Rserie+Zp'),
    ('I','c0/Zin','A','I=Vs/Zin',2),('S','c0*conj(I)/2','VA','S=Vpico conj(Ipico)/2'),
    *power_summary(),('phi','arg(S)','deg','phi>0: atraso; phi<0: avanco')),ops=[
    ('vsrc_v',40,85,195,'16/_45V'),('res_h',40,85,145,'2'),
    ('imp_v',145,85,140,'-j5'),('res_v',145,140,195,'10'),
    ('wire',145,85,265,85),('imp_v',265,85,140,'j6'),
    ('res_v',265,140,195,'8'),('wire',40,195,265,195),('gnd',145,195)
],engine={'omega':1,'peak':True},anchors={'S':15.559633027522938+1.4678899082568817j})

p,r=sinusoid(127,314.16,-26.5)
add('P1B',1,1,'Impedancia AC',['v(t)=127 cos(314.16t-26.5deg) V.', 'Determine amplitude, fase, periodo e frequencia.'],p,r,anchors={'f':50.00011692175})

p,r=sinusoid(-220,377,50,True)
add('P1B',2,1,'Impedancia AC',['Converta v(t)=-220 sen(377t+50deg) V para fasor polar.', 'Use cosseno e amplitude positiva.'],p,r,anchors={'X':-168.52977748617517+141.4132741310387j})

add('P1B',3,2,'Circuitos AC Cap9',[
    'Determine Zin e I em retangular e polar.',
    'Vs=120/_10 V, Rserie=2 ohm; ramos 4-j6 e 3+j4 ohm.'
],live=recipe(('Z1','z2+z3','ohm','Serie: Z1=4-j6'),
    ('Z2','z4+z5','ohm','Serie: Z2=3+j4'),
    ('Zp','1/(1/Z1+1/Z2)','ohm','Paralelo: Zp=Z1 Z2/(Z1+Z2)'),
    ('Zin','z1+Zp','ohm','Zin=Rserie+Zp'),
    ('ZinPolar','Zin','ohm','Forma polar',2),
    ('Iret','c0/Zin','A','I=Vs/Zin'),
    ('I','Iret','A','i(t)=|I|cos(wt+arg(I))',2)),ops=[
    ('vsrc_v',40,100,195,'120/_10V'),('res_h',40,100,135,'2'),
    ('res_h',135,100,205,'4'),('imp_h',205,100,275,'-j6'),
    ('wire',135,100,135,160),('res_h',135,160,205,'3'),
    ('imp_h',205,160,275,'j4'),('wire',275,100,275,195),
    ('wire',40,195,275,195),('gnd',135,195)
],engine={'omega':1},anchors={'Zin':6.830188679245283+1.0943396226415092j,
    'I':17.345678275793436+.27169356344104345j})

add('P1B',4,2,'Analise Nodal AC',[
    'Corrente total I=21/_-13 A. Determine Yeq, Zeq, V e I3.',
    'Ramos paralelos: j5, 5+j8.66, 15 e -j10 ohm. I3 no resistor 15.',
    'V positivo no barramento superior; I3 para baixo.'
],live=recipe(('Y1','1/z1','S','Admitancias de ramo: Yk=1/Zk'),
    ('Y2','1/(z2+z3)','S'),('Y3','1/z4','S'),('Y4','1/z5','S'),
    ('Yeq','Y1+Y2+Y3+Y4','S','Yeq=soma das admitancias'),
    ('Zeq','1/Yeq','ohm','Zeq=1/Yeq'),('V','c0/Yeq','V','KCL: V Yeq=I',2),
    ('I3','V/z4','A','I3=V/R3',2)),ops=[
    ('isrc_h',35,85,105,'21/_-13A',True),('imp_v',130,85,195,'j5'),
    ('res_v',185,85,140,'5'),('imp_v',185,140,195,'j8.66'),
    ('res_v',245,85,195,'15'),('imp_v',300,85,195,'-j10'),
    ('wire',105,85,300,85),('wire',35,85,35,195),
    ('wire',35,195,300,195),('lbl','I3=V/15',208,210),('gnd',35,195)
],engine={'omega':1},anchors={'V':67.49095514977517+67.45670449112812j,
    'I3':4.499397009985012+4.497113632741875j})

add('P1B',5,3,'Analise Malhas AC',[
    'Vs1=10 cos(2t) V; Vs2=6 sen(2t) V. R=4, L=2 H, C=0.25 F.',
    'Malhas I1/I2 horarias; Io=I1-I2 para baixo no capacitor.',
    'Determine Io em fasor e no tempo.'
],live=recipe(('V1','c0','V','Referencia cosseno',2),('V2','c4','V','Seno -> cosseno: fase -90 graus',2),
    ('ZL','z2','ohm','ZL=jwL'),('ZC','z3','ohm','ZC=1/(jwC)'),
    ('A','z1+z3','ohm','A I1-ZC I2=V1'),('D','z2+z3','ohm','-ZC I1+D I2=-V2'),
    ('Det','A*D-z3**2','ohm2'),
    ('I1','(c0*D-z3*c4)/Det','A','Cramer para a malha 1',2),
    ('I2','(z3*c0-A*c4)/Det','A','Cramer para a malha 2',2),
    ('Io','I1-I2','A','Io=I1-I2',2),('w','omega','rad/s','io(t)=|Io|cos(wt+arg(Io))'),
    ('check','guard(abs(Io-i3)<max(abs(Io),1e-30)*1e-3)','','',0),flags=1),ops=[
    ('vsrc_v',40,100,195,'10V'),('res_h',40,100,150,'4'),
    ('ind_h',150,100,265,'2H'),('cap_v',150,100,195,'0.25F'),
    ('vsrc_v',265,100,195,'6/_-90V'),('wire',40,195,265,195),
    ('arr_h',65,68,120,'I1',True),('arr_h',185,68,240,'I2',True),
    ('arr_v',131,130,180,'Io',False),('gnd',150,195)
],engine={'omega':2},anchors={'Io':1+1j})

add('P1B',6,4,'Analise Nodal AC',[
    'Use transformacao de fontes para Ix (para baixo em 4-j3).',
    'Vs=60/_0 V, Is=5/_90 A para cima. Rserie=2 e ZL=j4;',
    'shunt=6, ZC=-j2 e ramo de saida=4-j3 ohm.'
],live=recipe(('Zs','z1+z2','ohm','Serie da fonte V: Zs=R+jXL'),
    ('Zp','1/(1/z3+1/Zs)','ohm','Zp=Rshunt||Zs'),
    ('Veq','c0*Zp/Zs','V','Transformacao: Veq=(Vs/Zs)Zp',2),
    ('Zeq','Zp+z4','ohm','Zeq=Zp+ZC'),
    ('Zout','z5+z6','ohm','Zout=Rout+jXout'),
    ('In','Veq/Zeq','A','Norton: In=Veq/Zeq',2),
    ('Ix','(In+c7)*Zeq/(Zeq+Zout)','A','Divisor: Ix=(In+Is)Zeq/(Zeq+Zo)',2),
    ('check','guard(abs(Ix-i5)<max(abs(Ix),1e-30)*1e-3)','','',0),flags=1),ops=[
    ('vsrc_v',35,100,195,'60V'),('res_h',35,100,75,'2'),
    ('imp_h',75,100,115,'j4'),('res_v',115,100,195,'6'),
    ('imp_h',115,100,160,'-j2'),('res_v',170,100,145,'4'),
    ('imp_v',170,145,195,'-j3'),('isrc_v',300,100,195,'5/_90A',True),
    ('wire',160,100,300,100),('wire',35,195,300,195),('gnd',115,195),
    ('lbl','Ix: para baixo no ramo 4-j3',12,212)
],engine={'omega':1},anchors={'Ix':5+1.5625j})

add('R1A',1,1,'Circuitos AC Cap9',[
    'Ache Vo sobre L em fasor e no tempo. Vs=60 sen(200t) V.',
    'Rserie=50 ohm, Rpar=30 ohm, C=30 uF, L=0.1 H.',
    'Referencia cosseno: Vs=60/_-90 V. Vo positivo no topo de L.'
],live=recipe(('ZC','z3','ohm','ZC=1/(jwC)'),('ZL','z4','ohm','ZL=jwL'),
    ('Zp','1/(1/z2+1/ZC)','ohm','Zp=Rpar||ZC'),
    ('Zt','z1+Zp+ZL','ohm','Zt=Rserie+Zp+ZL'),
    ('I','c0/Zt','A','Serie: I=Vs/Zt',2),('Vo','I*ZL','V','Vo=I ZL',2),
    ('w','omega','rad/s','vo(t)=|Vo|cos(wt+arg(Vo))')),ops=[
    ('vsrc_v',35,90,195,'60/_-90V'),('res_h',35,90,115,'50'),
    ('res_h',115,90,225,'30'),('cap_h',115,150,225,'30uF'),
    ('wire',115,90,115,150),('wire',225,90,225,150),
    ('wire',225,90,275,90),('ind_v',275,90,195,'0.1H'),
    ('wire',35,195,275,195),('gnd',115,195),('lbl','Vo sobre L',178,212)
],engine={'omega':200},anchors={'Vo':14.666754517846769-2.7399984426381714j},
    notes='Seno convertido para cosseno; nao usar a fase do gabarito sem -90deg.')

add('R1A',2,2,'Circuitos AC Cap9',[
    'Is=5 cos(10t+40deg) A, para cima. R1=4, L=0.2 H, R2=3, C=0.1 F.',
    'Determine io(t), para baixo no capacitor.'
],live=recipe(('ZL','z2','ohm','ZL=jwL'),('ZC','z4','ohm','ZC=1/(jwC)'),
    ('Zesq','1/(1/z1+1/ZL)','ohm','R1 e L em paralelo (ramo esquerdo)'),
    ('Zdir','z3+ZC','ohm','R2 e C em serie (ramo direito)'),
    ('Io','c0*Zesq/(Zesq+Zdir)','A','Divisor: Io=Is Zesq/(Zesq+Zdir)',2),
    ('w','omega','rad/s','io(t)=|Io|cos(wt+arg(Io))'),
    ('check','guard(abs(Io-i4)<max(abs(Io),1e-30)*1e-3)','','',0),flags=1),ops=[
    ('isrc_h',35,90,105,'5/_40A',True),('res_v',125,90,195,'4'),
    ('ind_v',190,90,195,'0.2H'),('res_h',190,90,270,'3'),
    ('cap_v',270,90,195,'0.1F'),('wire',35,90,35,195),
    ('wire',105,90,190,90),('wire',35,195,270,195),
    ('arr_v',250,135,180,'Io',False),('gnd',35,195)
],engine={'omega':10},anchors={'Io':-.18088947357050933+2.3179051757474443j})

add('R1A',3,3,'Circuitos AC Cap9',[
    'Para Vs=90/_15 V, ache Zin e I em retangular e polar.',
    'Serie: 20+j15. Ramos paralelos: 25-j50 e 30+j10 ohm.'
],live=recipe(('Z1','z3+z4','ohm','Z1=R1+ZC'),('Z2','z5+z6','ohm','Z2=R2+ZL'),
    ('Zp','1/(1/Z1+1/Z2)','ohm','Zp=Z1||Z2'),('Zin','z1+z2+Zp','ohm','Zin=Rserie+ZLserie+Zp'),
    ('Zpolar','Zin','ohm','Forma polar',2),('Iret','c0/Zin','A','I=Vs/Zin'),
    ('I','Iret','A','Forma polar',2)),ops=[
    ('vsrc_v',40,100,195,'90/_15V'),('res_h',40,100,95,'20'),
    ('imp_h',95,100,160,'j15'),('imp_v',160,100,145,'-j50'),
    ('res_v',160,145,195,'25'),('res_v',270,100,145,'30'),
    ('imp_v',270,145,195,'j10'),('wire',160,100,270,100),
    ('wire',40,195,270,195),('gnd',160,195)
],engine={'omega':1},anchors={'Zin':45.67567567567568+10.945945945945944j,
    'I':1.915482663063451+.05094493588798613j})

alias('R1A',4,4,'e_p22_03','Mesma rede e mesmos fasores: duas malhas horarias.')

add('R1A',5,5,'Superposicao AC',[
    'Is=12 cos(10t+10deg) A e Vs=50 cos(10t) V.',
    'Determine V por superposicao. Rshunt=16, Rserie=20, L=5 H.',
    'Anule V por curto e I por circuito aberto.'
],live=recipe(('ZL','z3','ohm','ZL=jwL'),('Zs','z2+ZL','ohm','Zs=Rserie+ZL'),
    ('Zp','1/(1/z1+1/Zs)','ohm','Vs anulada: Zp=Rshunt||Zs'),
    ('V_Is','c0*Zp','V','Parcela da corrente: V_Is=Is Zp',2),
    ('V_Vs','c4*z1/(z1+Zs)','V','Parcela da tensao: V_Vs=Vs R/(R+Zs)',2),
    ('V','V_Is+V_Vs','V','Mesma w: V=V_Is+V_Vs',2),
    ('w','omega','rad/s','v(t)=|V|cos(wt+arg(V))')),ops=[
    ('isrc_v',40,100,195,'12/_10A',True),('res_v',135,100,195,'16'),
    ('res_h',135,100,210,'20'),('ind_h',210,100,285,'5H'),
    ('vsrc_v',285,100,195,'50V'),('wire',40,100,135,100),
    ('wire',40,195,285,195),('lbl','V',125,78),('gnd',135,195)
],engine={'omega':10},anchors={'V':160.95236700016517+57.59291892083198j},
    notes='Gabarito soma retangular incorreta; recalcule V_Is e V_Vs sem arredondar.')

p,r,o,g=rated_load(127,12000,.856)
add('P2A',1,1,'Potencia AC',[
    'Carga: V=127/_0 V RMS, |S|=12 kVA, FP=0.856 atrasado.',
    'Determine P, Q, corrente de pico e impedancia da carga.',
    'Q_sinal: +1 atrasado, -1 adiantado. Z=V/I, nao V/conj(I).'
],p,r,o,g,anchors={'S':10272+6203.709857818949j},
    notes='Q em VAR; calcular Z com corrente RMS. Gabarito mistura Irms e Ipico.')

p,r=motor(7650,380,18.2)
add('P2A',2,1,'Trifasico',[
    'Motor em estrela, sistema equilibrado: P=7650 W, VL=380 V RMS, IL=18.2 A.',
    'Determine o fator de potencia do motor (atrasado).'
],p,r,anchors={'FP':.6386248639821627})

p,r,o,g=parallel_power(220,124)
add('P2A',3,2,'Potencia AC',[
    'V=220 V RMS. Cargas paralelas: 124, 20-j25 e 90+j80 ohm.',
    'Determine |S| de cada ramo, |St|, P, Q e fator de potencia.',
    'Q negativo significa carga capacitiva e FP adiantado.'
],p,r,o,g,anchors={'S':1635.1266176510487-913.4533221194281j},
    notes='Potencia aparente e |Sk|, nao Sk. Q=-913.45 VAR.')

p,r,o,g=three_delta(380,'20-j15')
add('P2A',4,2,'Trifasico',[
    'Delta equilibrado: Zab=Zbc=Zca=20-j15 ohm. Vab=380/_0 V RMS, ABC.',
    'Calcule correntes de fase e de linha. Fonte desenhada em Y equivalente.',
    'Ica: C -> A. Ia=Iab-Ica. Cada fonte e impedancia pode ser editada.'
],p,r,o,g,anchors={'Iab':12.16+9.12j})

p,r,o,g=three_y(127,['25','6-j8','10+j5'],1)
add('P2A',5,3,'Trifasico',[
    'Y desequilibrado com neutro. Van=127/_0 V RMS, sequencia ABC.',
    'Za=25, Zb=6-j8, Zc=10+j5 ohm. Determine Ia, Ib, Ic e In.',
    'ABC: Vbn=127/_-120, Vcn=127/_120; nao inverter a sequencia.'
],p,r,o,g,anchors={'In':-9.388227153674844+.34029547438752594j},
    notes='Gabarito usa ACB, mas o enunciado exige ABC. Correntes recalculadas para ABC.')

p,r,o,g=rated_load(220,12000,.856)
add('P2B',1,1,'Potencia AC',[
    'V=220/_0 V RMS, |S|=12 kVA, FP=0.856 atrasado.',
    'Determine P, Q, Ipico e Z. Q_sinal: +1 atraso, -1 avanco.'
],p,r,o,g,anchors={'S':10272+6203.709857818949j})

p,r=motor(6750,380,12.2)
add('P2B',2,1,'Trifasico',[
    'Motor em Y equilibrado: P=6750 W, VL=380 V RMS, IL=12.2 A.',
    'Determine o fator de potencia do motor (atrasado).'
],p,r,anchors={'FP':.8406199993593559})

p,r,o,g=parallel_power(127,124)
add('P2B',3,2,'Potencia AC',[
    'V=127 V RMS. Cargas em paralelo: 124, 20-j25 e 90+j80 ohm.',
    'Ache |S| de cada ramo, |St|, P, Q e FP total.'
],p,r,o,g,anchors={'S':544.8958102498711-304.4026576955425j})

p,r,o,g=three_delta(220,'20-j15')
add('P2B',4,2,'Trifasico',[
    'Delta equilibrado, ABC: Vab=220/_0 V RMS, Zfase=20-j15 ohm.',
    'Ache correntes de fase e de linha. Fonte em Y equivalente.',
    'Ica: C -> A; Ia=Iab-Ica. Todas as fases sao editaveis.'
],p,r,o,g,anchors={'Iab':7.04+5.28j})

p,r,o,g=three_y(127,['35','10+j5','6-j8'],1)
add('P2B',5,3,'Trifasico',[
    'Y com neutro, ABC, Van=127/_0 V RMS.',
    'Za=35, Zb=10+j5, Zc=6-j8 ohm. Ache Ia, Ib, Ic e In.',
    'In aponta do neutro da carga para a fonte.'
],p,r,o,g,anchors={'In':18.459655725103413+4.739704525612473j})

add('R2A',1,1,'Potencia AC',[
    'Fonte 5/_30 V de pico; R=4 ohm em serie com ZC=-j2 ohm.',
    'Ache potencia media fornecida pela fonte e absorvida em R e C.',
    'Fasores de pico: S=V conj(I)/2. Capacitor ideal: P=0.'
],live=recipe(('Zt','z1+z2','ohm','Serie: Zt=R+ZC'),
    ('I','c0/Zt','A','I=Vs/Zt',2),('SR','z1*abs(I)**2/2','VA','SR=R |Ipico|^2/2'),
    ('SC','z2*abs(I)**2/2','VA','SC=ZC |Ipico|^2/2'),
    ('S','c0*conj(I)/2','VA','Potencia fornecida: S=Vs conj(I)/2'),
    ('Pfonte','real(S)','W','Pfornecida=PR+PC'),
    ('PR','real(SR)','W','Potencia absorvida em R'),
    ('PC','real(SC)','W','Capacitor ideal: potencia media zero'),
    *power_summary()),ops=[
    ('vsrc_v',40,90,195,'5/_30V'),('res_h',40,90,265,'4'),
    ('imp_v',265,90,195,'-j2'),('wire',40,195,265,195),('gnd',40,195)
],engine={'omega':1,'peak':True},anchors={'S':2.5-1.25j})

p,r=wave_power(120,-20,4,-10,100)
add('R2A',2,1,'Potencia AC',[
    'i(t)=4 cos(100t-10deg) A; v(t)=120 cos(100t-20deg) V.',
    'Ache |S|, FP, P e Q; corrente na convencao passiva.',
    'Fasores de pico: dividir V conj(I) por 2.'
],p,r,anchors={'S':236.35386072292994-41.675562640063276j},
    notes='Diferenca de fase -10deg: FP=cos(10), nao 0.866 do gabarito.')

add('R2A',3,2,'Trifasico',[
    'Carga delta equilibrada: P=5000 W, FP=0.8 atrasado, VL=380 V RMS.',
    'Determine a corrente de linha. Nao usar 400 V do gabarito.'
],params=[('P_W',5000),('FP',.8),('VL_V',380)],live=recipe(
    ('dom','guard(P_W>0 and FP>0 and FP<=1 and VL_V>0)','','',0),
    ('S','P_W/FP','VA','|S|=P/FP'),('phi','acos(FP)','deg','Carga indutiva: atraso'),
    ('Q','P_W*tan(phi)','VAR','Q=P tan(phi)'),
    ('IL','S/(sqrt(3)*VL_V)','A','IL=|S|/(sqrt(3) VL)'),
    ('Ifase','IL/sqrt(3)','A','Delta equilibrado: Ifase=IL/sqrt(3)')),
    anchors={'IL':9.495892585355687},
    notes='O PDF troca VL=380 por 400 no calculo; usar o enunciado.')

add('R2A',4,2,'Trifasico',[
    'Va=220 cos(wt+10deg), Vb=220 cos(wt-230deg), Vc=220 cos(wt-110deg) V.',
    'Determine a sequencia. ABC=1: A -> B -> C. ABC=0: A -> C -> B.',
    'Equilibrio exige magnitudes iguais e separacao de 120 graus.'
],params=[('A_V',220),('B_V',220),('C_V',220),
    ('pha_deg',10),('phb_deg',-230),('phc_deg',-110)],live=recipe(
    ('Va','polar(A_V,pha_deg)','V','Fasor Va, referencia cosseno',2),
    ('Vb','polar(B_V,phb_deg)','V','Fasor Vb',2),
    ('Vc','polar(C_V,phc_deg)','V','Fasor Vc',2),
    ('dAB','arg(Vb/Va)','deg','dAB=arg(Vb/Va)'),
    ('dBC','arg(Vc/Vb)','deg','dBC=arg(Vc/Vb)'),
    ('dCA','arg(Va/Vc)','deg','dCA=arg(Va/Vc)'),
    ('rot','sin(dAB)+sin(dBC)+sin(dCA)','','Sinal das diferencas ciclicas',0),
    ('dom','guard(abs(rot)>1e-5)','','',0),
    ('ABC','rot<0','','1: ABC (positiva); 0: ACB (negativa)'),
    ('erro120','max(abs(abs(dAB)-120),max(abs(abs(dBC)-120),abs(abs(dCA)-120)))',
        'deg','Erro de separacao angular'),
    ('erroAmp','max(abs(A_V-B_V),abs(A_V-C_V))','V','Erro entre magnitudes de fase')),
    anchors={'ABC':0,'dAB':120},
    notes='220 V no enunciado; a resolucao impressa troca indevidamente por 200 V.')

alias('R2A',5,2,'e_p2a_04','Mesma carga delta, fonte ABC e Vab=380/_0 V RMS.')

p,r,o,g=three_y(127,['25','6-j8','10+j5'],-1)
add('R2A',6,3,'Trifasico',[
    'Y desequilibrado com neutro, Van=127/_0 V RMS, sequencia ACB.',
    'Za=25, Zb=6-j8, Zc=10+j5 ohm. Ache Ia, Ib, Ic e In.',
    'ACB: Vbn=127/_120, Vcn=127/_-120. In: N -> fonte.'
],p,r,o,g,anchors={'In':17.00822715367484+4.739704525612473j})

add('L25',1,1,'Impedancia AC',[
    'Some 4 cos(wt) e -5 sen(wt). Mostre o diagrama fasorial.',
    'Mesmo w: X=Acos-j Asin. x(t)=|X|cos(wt+arg(X)).',
    'MODE edita ambos os coeficientes. O vetor muda junto com a resposta.'
],params=[('Acos',4),('Asin',-5)],live=recipe(
    ('X','complex(Acos,-Asin)','','cos -> real; sen -> -j',2),
    ('Xret','X','','Soma retangular: X=Acos-j Asin'),
    ('Amplitude','abs(X)','','Amplitude positiva=|X|'),
    ('fase','arg(X)','deg','x(t)=|X|cos(wt+fase)')),
    ops=[('wire',55,136,265,136),('wire',160,68,160,203),
         ('lbl','Re',275,132),('lbl','Im',166,61),
         ('lbl','Escala automatica; valores na solucao',12,211)],
    engine={'diagram_only':True,'flags2':8},anchors={'X':4+5j})

p,r=sinusoid(127,377,12)
add('L25',2,1,'Impedancia AC',[
    'v(t)=127 cos(377t+12deg) V. Ache amplitude, fase, T e f.'
],p,r,anchors={'f':60.00141354564455})

p,r=sinusoid(12,50,45)
add('L25',3,1,'Impedancia AC',[
    'v(t)=12 cos(50t+45deg) V. Ache amplitude, fase, T e f.'
],p,r,anchors={'T':.12566370614359174})

p,r=sinusoid(220,314,21)
add('L25',4,1,'Impedancia AC',[
    'v(t)=220 cos(314t+21deg) V. Ache amplitude, fase, T e f.'
],p,r,anchors={'f':49.97465213085514})

p,r=sinusoid(220,9*3.141592653589793,-32,True)
add('L25',5,1,'Impedancia AC',[
    'v(t)=220 sen(9 pi t-32deg) V. Ache amplitude, fase, w, T e f.',
    'Fase original no seno: -32deg. Fase em cosseno: -122deg.'
],p,r,anchors={'f':4.5})

p,r=sinusoid(110,60,20,time=.01)
add('L25',6,1,'Impedancia AC',[
    'v(t)=110 cos(60t+20deg) V. Ache a tensao, T, f e v(10ms).',
    'Edite t_s em segundos: 10ms=0.01 s.'
],p,r,anchors={'x_t':64.06869560565043})

add('L25',7,1,'Impedancia AC',[
    'V1(t)=20 sen(wt+60deg) V; V2(t)=60 cos(wt-10deg) V.',
    'Qual a diferenca de fase? Qual tensao adianta a outra?',
    'delta>0: V2 adianta V1. delta<0: V2 atrasa V1.'
],params=[('A1_V',20),('phi1_deg',60),('A2_V',60),('phi2_deg',-10)],
    live=recipe(('V1','polar(A1_V,phi1_deg-90)','V','Seno -> cosseno: subtrair 90deg',2),
    ('V2','polar(A2_V,phi2_deg)','V','Referencia cosseno',2),
    ('delta','arg(V2/V1)','deg','delta=arg(V2)-arg(V1), normalizado'),
    ('V2adianta','delta>0','','1: V2 adianta; 0: nao adianta'),
    ('V2atrasa','delta<0','','1: V2 atrasa; 0: nao atrasa')),
    anchors={'delta':20})

add('L25',8,1,'Impedancia AC',[
    'Calcule [15/_45 / (3-j4)] + j^2. Resposta retangular.',
    'Todas as constantes numericas sao editaveis em MODE.'
],params=[('A_mag',15),('A_deg',45),('R',3),('X',-4),('j_exp',2)],
    live=recipe(('A','polar(A_mag,A_deg)','','Numerador: A em retangular'),
    ('Z','complex(R,X)','','Denominador: Z=R+jX'),
    ('div','A/Z','','Divisao complexa A/Z'),
    ('jpow','complex(0,1)**j_exp','','j^2=-1 no caso original'),
    ('total','div+jpow','','Resultado retangular')),
    anchors={'total':-1.4242640687119286+2.9698484809834995j})

add('L25',9,1,'Impedancia AC',[
    'Calcule [10/_-30+(3-j4)] / [(2+j4)(3-j5)*]. Resposta polar.',
    'A estrela conjuga somente o fator (3-j5).'
],params=[('A_mag',10),('A_deg',-30),('B_re',3),('B_im',-4),
    ('C_re',2),('C_im',4),('D_re',3),('D_im',-5)],live=recipe(
    ('A','polar(A_mag,A_deg)','','Converta o fasor do numerador'),
    ('B','complex(B_re,B_im)','','Parcela retangular do numerador'),
    ('C','complex(C_re,C_im)','','Primeiro fator do denominador'),
    ('Dconj','conj(complex(D_re,D_im))','','Conjugue somente o segundo fator'),
    ('num','A+B','','Numerador=A+B'),('den','C*Dconj','','Denominador=C conj(D)'),
    ('ret','num/den','','Divisao em retangular'),
    ('total','ret','','Resultado polar',2)),
    anchors={'total':-.531240524308561-.1919493953420243j})

add('L25',10,1,'Impedancia AC',[
    'Calcule [8/_-20 / ((2+j)(3-j4))] + [10/(-5+j12)].',
    'De o resultado retangular.'
],params=[('A_mag',8),('A_deg',-20),('B_re',2),('B_im',1),
    ('C_re',3),('C_im',-4),('D',10),('E_re',-5),('E_im',12)],live=recipe(
    ('num','polar(A_mag,A_deg)','','Converta o primeiro numerador'),
    ('den1','complex(B_re,B_im)*complex(C_re,C_im)','','Multiplique os fatores'),
    ('p1','num/den1','','Primeira parcela'),
    ('p2','D/complex(E_re,E_im)','','Segunda parcela'),
    ('total','p1+p2','','Some as parcelas retangulares')),
    anchors={'total':.4149917350015149-.6282504246745704j})

add('L25',11,2,'Impedancia AC',[
    'Converta para fasores polares em referencia cosseno:',
    '(a) -10 cos(4t+75deg); (b) 5 sen(20t-10deg); (c) 4 cos(2t)+3 sen(2t).',
    'Em (c), some antes de obter modulo e fase.'
],params=[('Aa',-10),('wa_rad_s',4),('pha_deg',75),
    ('Ab',5),('wb_rad_s',20),('phb_deg',-10),
    ('Ac_cos',4),('Ac_sen',3),('wc_rad_s',2)],live=recipe(
    ('Xa','polar(Aa,pha_deg)','','Amplitude negativa soma 180deg',2),
    ('wa','wa_rad_s','rad/s','Frequencia angular do item a'),
    ('Xb','polar(Ab,phb_deg-90)','','Seno: fase menos 90deg',2),
    ('wb','wb_rad_s','rad/s','Frequencia angular do item b'),
    ('Xc','complex(Ac_cos,-Ac_sen)','','Mesmo w: cos -> real, sen -> -j',2),
    ('wc','wc_rad_s','rad/s','Frequencia angular do item c')),
    anchors={'Xc':4-3j})

add('L25',12,2,'Impedancia AC',[
    'Converta os quatro fasores ao tempo (referencia cosseno):',
    'V1=60/_15 V, w1=1; V2=6+j8 V, w2=40;',
    'I1=2.8 exp(-j pi/3) A, w3=377; I2=-0.5-j1.2 A, w4=1000.',
    'x(t)=|X|cos(wt+arg(X)). t_s permite conferir qualquer instante.'
],params=[('V1_mag',60),('V1_deg',15),('w1_rad_s',1),
    ('V2_re',6),('V2_im',8),('w2_rad_s',40),
    ('I1_mag',2.8),('I1_deg',-60),('w3_rad_s',377),
    ('I2_re',-.5),('I2_im',-1.2),('w4_rad_s',1000),('t_s',.01)],
    live=recipe(('V1','polar(V1_mag,V1_deg)','V','Forma polar de V1',2),
    ('w1','w1_rad_s','rad/s','v1(t)=|V1|cos(w1 t+arg V1)'),
    ('v1_t','abs(V1)*cos(w1*t_s*180/pi+arg(V1))','V','Avaliacao de v1(t)'),
    ('V2','complex(V2_re,V2_im)','V','Retangular -> polar de V2',2),
    ('w2','w2_rad_s','rad/s','v2(t)=|V2|cos(w2 t+arg V2)'),
    ('v2_t','abs(V2)*cos(w2*t_s*180/pi+arg(V2))','V','Avaliacao de v2(t)'),
    ('I1','polar(I1_mag,I1_deg)','A','-pi/3 rad = -60 graus',2),
    ('w3','w3_rad_s','rad/s','i1(t)=|I1|cos(w3 t+arg I1)'),
    ('i1_t','abs(I1)*cos(w3*t_s*180/pi+arg(I1))','A','Avaliacao de i1(t)'),
    ('I2','complex(I2_re,I2_im)','A','Retangular -> polar de I2',2),
    ('w4','w4_rad_s','rad/s','i2(t)=|I2|cos(w4 t+arg I2)'),
    ('i2_t','abs(I2)*cos(w4*t_s*180/pi+arg(I2))','A','Avaliacao de i2(t)')),
    anchors={'I1':1.4-2.424871130596428j,'V2':6+8j})

add('L25',13,2,'Circuitos AC Cap9',[
    'Vs=100/_0 V sobre a carga Z=5+j4 ohm. Determine IL em fasor.',
    'IL aponta para baixo na carga; polaridade positiva no topo.'
],live=recipe(('Z','z1','ohm','Z da carga, forma retangular'),
    ('ILret','c0/Z','A','Lei de Ohm: IL=Vs/Z'),
    ('IL','ILret','A','Corrente em forma polar',2)),
    ops=[('vsrc_v',40,90,195,'100V'),('wire',40,90,265,90),
        ('imp_v',265,90,195,'5+j4'),('wire',40,195,265,195),
        ('arr_v',215,125,175,'IL',False),('gnd',40,195)],
    engine={'omega':1},anchors={'IL':12.195121951219512-9.756097560975611j})

alias('L25',14,2,'p9_35','Exatamente o problema 9.35: 50 cos(200t), R10, C5mF, L20mH.')

base=next(e for e in EXERCISES if e['id']=='e_r1a_01')
o=[tuple(list(op[:4])+[{'50':'30','30':'50','30uF':'50uF'}.get(op[4],op[4])]+list(op[5:]))
    if op[0] in ('res_h','cap_h') else op for op in CIRCUITS['e_r1a_01']]
add('L25',15,2,'Circuitos AC Cap9',[
    'Vs=60 sen(200t) V; Rserie=30, Rpar=50, C=50uF, L=0.1H.',
    'Ache vo(t) sobre L e o fasor Vo, positivo no topo do indutor.',
    'No caso original, Vo=17.1429/_0 V de pico.'
],live=base['live_recipe'],ops=o,engine={'omega':200},
    anchors={'Vo':17.142857142857142})

p,r=sinusoid(15,25*3.141592653589793,-25,unit='A',time=.003)
add('L25',16,3,'Impedancia AC',[
    'is(t)=15 cos(25 pi t-25deg) A. Ache amplitude, w, f e is(3ms).',
    't_s em segundos: 3ms=0.003 s.'
],p,r,anchors={'f':12.5})

add('L25',17,3,'Circuitos AC Cap9',[
    'Vs=10 cos(4t) V, R=5 ohm, C=0.1 F em serie.',
    'Determine i(t) e vC(t), positivo no topo do capacitor.'
],live=recipe(('ZC','z2','ohm','ZC=1/(jwC)'),('Zt','z1+ZC','ohm','Zt=R+ZC'),
    ('I','c0/Zt','A','i(t)=|I|cos(wt+arg(I))',2),
    ('V','I*ZC','V','vC(t)=|V|cos(wt+arg(V))',2),
    ('w','omega','rad/s','Mesma frequencia da fonte')),
    ops=[('vsrc_v',40,90,195,'10V'),('res_h',40,90,265,'5'),
    ('cap_v',265,90,195,'0.1F'),('wire',40,195,265,195),('gnd',40,195)],
    engine={'omega':4},anchors={'V':2-4j,'I':1.6+.8j})

alias('L25',18,3,'p9_37','Admitancia do mesmo paralelo 4, j8 e -j10 ohm do livro.')

alias('L25',19,3,'e_r1a_02','Mesmos dados, sentido de Io e pedido no dominio do tempo.')

alias('L25',20,3,'e_p1b_03','Mesma fonte 120/_10 e mesma rede 2 + [(4-j6)||(3+j4)].')

add('L25',21,4,'Impedancia AC',[
    'Ache Zin em retangular. Serie 25+j15 ohm; ramos 20-j50 e 30+j10 ohm.'
],live=recipe(('Z1','z2+z3','ohm','Ramo 1: 20-j50'),('Z2','z4+z5','ohm','Ramo 2: 30+j10'),
    ('Zp','1/(1/Z1+1/Z2)','ohm','Paralelo: Zp=Z1||Z2'),
    ('Zin','z0+z1+Zp','ohm','Zin=Rserie+ZLserie+Zp')),
    ops=[('term',40,100,'a'),('term',40,195,'b'),
    ('res_h',40,100,95,'25'),('imp_h',95,100,160,'j15'),
    ('imp_v',160,100,145,'-j50'),('res_v',160,145,195,'20'),
    ('res_v',270,100,145,'30'),('imp_v',270,145,195,'j10'),
    ('wire',160,100,270,100),('wire',40,195,270,195),('gnd',40,195)],
    engine={'omega':1},anchors={'Zin':51.09756097560975+9.878048780487804j})

alias('L25',22,4,'p10_1','Mesmo circuito e fonte 2 cos(10t) V do problema 10.1.')

add('L25',23,4,'Analise Nodal AC',[
    'Is=8/_45 A. Rin=2, Z1=8+j6, Zsh=-j1, Z2=4+j5, Zo=-j2 ohm.',
    'Fonte dependente 2Vx para cima; Vx sobre Rin. Ache Vo usando KCL.',
    'Vo positivo no topo de Zo. Ganho dependente em A/V.'
],live=recipe(('Zdir','z5+z6','ohm','Ramo direito: Zdir=Z2+Zo'),
    ('Ym','1/z2+1/z4+1/Zdir','S','No medio: Ym Vm=(1/Z1+g)Vx'),
    ('H','(1/z2+c3)/Ym','','H=Vm/Vx'),
    ('Yx','1/z1+(1-H)/z2','S','No esquerdo: Is=Yx Vx'),
    ('Vx','c0/Yx','V','Vx=Is/Yx',2),('Vm','H*Vx','V','Vm=H Vx',2),
    ('Vo','Vm*z6/Zdir','V','Divisor: Vo=Vm Zo/Zdir',2),
    ('check','guard(abs(Vo-i6*z6)<max(abs(Vo),1e-30)*1e-3)','','',0),flags=1),
    ops=[('isrc_h',30,90,75,'8/_45A',True),('res_v',75,90,195,'2'),
    ('imp_h',75,90,175,'8+j6'),('dis_v',125,110,195,'2Vx',True),
    ('imp_v',175,90,195,'-j1'),('imp_h',175,90,285,'4+j5'),
    ('imp_v',285,90,195,'-j2'),('wire',175,90,175,110),
    ('wire',125,110,175,110),('wire',30,90,30,195),
    ('wire',30,195,285,195),('lbl','Vx',96,154),('gnd',30,195)],
    engine={'omega':1,'dep_resolve':{3:{'kind':'voltage','node_op_index':1}}},
    anchors={'Vo':-11.122828086791424-1.753511583199811j})

add('L25',24,4,'Superposicao AC',[
    'Is=12 cos(6t+10deg) A; Vs=50 sen(2t) V. Ache v(t).',
    'Rshunt=16, Rserie=20, L=5H. Fontes com frequencias diferentes.',
    'Resolva cada fonte na sua w. Some as parcelas no TEMPO, nao os fasores.'
],params=[('wV_rad_s',2),('t_s',.01)],live=recipe(
    ('dom','guard(wV_rad_s>0 and omega>0)','','',0),
    ('ZLi','z3','ohm','Indutor na frequencia de Is'),
    ('ZLv','complex(0,wV_rad_s*c3)','ohm','Indutor na frequencia de Vs'),
    ('Zpi','1/(1/z1+1/(z2+ZLi))','ohm','Vs anulada: Rshunt||(Rserie+ZLi)'),
    ('VI','c0*Zpi','V','Parcela de Is: VI=Is Zpi',2),
    ('solve_i','solve(omega,1)','','',0),
    ('check_i','guard(abs(VI-i1*z1)<max(abs(VI),1e-30)*1e-3)','','',0),
    ('VV','c4*z1/(z1+z2+ZLv)','V','Parcela de Vs: VV=Vs R/(R+Zs)',2),
    ('solve_v','solve(wV_rad_s,16)','','',0),
    ('check_v','guard(abs(VV-i1*z1)<max(abs(VV),1e-30)*1e-3)','','',0),
    ('wi','omega','rad/s','vi(t)=|VI|cos(wi t+arg VI)'),
    ('wv','wV_rad_s','rad/s','vv(t)=|VV|cos(wv t+arg VV)'),
    ('vi_t','abs(VI)*cos(wi*t_s*180/pi+arg(VI))','V','Parcela temporal de Is'),
    ('vv_t','abs(VV)*cos(wv*t_s*180/pi+arg(VV))','V','Parcela temporal de Vs'),
    ('v_t','vi_t+vv_t','V','v(t)=vi(t)+vv(t); nao existe V unico')),
    ops=[('isrc_v',40,100,195,'12/_10A',True),('res_v',135,100,195,'16'),
    ('res_h',135,100,210,'20'),('ind_h',210,100,285,'5H'),
    ('vsrc_v',285,100,195,'50/_-90V'),('wire',40,100,135,100),
    ('wire',40,195,285,195),('lbl','V',125,78),('gnd',135,195)],
    engine={'omega':6},anchors={'VI':132.19999428193663+65.92505086481198j,
    'VV':-5.730659025787966-20.630372492836674j})

add('L25',25,4,'Thevenin AC',[
    'Use transformacao de fontes para Vo. Vs=20/_0 V.',
    'Rserie=4, shunt j2; depois -j3 em serie, shunt 2;',
    'depois j4 em serie e carga -j2. Vo positivo no topo da carga.'
],live=recipe(('IN1','c0/z1','A','Vs+R -> Norton: IN1=Vs/R',2),
    ('Zp1','1/(1/z1+1/z2)','ohm','Zp1=Rserie||Zshunt'),
    ('VT1','IN1*Zp1','V','Norton -> Thevenin: VT1=IN1 Zp1',2),
    ('Zs1','Zp1+z3','ohm','Zs1=Zp1+ZCserie'),
    ('IN2','VT1/Zs1','A','Segundo Norton: IN2=VT1/Zs1',2),
    ('Zp2','1/(1/Zs1+1/z4)','ohm','Zp2=Zs1||Rshunt'),
    ('VT2','IN2*Zp2','V','Segundo Thevenin: VT2=IN2 Zp2',2),
    ('Vo','VT2*z6/(Zp2+z5+z6)','V','Divisor final: Vo=VT2 Zo/(Zp2+ZL+Zo)',2),
    ('check','guard(abs(Vo-i6*z6)<max(abs(Vo),1e-30)*1e-3)','','',0),flags=1),
    ops=[('vsrc_v',40,90,195,'20V'),('res_h',40,90,115,'4'),
    ('imp_v',115,90,195,'j2'),('imp_h',115,90,190,'-j3'),
    ('res_v',190,90,195,'2'),('imp_h',190,90,270,'j4'),
    ('imp_v',270,90,195,'-j2'),('wire',40,195,270,195),('gnd',40,195)],
    engine={'omega':1},anchors={'Vo':3.5294117647058836-5.882352941176471j})

add('L25',26,5,'Potencia AC',[
    'Z=20-j60 ohm, V=127/_0 V RMS. Ache a potencia media absorvida.',
    'Convencao RMS: S=V conj(I), sem dividir por 2.'
],live=recipe(('Z','z1','ohm','Impedancia da carga'),
    ('I','c0/Z','A','I=V/Z',2),('S','c0*conj(I)','VA','S=Vrms conj(Irms)'),
    *power_summary()),ops=[('vsrc_v',40,90,195,'127V'),
    ('wire',40,90,265,90),('imp_v',265,90,195,'20-j60'),
    ('wire',40,195,265,195),('gnd',40,195)],
    engine={'omega':1},anchors={'S':80.645-241.935j})

add('L25',27,5,'Thevenin AC',[
    'Vs=10/_0 V RMS; Rserie=4, ramo 8-j6, reatancia serie final j5.',
    'Determine ZL para maxima potencia media e o valor de Pmax.',
    'ZL e desconhecida: o desenho mostra o porto sem carga.'
],live=recipe(('Zramo','z2+z3','ohm','Ramo shunt: Zramo=R+ZC'),
    ('Vth','c0*Zramo/(z1+Zramo)','V','Sem carga: Vth=Vs Zramo/(R+Zramo)',2),
    ('Zp','1/(1/z1+1/Zramo)','ohm','Fonte anulada: Zp=Rserie||Zramo'),
    ('Zth','Zp+z4','ohm','Zth=Zp+ZLserie'),
    ('dom','guard(real(Zth)>0)','','',0),
    ('ZLopt','conj(Zth)','ohm','Maxima transferencia: ZL=conj(Zth)'),
    ('Iopt','Vth/(Zth+ZLopt)','A','Corrente com a carga otima',2),
    ('Pmax','abs(Vth)**2/(4*real(Zth))','W','Pmax=|Vth RMS|^2/(4 Re Zth)')),
    ops=[('vsrc_v',40,90,195,'10V'),('res_h',40,90,145,'4'),
    ('res_v',145,90,145,'8'),('imp_v',145,145,195,'-j6'),
    ('imp_h',145,90,265,'j5'),('wire',40,195,265,195),
    ('term',265,90,'a'),('term',265,195,'b'),('gnd',40,195)],
    engine={'omega':1},anchors={'Zth':2.933333333333333+4.466666666666667j,
    'Pmax':4.734848484848484})

p,r,o,g=wave_load(120,-20,4,-20,100*3.141592653589793)
add('L25',28,5,'Potencia AC',[
    'i(t)=4 cos(100 pi t-20deg) A; v(t)=120 cos(100 pi t-20deg) V.',
    'Ache |S|, P, FP e o circuito equivalente a partir de Z=V/I.',
    'No original, Z=30 ohm: resistor puro; RMS=valor de pico/sqrt(2).'
],p,r,o,g,anchors={'S':240,'Z':30})

p,r,o,g=wave_load(179,-10,3.5,50,377)
add('L25',29,5,'Potencia AC',[
    'v(t)=179 cos(377t-10deg) V; i(t)=3.5 cos(377t+50deg) A.',
    'Ache S, |S|, P, Q, Z e o tipo de carga. I entra no positivo.',
    'Q<0: capacitiva; Q>0: indutiva; Q=0: resistiva.'
],p,r,o,g,anchors={'S':156.625-271.2824577354754j})

p,r,o,g=rated_load(127,15000,.886)
add('L25',30,5,'Potencia AC',[
    'Carga: V=127 V RMS, |S|=15 kVA, FP=0.886 atrasado.',
    'Ache P, Q, Ipico e Z. Q_sinal=+1 atraso, -1 avanco.'
],p,r,o,g,anchors={'S':13290+6955.278570984774j})

add('L25',31,5,'Potencia AC',[
    'Fonte=220/_0 V RMS; linha Z=4+j2; carga Z=15-j10 ohm.',
    'Determine potencias ativa e reativa fornecidas pela fonte.',
    'Sfonte=Slinha+Scarga. Positivo: potencia fornecida.'
],live=recipe(('Zlinha','z1+z2','ohm','Zlinha=Rlinha+ZLlinha'),
    ('Zcarga','z3+z4','ohm','Zcarga=Rcarga+ZCcarga'),
    ('Ztotal','Zlinha+Zcarga','ohm','Serie: Ztotal=Zlinha+Zcarga'),
    ('I','c0/Ztotal','A','I=Vs/Ztotal',2),
    ('Slinha','Zlinha*abs(I)**2','VA','Slinha=Zlinha |Irms|^2'),
    ('Scarga','Zcarga*abs(I)**2','VA','Scarga=Zcarga |Irms|^2'),
    ('S','c0*conj(I)','VA','Fonte fornece S=Vs conj(I)'),
    *power_summary()),
    ops=[('vsrc_v',35,100,195,'220V'),('res_h',35,100,110,'4'),
    ('imp_h',110,100,190,'j2'),('res_v',285,100,145,'15'),
    ('imp_v',285,145,195,'-j10'),('wire',190,100,285,100),
    ('wire',35,195,285,195),('gnd',35,195)],
    engine={'omega':1},anchors={'S':2163.764705882353-911.0588235294116j})

add('L25',32,6,'Potencia AC',[
    'Carga P=4kW, V=127V RMS, f=60Hz, FP=0.7 atrasado.',
    'Ache o capacitor shunt que corrige FP para 0.95.',
    'P permanece igual. FPnovo>=FPantigo para correcao por capacitor.'
],params=[('P_W',4000),('V_V',127),('f_Hz',60),('FPantigo',.7),('FPnovo',.95)],
    live=recipe(('dom','guard(P_W>0 and V_V>0 and f_Hz>0 and FPantigo>0 and FPantigo<1 and FPnovo>=FPantigo and FPnovo<=1)','','',0),
    ('phi1','acos(FPantigo)','deg','Angulo antes da correcao'),
    ('phi2','acos(FPnovo)','deg','Angulo depois da correcao'),
    ('Q1','P_W*tan(phi1)','VAR','Q1=P tan(phi1)'),
    ('Q2','P_W*tan(phi2)','VAR','Q2=P tan(phi2)'),
    ('QC','Q1-Q2','VAR','Capacitor compensa QC=Q1-Q2'),
    ('w','2*pi*f_Hz','rad/s','w=2pi f'),
    ('C','QC/(w*V_V**2)','F','QC=w C V^2 -> C=QC/(w V^2)')),
    anchors={'C':.00045491069605762673})

add('L25',33,6,'Potencia AC',[
    'Carga Q=140kVAR, FP=0.85 atrasado, V=110V RMS, f=60Hz.',
    'Ache capacitancia shunt para FP=1 (unitario).',
    '140kVAR e potencia REATIVA, nao potencia ativa.'
],params=[('Q_VAR',140000),('FPantigo',.85),('V_V',110),('f_Hz',60),('FPnovo',1)],
    live=recipe(('dom','guard(Q_VAR>0 and V_V>0 and f_Hz>0 and FPantigo>0 and FPantigo<1 and FPnovo>=FPantigo and FPnovo<=1)','','',0),
    ('phi1','acos(FPantigo)','deg','Angulo original: acos(FPantigo)'),
    ('P','Q_VAR/tan(phi1)','W','Q=P tan(phi1) -> P=Q/tan(phi1)'),
    ('Qnovo','P*tan(acos(FPnovo))','VAR','Qnovo=P tan(acos(FPnovo))'),
    ('QC','Q_VAR-Qnovo','VAR','QC=Qoriginal-Qnovo'),
    ('C','QC/(2*pi*f_Hz*V_V**2)','F','C=QC/(2pi f V^2)')),
    anchors={'C':.030691035857941255})

p,r=motor(5600,220,18.2)
add('L25',34,6,'Trifasico',[
    'Motor Y equilibrado: P=5.6kW, VL=220V RMS e IL=18.2A.',
    'Determine o fator de potencia do motor.'
],p,r,anchors={'FP':.8074828939715046})

alias('L25',35,6,'e_r2a_03','Mesma carga delta: P=5kW, FP=0.8, VL=380V RMS.')

p,r,o,g=y_three_wire(127,'10+j8','5-j2')
add('L25',36,6,'Trifasico',[
    'Y-Y, tres fios: Van=127/_0, Vbn=127/_-120, Vcn=127/_-240 V RMS.',
    'Zlinha=5-j2, Zcarga=10+j8 ohm por fase. Fonte ideal (Zs=0).',
    'Ache P e Q totais na fonte e na carga. Neutro N nao esta ligado a n.',
    'Zs aparece sem valor no desenho; nao ha queda interna especificada.'
],p,r,o,g,anchors={'Ia':7.298850574712644-2.9195402298850577j},
    notes='Desenho Y-Y: nao confundir a carga estrela com delta. Zs sem valor: fonte ideal.')

p,r,o,g=y_three_wire(440,'6-j8')
add('L25',37,6,'Trifasico',[
    'Y-Y equilibrado, ABC, tres fios: Van=440/_0 V RMS, Zfase=6-j8 ohm.',
    'Determine correntes de linha. Neutros n e N separados.',
    'Apos desequilibrar valores, o app recalcula o deslocamento do neutro.'
],p,r,o,g,anchors={'Ia':26.4+35.2j})

p,r,o,g=delta_with_lines(100,'1+j2','12+j12')
add('L25',38,6,'Trifasico',[
    'Y-delta, ABC, Van=100/_0 V RMS. Zdelta=12+j12, Zlinha=1+j2 ohm.',
    'Determine correntes de linha. Zs da fonte nao informada: fonte ideal.',
    'No caso equilibrado, Zdelta/3 vira a carga Y equivalente.'
],p,r,o,g,anchors={'Ia':8.19672131147541-9.83606557377049j},
    notes='Zs sem valor no desenho: fonte ideal. Nao omitir Zlinha=1+j2.')

p,r,o,g=three_delta(230,'10+j8')
add('L25',39,7,'Trifasico',[
    'Delta-delta equilibrado, ABC: VP=230/_0 V RMS, Zdelta=10+j8 ohm.',
    'Ache IAC (A -> C). VP da fonte delta e Vab, nao Van.',
    'Fonte desenhada como Y equivalente. IAC=-ICA.'
],p,r,o,g,anchors={'Iac':-2.7041874570937012-17.75523432136713j},
    notes='O texto chama a tensao de fase delta de VAN. Interpretar VP como Vab conforme a figura.')

p,r,o,g=y_three_wire(440/3**.5,'10-j8','3+j2',-20)
add('L25',40,7,'Trifasico',[
    'Delta-Y, ABC, tres fios: Vab=440/_10, Vbc=440/_250, Vca=440/_130 V RMS.',
    'Zcarga Y=10-j8; Zlinha=3+j2 ohm por fase. Ache correntes de linha.',
    'Fonte Y equivalente: Van=Vab/sqrt(3) /_-30deg. Neutro da carga flutua.'
],p,r,o,g,anchors={'Ia':17.680929455984135+1.4769839335593193j})
