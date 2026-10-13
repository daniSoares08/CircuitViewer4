"""Exercise-specific targets and design equations, linked to component registers."""
from content.live_solutions import recipe, power_summary

def special_recipe(key,t,topo,ops):
    c=t['comps']
    if key=='p9_49':
        return recipe(('Ix','polar(p0,p1)','A','Ix dado: seno -> fase -90 graus',2),('Vx','Ix*z3','V','Vx=Ix ZC',2),
            ('Vm','Ix*(z2+z3)','V','Vm=Ix(R1+ZC)',2),('Is','Ix+Vm/z1','A','KCL: Is=Ix+Vm/ZL',2),
            ('Vs','Vm+Is*z0','V','Vs=Vm+Is R2',2),('w','p2','rad/s','vs(t)=|Vs|cos(wt+arg(Vs))'))
    if key in ('p9_51','p9_52'):
        rows=[('Vo','polar(p0,p1)','V','Tensao de saida fornecida',2)]
        if key=='p9_51':rows += [('Io','Vo/z3','A','Io=Vo/Rsaida',2),('Vi','Vo+Io*(z1+z2)','V','Vi=Vo+Io(ZC+ZL)',2)]
        else:rows += [('Io','Vo*(1/z1+1/z3)','A','Io=Vo(1/Rsaida+1/ZL)',2),('Vi','Vo+Io*z2','V','Vi=Vo+Io ZC',2)]
        rows += [('Is','Io+Vi/z0','A','KCL: Is=Io+Vi/Rentrada',2),('w','omega','rad/s','is(t)=|Is|cos(wt+arg(Is))')]
        return recipe(*rows)
    if key=='p9_54':
        return recipe(('Io','polar(p0,p1)','A','Corrente de saida fornecida',2),('Vout','Io*z5','V','Vout=Io Rsaida',2),
            ('Vr','Vout+Io*z4','V','Vr=Vout+Io ZCsaida',2),('It','Io+Vr/z3','A','KCL no lado direito',2),
            ('Vl','-It/(1/(z0+z1)+1/z2)','V','KCL: Vl YladoEsquerdo=-It',2),('Vs','Vl-Vr','V','Fonte: positivo esquerdo',2))
    if key=='p9_55':
        return recipe(('Vo','polar(p0,p1)','V','Tensao de saida fornecida',2),('Io','Vo/z3','A','Io=Vo/ZL',2),
            ('Vm','(c0-z1*Io)/(1+z1/z2)','V','KCL: (Vs-Vm)/R=Vm/ZC+Io',2),('Z','(Vm-Vo)/Io','ohm','Z=(Vm-Vo)/Io'))
    if key=='p9_34':
        return recipe(('w0','1/sqrt(c2*c3)','rad/s','Vo sobre LC: ZL+ZC=0'),
            ('f0','w0/(2*pi)','Hz','f0=w0/(2pi)'),('I','c0/(z1+z2+z3)','A','I=Vs/(R+ZC+ZL)',2),
            ('Vo','I*(z2+z3)','V','Vo=I(ZL+ZC); zero em w0',2))
    if key=='p9_40':
        rows=[]
        for w in (1,5,10):
            k=str(w)
            rows += [('Zp'+k,'1/(1/c2+complex(0,%d*c3))'%w,'ohm','R e C em paralelo'),
                     ('I'+k,'c0/(complex(0,%d*c1)+Zp%s)'%(w,k),'A','Io=Vs/(ZL+Zp)',2)]
        return recipe(*rows)
    if key=='p9_77':
        return recipe(('ZC','z1','ohm','ZC=1/(jwC)'),('H','ZC/(z0+ZC)','','H=ZC/(R+ZC)',2),
            ('fase','arg(H)','deg','fase=arg(H): negativo=atraso'),('f45','1/(2*pi*c0*c1)','Hz','|fase|=45: f=1/(2pi RC)'))
    if key=='p9_79':
        # Loaded ladder, reducing from the output back toward the input.
        return recipe(('Z3','z4+z5','ohm','Ultimo ramo: R3+ZL3'),('Z2','1/(1/z3+1/Z3)','ohm','Z2=ZL2||(R3+ZL3)'),
            ('Z1','1/(1/z1+1/(z2+Z2))','ohm','Z1=ZL1||(R2+Z2)'),
            ('H','Z1/(z0+Z1)*Z2/(z2+Z2)*z5/Z3','','H=produto dos divisores carregados',2),
            ('fase','arg(H)','deg','fase>0: adianta; fase<0: atrasa'),('Vo','p0*H','V','Vo=Vi H',2))
    if key=='p9_89':
        return recipe(('Cideal','1/(omega**2*c2)','F','Cideal=1/(w^2 L)'),('Zatual','z0+z1+z2','ohm','Zatual=ZC+R+ZL'),
            ('fase','arg(Zatual)','deg','Carga resistiva quando fase=0'))
    if key=='p9_91':
        return recipe(('Zp','1/(1/z1+1/z2)','ohm','Zp=R||jwL'),('Cideal','1/(omega*imag(Zp))','F','Cideal=1/[w Im(Zp)]'),
            ('Zatual','z0+Zp','ohm','Zatual=ZC+Zp'))
    if key=='p9_88':
        return recipe(('ZT','z1+z2+z3+z4','ohm','Serie: ZT=soma dos componentes'),('I','c0/ZT','A','I=Vs/ZT',2))
    if key=='p10_20':
        return recipe(('Yp','1/z2+1/z3','S','Yp=1/ZL+1/ZC'),('H','1/(1+z1*Yp)','','H=1/(1+R Yp)',2),
            ('Vo','c0*H','V','Vo=Vs H',2),('w0','1/sqrt(c2*c3)','rad/s','Ressonancia LC: w0=1/sqrt(LC)'))
    if key=='p10_21':
        return recipe(('Hc','z3/(z1+z2+z3)','','(a) Hc=ZC/(R+ZL+ZC)',2),('Hl','z2/(z1+z2+z3)','','(b) Hl=ZL/(R+ZC+ZL)',2),
            ('w0','1/sqrt(c2*c3)','rad/s'),('Hc0','1','','w=0: C aberto, L curto'),('Hl0','0','','w=0: queda no L nula'),
            ('HcInf','0','','w infinito: C curto'),('HlInf','1','','w infinito: L aberto'),
            ('HcRes','1/complex(0,w0*c3*c1)','','Em w0: ZL+ZC=0',2),('HlRes','complex(0,w0*c2)/c1','','',2))
    if key=='p10_22':
        return recipe(('Zp','1/(1/(z1+z2)+1/z4)','ohm','Zp=(R2+ZL)||ZC'),('H','Zp/(z3+Zp)','','H=Zp/(R1+Zp)',2),('Vo','c0*H','V','Vo=Vs H',2))
    if key=='p10_23':
        return recipe(('Y','1/(z1+z2)+1/z4','S','Y=1/(ZL+ZC1)+1/ZC2'),('H','1/(1+z3*Y)','','H=1/(1+R Y)',2),('Vo','c0*H','V','Vo=Vs H',2))
    if key=='p10_41':
        return recipe(('w1','p0','rad/s'),('w2','p1','rad/s'),('H1','c2/(c2+1/complex(0,w1*c1))','','H1=R/(R+1/jw1C)',2),
            ('H2','c2/(c2+1/complex(0,w2*c1))','','H2=R/(R+1/jw2C)',2),('Vo1','c0*H1','V','Vo1: parcela na frequencia w1',2),
            ('Vo2','polar(p2,p3-90)*H2','V','Vo2: converta seno para cosseno',2))
    if key in ('p10_44','p10_45','p10_46','p10_47','p10_48'):
        # MNA is re-run independently with the correct physical reactances.
        groups={'p10_44':[(0,'p0'),(4,'p1')], 'p10_45':[(0,'p0'),(3,'p1')],
                'p10_46':[(0,'p0'),(3,'p1'),(5,'0')],
                'p10_47':[(0,'p0'),(5,'0'),(2,'p1')],
                'p10_48':[(0,'p0'),(4,'0'),(6,'p1')]}[key]
        rows=[]
        for n,(source,w) in enumerate(groups):
            # A 180-degree edit can leave sinf(pi) rounding residue. Reject
            # genuinely complex DC data, not a real source with float noise.
            if w=='0':rows.append(('dc_guard%d'%n,
                'guard(abs(imag(c%d))<max(abs(c%d),1e-30)*1e-6)'%(source,source),'','',0))
            rows.append(('solve%d'%n,'solve(%s,%d)'%(w,1<<source),'','',0))
            if key=='p10_44':out='v%d-v%d'%(c[1]['na'],c[1]['nb'])
            elif key=='p10_45':out='i1'
            elif key=='p10_46':out='v%d-v%d'%(c[2]['na'],c[2]['nb'])
            elif key=='p10_47':out='i7'
            else:out='-i2'
            rows.extend([('w%d'%n,w,'rad/s','w distintas: some senoides no tempo'),('Parcela%d'%n,out,'V' if key in ('p10_44','p10_46') else 'A','Resposta somente desta fonte',2)])
        return recipe(*rows)
    if key=='p10_69':
        return recipe(('H','-z2/z1','','AOP inversor: H=-R/ZC',2),('Vo','c0*H','V','Vo=Vs H',2),('wRC','1/(c1*c2)','rad/s','wRC=1/(RC)'))
    if key in ('p10_71','p10_72','p10_73','p10_75','p10_76','p10_77','p10_78','p10_79','p10_80','p11_9','p11_10'):
        from content.live_networks import opamp_constraints
        amps=opamp_constraints(ops,topo)
        rows=[('Vo','v%d'%amps[-1][0],'V','AOP ideal: V+=V- e Ient=0',2),
            ('H','Vo/c0','','H=Vo/Vs',2)]
        if key=='p10_73':rows += [('Is','-i0','A','KCL na entrada: Is=-Ifonte',2),('Zent','c0/Is','ohm','Zent=Vs/Is')]
        if key=='p10_75':rows += [('Ganho','abs(H)','','Ganho=|Vo/Vs|'),('Fase','arg(H)','deg','Fase=arg(Vo/Vs)')]
        if key=='p10_76':rows += [('Io','i3','A','Io=(Vjuncao-Vo)/Rf',2)]
        if key=='p10_72':rows += [('Io','i2','A','Io=Vo/Rcarga',2)]
        if key in ('p11_9','p11_10'):
            for k,comp in enumerate(c):
                if comp['kind'] in (0,8):rows += [('P%d'%k,'real(s%d)/2'%k,'W','P=Re(V conj(I))/2 (pico)')]
        return recipe(*rows,flags=1,opamps=amps)
    if key=='p10_74':
        return recipe(('Zi','z1+z2','ohm','Zi=R1+1/(jwC1)'),('Zf','z3+z4','ohm','Zf=R2+1/(jwC2)'),
            ('H','-Zf/Zi','','H=-Zf/Zi',2),('H0','-c2/c4','','w=0: H=-C1/C2'),('Hinf','-c3/c1','','w infinito: H=-R2/R1'),
            ('w1','1/(c1*c2)','rad/s','w1=1/(R1C1)'),('w2','1/(c3*c4)','rad/s','w2=1/(R2C2)'),('Vo','c0*H','V','Vo=Vs H',2))
    if key in ('p11_76','p11_77','p11_78','p11_79','p11_80'):
        if key=='p11_76':voltage='v%d'%c[5]['nb'];current='-i5'
        elif key=='p11_77':voltage='v%d'%c[4]['na'];current='-i0'
        elif key in ('p11_78','p11_79'):voltage=('-' if key=='p11_79' else '')+'v%d'%c[1]['nb'];current='-i0'
        else:voltage='c0';current='i1'
        factor='/2' if t['flags2']&1 else ''
        return recipe(('Vw',voltage,'V','Tensao na bobina de potencial',2),('Iw',current,'A','Corrente com polaridade da bobina',2),
            ('W','real(Vw*conj(Iw))'+factor,'W','W=Re(Vpico conj(Ipico))/2' if factor else 'W=Re(Vrms conj(Irms))'),flags=1)
    if key in ('p12_66','p12_71','p12_72','p12_73','p12_74'):
        sources=[k for k,comp in enumerate(c) if comp['kind']==1]
        a,b,d=sources
        rows=[('Ia','-i%d'%a,'A','Correntes de linha: -Ifonte',2),
              ('Ib','-i%d'%b,'A','',2),('Ic','-i%d'%d,'A','',2)]
        if key=='p12_66':
            rows += [('In','-(Ia+Ib+Ic)','A','In=-(Ia+Ib+Ic)',2)]
            for n,k in enumerate(sources):
                rows += [('W%d'%(n+1),'real(c%d*conj(I%s))'%(k,'abc'[n]),'W','Wk=Re(Vkn conj(Ik))')]
            rows += [('P','W1+W2+W3','W','P=W1+W2+W3')]
        else:
            rows += [('Vab','c%d-c%d'%(a,b),'V','Bobina W1: Vab',2),
                ('Vcb','c%d-c%d'%(d,b),'V','Bobina W2: Vcb',2),
                ('W1','real(Vab*conj(Ia))','W','W1=Re(Vab conj(Ia))'),
                ('W2','real(Vcb*conj(Ic))','W','W2=Re(Vcb conj(Ic))'),
                ('P','W1+W2','W','P=W1+W2: tambem desequilibrado')]
        rows += [('S','-('+'+'.join('s%d'%k for k in sources)+')','VA','St=soma das potencias fornecidas'),*power_summary()[1:]]
        return recipe(*rows,flags=1)
    if key in ('p10_93','p10_94','p10_95'):
        if key=='p10_95':rows=[('Leq','c3+c4','H','Leq=L1+L2'),('w0','1/sqrt(c2*Leq)','rad/s','w0=1/sqrt(C Leq)')]
        else:rows=[('Ceq','c3*c4/(c3+c4)','F','Ceq=C1C2/(C1+C2)'),('w0','1/sqrt(c2*Ceq)','rad/s','w0=1/sqrt(L Ceq)')]
        rows += [('f0','w0/(2*pi)','Hz','f0=w0/(2pi)'),('Av','-c0/c1','','Av=-Rf/Ri'),
                 ('Beta','-c4/c3' if key!='p10_95' else '-c3/c4','','Beta=-C1/C2' if key!='p10_95' else 'Beta=-L2/L1'),('Laco','Av*Beta','','Barkhausen: ganho de laco >=1')]
        if key=='p10_94':rows += [('Lprojeto','1/((2*pi*p0)**2*Ceq)','H','Lprojeto=1/[(2pi fpedido)^2 Ceq]')]
        return recipe(*rows)
    if key=='p10_89':
        return recipe(('Leq','c1*c3*c5*c4/c2','H','Leq=R1 R3 R4 C/R2'),('Zin','complex(0,omega*Leq)','ohm','Zin=jw Leq'),
            ('Iin','c0/Zin','A','Iin=Vin/Zin',2))
    if key=='p10_90':
        return recipe(('w0','1/sqrt(c1*c3*c2*c4)','rad/s','w0=1/sqrt(Ra Rb Ca Cb)'),('f0','w0/(2*pi)','Hz'),
            ('Beta0','1/(1+c1/c3+c4/c2)','','Beta0=1/(1+Ra/Rb+Cb/Ca)'),('Avmin','1/Beta0','','Avmin=1/Beta0'),
            ('DivR','c6/(c5+c6)','','DivR=R2/(R1+R2)'),('Vo0','c0*(Beta0-DivR)','V','Ponte: Vo0=Vi(Beta0-DivR)',2),
            ('H','1/(1+(z1+z2)*(1/z3+1/z4))','','H da rede RC na w atual',2))
    if key=='p10_91':
        return recipe(('w0','1/sqrt(c1*c2)','rad/s','w0=1/sqrt(LC)'),('f0','w0/(2*pi)','Hz'),
            ('Av','1+c4/c5','','Av=1+Rf/Ri'),('Rlim','(Av-1)*c3','ohm','Limite de partida: R=(Av-1)Rp'),
            ('Laco','Av*c3/(c3+c6)','','Na ressonancia: laco=Av Rp/(Rp+R)'),('Vteste','c0*Laco','V','Resposta a uma excitacao de teste',2))
    if key=='p10_92':
        return recipe(('w0','1/sqrt(c1*c2)','rad/s','w0=1/sqrt(LC)'),('f0','w0/(2*pi)','Hz'),
            ('Av','1+c3/c5','','Av=1+Rf/Ri'),('Rolim','(Av-1)*c4','ohm','Limite: Ro=(Av-1)Rp'),
            ('Laco','Av*c4/(c4+c6)','','Na ressonancia: laco=Av Rp/(Rp+Ro)'),('Vteste','c0*Laco','V','Resposta a uma excitacao de teste',2))
    if key=='p10_96':
        return recipe(('H','1/(1+(z1+z2)*(1/z3+1/z4))','','H da rede RL de realimentacao',2),
            ('w0','sqrt(c1*c4/(c2*c3))','rad/s','w0=sqrt(Ra Rb/(La Lb))'),('f0','w0/(2*pi)','Hz'),
            ('Av','1+c0/c5','','Av=1+R2/R1'),('Avmin','1+c1/c4+c2/c3','','Avmin=1+Ra/Rb+La/Lb'),
            ('R2ideal','(Avmin-1)*c5','ohm','R2ideal=(Avmin-1)R1'))
    return None

EXTRA_PARAMS={
 'p9_49':[('Ix_A',.5),('Ix_deg',-90),('w_rad_s',200)],
 'p9_51':[('Vo_V',10),('Vo_deg',0)],'p9_52':[('Vo_V',8),('Vo_deg',30)],
 'p9_54':[('Io_A',2),('Io_deg',0)],'p9_55':[('Vo_V',4),('Vo_deg',0)],
 'p9_79':[('Vin_V',120)],
 'p10_41':[('w1',2),('w2',4),('Vm2',4),('phi2',0)],
 'p10_44':[('wIs',6),('wVs',2)],'p10_45':[('wVs1',10),('wVs2',4)],
 'p10_46':[('wVs',3),('wIs',2)],'p10_47':[('wVs',1),('wIs',3)],
 'p10_48':[('wVs',2000),('wIs',4000)],'p10_94':[('fpedido_Hz',50000)],
}
