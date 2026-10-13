"""Live mathematical recipes. Every displayed number comes from current inputs.

These definitions are independent of authored textbook answer strings. Source
corrections live here until merged into the chapter authoring modules.
"""
from live_recipe import step

def recipe(*rows, **options):
    steps=[]
    for row in rows:
        key,expr,*rest=row
        unit=rest[0] if rest else ''
        formula=rest[1] if len(rest)>1 else ''
        mode=rest[2] if len(rest)>2 else 1
        steps.append(step(key,expr,unit,formula,mode))
    return dict(options,steps=steps)

def polar_rows(key,mag,deg,unit='',w=None):
    rows=[(key,'polar(%s,%s)'%(mag,deg),unit,'Fasor = modulo /_ fase',2)]
    if w:rows.append(('w_'+key,w,'rad/s','x(t)=|X|cos(wt+arg(X))'))
    return rows

def power_summary(expr='S',prefix=''):
    return [(prefix+'P','real('+expr+')','W','P = Re(S)'),
            (prefix+'Q','imag('+expr+')','VAR','Q = Im(S)'),
            (prefix+'Smag','abs('+expr+')','VA','|S| = sqrt(P^2+Q^2)'),
            (prefix+'FP','abs(real('+expr+'))/max(abs('+expr+'),1e-30)','','FP=|P|/|S|; S=0: indefinido (0)')]

def pf_correction(p='P',q='Q',v='V_V',f='f_Hz',target='FPnovo'):
    return [('Qalvo',p+'*tan(acos('+target+'))','VAR','Qalvo = P tan(acos(FPnovo))'),
            ('Qc',q+'-Qalvo','VAR','Qc = Qoriginal - Qalvo'),
            ('C','Qc/(2*pi*'+f+'*'+v+'**2)','F','C = Qc/(2 pi f V^2)')]

SCALAR={}
PARAM_FIX={}

def put(ch,num,*rows,params=None,**options):
    key='p%d_%s'%(ch,num)
    SCALAR[key]=recipe(*rows,**options)
    if params is not None:PARAM_FIX[key]=params

put(9,1,('T','2*pi/w_rad_s','s','T=2pi/w'),('f','w_rad_s/(2*pi)','Hz','f=w/(2pi)'),
    ('v_t','Vm_V*cos(w_rad_s*t_s*180/pi+phi_deg)','V','v(t)=Vm cos(wt+phi)'))
put(9,2,('f','w_rad_s/(2*pi)','Hz','f=w/(2pi)'),('T','2*pi/w_rad_s','s','T=2pi/w'),
    ('i_t','Im_A*cos(w_rad_s*t_s*180/pi+phi_deg)','A','i(t)=Im cos(wt+phi)'))
put(9,3,('Xa','polar(A1,ph1_deg-90)','','sen(x)=cos(x-90deg)',2),
    ('Xb','polar(A2,-90)','','Fasor da alinea b',2),('wb','w2_rad_s','rad/s'),
    ('Xc','polar(A3,ph3_deg-90)','','Fasor da alinea c',2))
put(9,4,('X','polar(Vm_V,phi_deg)','V','Exemplo: v=Vm cos(wt+phi)',2),
    ('T','2*pi/w_rad_s','s','T=2pi/w'),('f','w_rad_s/(2*pi)','Hz'))
put(9,5,('V1','polar(A1,ph1_deg-90)','V','Converta seno para cosseno',2),
    ('V2','polar(A2,ph2_deg)','V','Referencia em cosseno',2),
    ('delta','arg(V2/V1)','deg','Delta=arg(V2)-arg(V1)'))
put(9,6,('delta_a','arg(polar(1,ia_deg-va_deg))','deg','Positivo: primeiro adianta'),
    ('delta_b','arg(polar(1,v2b_deg-v1b_deg))','deg'),
    ('delta_c','arg(polar(1,yc_deg-xc_deg))','deg'))
put(9,7,('Euler','polar(1,phi_deg)','','exp(jphi)=cos(phi)+j sen(phi)'))

# Three independent subitems: the original generic A/B bank did not encode
# these expressions. Each operand below was checked on PDF page 381.
put(9,8,('a','polar(p0,p1)/complex(p2,p3)+complex(0,p4)','', 'a=A/_fase/(R+jX)+jB'),
    ('b','polar(p5,p6)/(complex(p7,p8)*complex(p9,p10))+p11/complex(p12,p13)','', 'b: opere produtos e quocientes'),
    ('c','p14+polar(p15,p16)*complex(p17,p18)','', 'c=20+(16/_-50)(5+j12)'),
    params=[('a_mag',60),('a_deg',45),('a_R',7.5),('a_X',-10),('a_j',2),
            ('b_mag',32),('b_deg',-20),('b1_R',6),('b1_X',-8),('b2_R',4),('b2_X',2),
            ('b_num',20),('b3_R',-10),('b3_X',24),('c_dc',20),('c_mag',16),('c_deg',-50),('c_R',5),('c_X',12)])
put(9,9,('a','polar(p0,p1)*(complex(p2,p3)+polar(p4,p5)/complex(p6,p7))','','Some em retangular; converta polar',2),
    ('b','polar(p8,p9)*polar(p10,p11)/(complex(p12,p13)-complex(p14,p15))','','Multiplique e divida fasores',2),
    params=[('a_mag',5),('a_deg',30),('a_R',6),('a_X',-8),('b_mag',3),('b_deg',60),('b_R',2),('b_X',1),
            ('c_mag',10),('c_deg',60),('d_mag',35),('d_deg',-50),('c_R',2),('c_X',6),('d_R',5),('d_X',1)])
put(9,10,*polar_rows('X','Xm','phi_deg','', 'w_rad_s'))
put(9,11,*sum([polar_rows('X%d'%i,'X%d_mag'%i,'X%d_deg'%i,'V' if i in (1,3) else 'mA') for i in range(1,5)],[]))
put(9,12,('X','polar(X_mag,X_deg)','','X: polar para retangular',0),
    ('Y','polar(Y_mag,Y_deg)','','',0),('a','(X+Y)*conj(X)','','(a) (X+Y)conj(X)',2),
    ('b','conj(X-Y)','','(b) conj(X-Y)',2),('c','(X+Y)/X','','(c) (X+Y)/X',2))
complex_params=[('a_R',5),('a_X',-6),('b_R',2),('b_X',8),('c_R',-3),('c_X',4),
                ('d_R',5),('d_X',-1),('e_R',4),('e_X',-6),('f_mag',240),('f_deg',75),
                ('g_mag',160),('g_deg',-30),('h_R',60),('h_X',-80),('k_R',67),('k_X',84),
                ('l_mag',20),('l_deg',32),('m_R',10),('m_X',20),('n_R',3),('n_X',4),
                ('o_R',10),('o_X',5),('q_R',16),('q_X',-20)]
for n in (13,14):
    put(9,n,('a','(complex(p0,p1)-complex(p2,p3))/(complex(p4,p5)*complex(p6,p7)+complex(p8,p9))','','a: racionalize o quociente'),
        ('b','(polar(p10,p11)+polar(p12,p13))*complex(p14,p15)/(complex(p16,p17)*polar(p18,p19))','','b: opere fasores e complexos'),
        ('c','(complex(p20,p21)/complex(p22,p23))**2*csqrt(complex(p24,p25)*complex(p26,p27))','','c: quadrado e raiz complexa'),params=complex_params)
put(9,15,('a','complex(p0,p1)*complex(p6,p7)-complex(p2,p3)*complex(p4,p5)','','det 2x2 = ad-bc'),
    ('b','polar(p8,p9)*polar(p14,p15)-polar(p10,p11)*polar(p12,p13)','','det 2x2 em fasores'),
    ('c','complex(p16,p17)*(complex(p24,p25)*complex(p32,p33)-complex(p26,p27)*complex(p30,p31))-complex(p18,p19)*(complex(p22,p23)*complex(p32,p33)-complex(p26,p27)*complex(p28,p29))+complex(p20,p21)*(complex(p22,p23)*complex(p30,p31)-complex(p24,p25)*complex(p28,p29))','','det 3x3: expansao por linha'),
    params=[('a11_R',10),('a11_X',6),('a12_R',2),('a12_X',-3),('a21_R',-5),('a21_X',0),('a22_R',-1),('a22_X',1),
            ('b11_mag',20),('b11_deg',-30),('b12_mag',-4),('b12_deg',-10),('b21_mag',16),('b21_deg',0),('b22_mag',3),('b22_deg',45),
            ('c11_R',1),('c11_X',-1),('c12_R',0),('c12_X',-1),('c13_R',0),('c13_X',0),('c21_R',0),('c21_X',1),
            ('c22_R',1),('c22_X',0),('c23_R',0),('c23_X',-1),('c31_R',1),('c31_X',0),('c32_R',0),('c32_X',1),('c33_R',1),('c33_X',1)])
put(9,16,*polar_rows('a','X1_mag','X1_deg'),*polar_rows('b','X2_mag','X2_deg'),('c','complex(X3_R,X3_X)','','cosseno - seno -> a+jb',2))
put(9,17,('V1','polar(V1_V,ph1_deg)','V','V1 = modulo /_ fase',2),('V2','polar(V2_V,ph2_deg)','V','V2 = modulo /_ fase',2),
    ('V','V1+V2','V','v(t)=|V1+V2|cos(wt+arg(V))',2),('w','w_rad_s','rad/s'))
put(9,18,*sum([polar_rows('X%d'%i,'X%d_mag'%i,'X%d_deg'%i,'', 'w%d'%i) for i in range(1,5)],[]))
put(9,19,('a','polar(p0,p1)-polar(p2,p3)','','a: some fasores em retangular',2),
    ('b','polar(p4,-90)+polar(p5,p6)','','b: sen -> cos, depois some',2),
    ('c','polar(p7,-90)+polar(p8,p9)+polar(p10,p11-90)','','c: some as tres parcelas',2),
    params=[('a1_mag',3),('a1_deg',10),('a2_mag',5),('a2_deg',-30),('b1_mag',40),('b2_mag',30),('b2_deg',-45),
            ('c1_mag',20),('c2_mag',10),('c2_deg',60),('c3_mag',-5),('c3_deg',-20)])
put(9,20,('Z','polar(V_V,V_deg)/polar(I_A,I_deg)','ohm','Z=V/I',2),('w','w_rad_s','rad/s'))
put(9,21,('F','polar(p0,p1)-polar(p2,p3-90)','','F=fasor1-fasor2',2),
    ('G','polar(p4,-90)+polar(p5,p6)','','G=fasor1+fasor2',2),
    ('H','complex(p7,-p8)/complex(0,p9)','','Integral: divida por jw',2),
    ('Hdc','-real(H)','','Integral definida desde t=0'),
    params=[('F1',5),('F1_deg',15),('F2',4),('F2_deg',-30),('G1',8),('G2',4),('G2_deg',50),('Hcos',10),('Hsin',50),('wH',40)])
put(9,22,('K','K0+complex(0,Kd*w_rad_s)+Ki/complex(0,w_rad_s)','','d/dt -> jw; integral -> 1/jw'),
    ('Y','K*polar(Vm_V,phi_deg)','','Y=K V',2),('w','w_rad_s','rad/s'))
put(9,23,('V','polar(p0,p1-90)+polar(p2,p3)','V','Converta seno e some V',2),
    ('I','polar(p4,p5)-polar(p6,p7-90)','A','Converta seno e subtraia I',2),
    params=[('Vsin',110),('Vsin_deg',30),('Vcos',220),('Vcos_deg',-90),('Icos',30),('Icos_deg',60),('Isin',20),('Isin_deg',60)])
put(9,24,('Ka','Ka_R+complex(0,Ka_X)','','Coeficiente fasorial a'),('Va','Sa_mag/Ka','V','Va=fonte/coeficiente',2),
    ('Kb','Kb_R+complex(0,Kb_X)','','Coeficiente fasorial b'),('Vb','polar(Sb_mag,Sb_deg)/Kb','V','Vb=fonte/coeficiente',2),('w','wb','rad/s'))
put(9,25,('Ia','polar(Sa_mag,Sa_deg)/complex(Ka_R,Ka_X)','A','Ia=fonte/(3+j4)',2),('wa','wa','rad/s'),
    ('Ib','polar(Sb_mag,Sb_deg)/complex(Kb_R,wb-Kb_int/wb)','A','Ib=fonte/[R+j(w-Ki/w)]',2),('wb','wb','rad/s'),
    params=[('Sa_mag',4),('Sa_deg',-45),('Ka_R',3),('Ka_X',4),('wa',2),('Sb_mag',5),('Sb_deg',22),('wb',5),('Kb_R',6),('Kb_int',10)])
put(9,26,('Zop','K0+complex(0,Kd*w_rad_s)+Ki/complex(0,w_rad_s)','','Zop=K0+jwKd+Ki/(jw)'),('I','Smag/Zop','A','I=fonte/Zop',2),('w','w_rad_s','rad/s'))
put(9,27,('K','G+complex(0,w_rad_s)+Kint/complex(0,w_rad_s)','','K=G+jw+Kint/(jw)'),('V','polar(Vs_V,Vs_deg)/K','V','V=Vs/K',2))
put(9,28,('I','Vs_V/R_ohm','A','I=V/R'),('w','w_rad_s','rad/s'))
put(9,29,('Zc','1/complex(0,w_rad_s*C_F)','ohm','Zc=1/(jwC)'),('V','polar(Im_A,phi_deg-90)*Zc','V','V=I Zc, referencia cosseno',2))
put(9,30,('V','polar(Vm_V,phi_deg)','V','V em forma fasorial',0),('IR','V/R_ohm','A','IR=V/R',2),('IC','complex(0,w_rad_s*C_F)*V','A','IC=jwC V',2))
put(9,31,('Z','complex(R_ohm,w_rad_s*L_H-1/(w_rad_s*C_F))','ohm','Z=R+j(wL-1/wC)'),('I','Vm_V/Z','A','I=V/Z',2))
put(9,32,('Z','complex(R_ohm,w_rad_s*L_H)','ohm','Z=R+jwL'),('I','polar(V_V,V_deg)/Z','A','I=V/Z',2))
put(9,33,('VL','sqrt(Vs_V**2-VR_V**2)','V','VL=sqrt(Vs^2-VR^2)'))
put(9,38,('Yrc','1/R_ohm+complex(0,w_rad_s*C_F)','S','Yrc=1/R+jwC'),('Yrlc','Yrc+1/complex(0,w_rad_s*L_H)','S','Yrlc=Yrc+1/(jwL)'),('Z','1/Yrlc','ohm','Z=1/Y'))
put(9,74,('ZL','complex(0,w_rad_s*L_H)','ohm','ZL=jwL'),('I','Vin_V/(R_ohm+ZL)','A','I=Vin/(R+jwL)',2),('VL','I*ZL','V','VL=jwL I',2),('delta','arg(VL/I)','deg','VL adianta I por 90deg'))
put(9,76,('a','arg(polar(1,a_v1_deg-a_v2_deg))','deg','Fase primeira - fase segunda'),('b','arg(polar(1,b_v1_deg-b_v2_deg))','deg'),('c','arg(polar(1,c_v1_deg-c_v2_deg))','deg'))
put(9,78,('Yalvo','1/complex(Zeq_R,Zeq_X)','S','Yalvo=1/Zeq'),
    ('B','imag(Yalvo)','S','',0),('Xserie','-2*B*Z_R**2/(1+sqrt(1-4*B**2*Z_R**2))','ohm','Im(1/Zserie)=Im(Yalvo)'),
    ('X','Z_X-Xserie','ohm','Capacitor -jX: X=Xbobina-Xserie'),('R','1/(real(Yalvo)-Z_R/(Z_R**2+Xserie**2))','ohm','1/R=Re(Yalvo)-Re(1/Zserie)'))
put(9,81,('Rx','R2_ohm*R3_ohm/R1_ohm','ohm','Rx=R2 R3/R1'),('Cx','R1_ohm*C2_F/R3_ohm','F','Cx=R1 C2/R3'))
put(9,82,('Cx','R2_ohm*Cs_F/R1_ohm','F','Cx=(R2/R1)Cs'))
put(9,83,('Lx','Ls_H*R2_ohm/R1_ohm','H','Lx=Ls R2/R1'))
put(9,84,('Lx','R2_ohm*R3_ohm*Cs_F','H','Lx=R2 R3 Cs'),('Rx','R2_ohm*R3_ohm/R1_ohm','ohm','Rx=(R2/R1)R3'))
put(9,85,('w0','1/sqrt(R2_ohm*R4_ohm*C2_F*C4_F)','rad/s','w0=1/sqrt(R2 R4 C2 C4)'),('f0','w0/(2*pi)','Hz','f0=w0/(2pi)'))
put(9,92,('Z','polar(Z_mag,Z_deg)','ohm','Z em forma complexa',0),('Y','polar(Y_S,Y_deg)','S','Y em forma complexa',0),('Zo','csqrt(Z/Y)','ohm','Zo=sqrt(Z/Y)',2),('gamma','csqrt(Z*Y)','','gamma=sqrt(ZY)',2))

# Power, RMS and scalar word problems.
put(11,3,('Vrms','Vpk_V/sqrt(2)','V','Vrms=Vpico/sqrt(2)'),('P','Vrms**2/R_ohm','W','P=Vrms^2/R'),('Qc','-Vrms**2*w_rad_s*C_F','VAR','Qc=-Vrms^2 wC'))
put(11,11,('Z','1/(1/R_ohm+complex(0,w_rad_s*C_F))','ohm','Z=1/(1/R+jwC)'),('I','polar(Ipk_A/sqrt(2),I_deg)','A','I: pico para RMS',0),('S','Z*abs(I)**2','VA','S=|I|^2 Z'),('P','real(S)','W','P=Re(S)'))
put(11,13,('ZL','complex(Zth_R,-Zth_X)','ohm','ZL=conj(Zth)'),('Pmax','Vth_pk_V**2/(8*Zth_R)','W','Pmax=Vpico^2/(8Rth)'))
put(11,22,('Idc','Ipk_A/2','A','Onda de 0 a Ip: Idc=Ip/2'),('Iac','Ipk_A/2','A'),
    ('Irms','sqrt(Idc**2+Iac**2/2)','A','Irms=sqrt(Idc^2+Iac^2/2)'),
    params=[('Ipk_A',4)])
put(11,23,('Vrms','abs(Vp_V)*sqrt(duty)','V','Vrms=Vp sqrt(duty)'),('Ton','T_s*duty','s','Ton=duty T'))
put(11,24,('Vrms','sqrt(duty*Vhi_V**2+(1-duty)*Vlo_V**2)','V','Vrms=sqrt(d Vhi^2+(1-d)Vlo^2)'))
put(11,25,('T','thi_s+tlo_s+tzero_s','s','T=thi+tlo+tzero'),
    ('Vrms','sqrt((Fhi**2*thi_s+Flo**2*tlo_s)/T)','','RMS por soma de trechos'),
    params=[('Fhi',4),('Flo',-4),('thi_s',1),('tlo_s',1),('tzero_s',1)])
put(11,26,('Vrms','sqrt(duty*V1_V**2+(1-duty)*V2_V**2)','V','RMS dos dois patamares'))
put(11,27,('Irms','abs(Ipk_A)/sqrt(3)','A','Irms=Ipico/sqrt(3)'),('T','T_s','s'))
PARAM_FIX['p11_27']=[('Ipk_A',5),('T_s',5)]
put(11,28,('T','trampa_s+tzero_s','s'),('Integral','Vpk_V**2*trampa_s/3','V^2s','Integral da rampa: Vp^2 tr/3'),
    ('Vrms','sqrt(Integral/T)','V','Vrms=sqrt(integral/T)'),('P','Vrms**2/R_ohm','W','P=Vrms^2/R'),
    params=[('Vpk_V',8),('R_ohm',2),('trampa_s',2),('tzero_s',3)])
put(11,29,('Irms','abs(Ipk_A)/sqrt(3)','A','Triangulo: Irms=Ipico/sqrt(3)'),('P','Irms**2*R_ohm','W','P=Irms^2 R'),('T','T_s','s'))
PARAM_FIX['p11_29']=[('Ipk_A',30),('R_ohm',12),('T_s',20)]
for n in (30,31):put(11,n,('Vrms','sqrt((Vramp_V**2/3+Vlow_V**2)/2)','V','RMS: rampa e patamar iguais'),('T','T_s','s'))
PARAM_FIX['p11_30']=[('Vramp_V',2),('Vlow_V',-1),('T_s',4)]
put(11,32,('Irms','sqrt(K_A_s2**2*t1_s**5/(5*T_s))','A','Irms^2=K^2 t1^5/(5T)'))
put(11,33,('T','tsub_s+tpat_s+tdes_s+tzero_s','s','T=soma das duracoes'),
    ('Integral','Ipk_A**2*((tsub_s+tdes_s)/3+tpat_s)','A^2s','Rampas: Ip^2 t/3; patamar: Ip^2 t'),
    ('Irms','sqrt(Integral/T)','A','Irms=sqrt(integral/T)'),
    params=[('Ipk_A',5),('tsub_s',1),('tpat_s',1),('tdes_s',1),('tzero_s',2)])
put(11,34,('T','trampa_s+tpatamar_s','s'),('Integral','Fpk**2*(trampa_s/3+tpatamar_s)','','Integre rampa e patamar'),
    ('RMS','sqrt(Integral/T)','','RMS=sqrt(integral/T)'),
    params=[('Fpk',6),('trampa_s',2),('tpatamar_s',1)])
put(11,35,('T','t1_s+t2_s+t3_s+t4_s+t5_s','s'),
    ('Integral','V1_V**2*t1_s+V2_V**2*t2_s+V3_V**2*t3_s+V4_V**2*t4_s+V5_V**2*t5_s','V^2s','Some V^2 dt de cada degrau'),
    ('Vrms','sqrt(Integral/T)','V','Vrms=sqrt(integral/T)'),
    params=[('V1_V',10),('V2_V',20),('V3_V',30),('V4_V',20),('V5_V',10),('t1_s',1),('t2_s',1),('t3_s',2),('t4_s',1),('t5_s',1)])
put(11,36,('a','abs(Ia_dc_A)','A','DC: RMS=|DC|'),('b','sqrt(Vb_dc_V**2+Vb_ac_V**2/2)','V','RMS^2=DC^2+ACpico^2/2'),('c','sqrt(Ic_dc_A**2+Ic_ac_A**2/2)','A'),('d','sqrt((Vd_sin_V**2+Vd_cos_V**2)/2)','V'))
put(11,37,('Irms','sqrt((I1_A**2+I2_A**2+2*I1_A*I2_A*(f1_Hz==f2_Hz))/2)','A','Mesma f: some; distintas: RMS^2'),('f1','f1_Hz','Hz'),('f2','f2_Hz','Hz'))
put(11,39,('S','V_V**2/complex(Z_R,-Z_X)','VA','S=V^2/conj(Z)'),*power_summary(),*pf_correction())
put(11,40,('S','polar(V_V*I_A,phi_deg)','VA','S=VI /_ phi'),*power_summary())
put(11,42,('S','polar(S_VA,acos(FP))','VA','S=|S| /_ acos(FP)'),('I','conj(S/V_V)','A','I=conj(S/V)',2),('Z','V_V/I','ohm','Z=V/I'),('R','real(Z)','ohm'),('L','imag(Z)/(2*pi*f_Hz)','H','L=X/(2pi f)'))
put(11,43,('V','polar(V_V,V_deg)','V','V em forma complexa',0),('I','polar(I_A,I_deg)','A','I em forma complexa',0),('S','V*conj(I)','VA','S=V conj(I)'),*power_summary())
put(11,45,('Vrms','sqrt(Vdc_V**2+Vac_pk_V**2/2)','V','Vrms^2=Vdc^2+Vac^2/2'),('Irms','sqrt(Idc_A**2+Iac_pk_A**2/2)','A'),('P','Vdc_V*Idc_A','W','Termo CA em quadratura: Pca=0'),('w','w_rad_s','rad/s'))
rows=[]
for k in 'abcd':
    rows.append(('S'+k,'polar(V%s_V*I%s_A,V%s_deg-I%s_deg)'%(k,k,k,k),'VA','S=V conj(I)'))
    rows.extend(power_summary('S'+k,k+'_'))
put(11,46,*rows)
put(11,47,('Sa','polar(Va_pk_V*Ia_pk_A/2,Va_deg-Ia_deg)','VA','Pico: S=Vp Ip*/2'),('Sb','polar(Vb_pk_V*Ib_pk_A/2,Vb_deg-Ib_deg)','VA'),('Sc','Vc_V**2/polar(Zc_mag,-Zc_deg)','VA','S=|V|^2/conj(Z)'),('Sd','Id_A**2*polar(Zd_mag,Zd_deg)','VA','S=|I|^2 Z'))
put(11,48,('Sa','complex(Pa_W,Qa_VAR)','VA'),('Sb','complex(abs(Qb_VAR)/tan(acos(FPb)),Qb_VAR)','VA','P=|Q|/tan(acos(FP))'),('Sc','complex(sqrt(Sc_VA**2-Qc_VAR**2),Qc_VAR)','VA','P=sqrt(|S|^2-Q^2)'),('Sd','complex(Pd_W,Pd_W*tan(Zd_deg))','VA','Q=P tan(phi)'),('Zd','Vd_V**2/conj(Sd)','ohm','Z=V^2/conj(S)'))
put(11,49,('Sa','complex(Pa_W,Pa_W*tan(acos(FPa)))','VA'),('Sb','complex(Pb_W,-sqrt(Sb_VA**2-Pb_W**2))','VA'),('Sc','polar(Vc_V*Ic_A,Vc_deg-Ic_deg)','VA'),('Sd','Vd_V**2/complex(Zd_R,-Zd_X)','VA','S=|V|^2/conj(Z)'),('Vd','polar(Vd_V,Vd_deg)','V','',0))
put(11,50,('Sa','complex(Pa_W,-Pa_W*tan(acos(FPa)))','VA','Carga a adiantada'),('Za','Va_V**2/conj(Sa)','ohm','Z=|V|^2/conj(S)'),('Zb','complex(Pb_W,Qb_VAR)/Ib_A**2','ohm','Z=S/|I|^2'),('Zc','Vc_V**2/conj(polar(Sc_VA,Sc_deg))','ohm'),('Vref','polar(Vc_V,Vc_deg)','V','',0))
for n in (70,81):put(11,n,('P','P_W','W'),('Q','Q_VAR','VAR'),('S','complex(P,Q)','VA'),('FP','P/abs(S)','','FP=P/|S|'),*pf_correction())
put(11,71,('S1','complex(Q1_VAR/tan(acos(FP1)),Q1_VAR)','VA'),('S2','complex(P2_W,Q2_VAR)','VA'),('S3','complex(P3_W,P3_W*tan(acos(FP3)))','VA'),('S','S1+S2+S3','VA','St=S1+S2+S3'),('I','conj(S/V_V)','A','I=conj(St/V)',2),('Z','V_V/I','ohm'),*power_summary())
put(11,72,('Q','Ptot_W*tan(acos(FPtot))','VAR'),('P2','Ptot_W-P1_W','W'),('Q2','Q-P1_W*tan(acos(FP1))','VAR'),('FP2','P2/abs(complex(P2,Q2))','','FP2=P2/|S2|'),*pf_correction('Ptot_W','Q'))
put(11,73,('P','P_W','W'),('Q','Qcap_VAR+Qind_VAR','VAR'),('S','complex(P,Q)','VA'),('I','conj(S/V_V)','A','I=conj(S/V)',2),*pf_correction())
put(11,82,('P','Pheat_W+Smotor_VA*FPmotor','W'),('Q','Smotor_VA*sqrt(1-FPmotor**2)','VAR'),('S','complex(P,Q)','VA'),*pf_correction())
put(11,83,('S','polar(V_V*I_A/2,V_deg-I_deg)','VA','Fasores de pico: S=VI*/2'),*power_summary())
put(11,84,('Custo','Energia_kWh*tar_kWh+Demanda_VA/1000*dem_USDkVA','USD','Custo=energia+demanda'),('Tarifa','Custo/Energia_kWh','USD/kWh','Tarifa=custo/energia'))
put(11,86,('Zant','complex(R_ohm,2*pi*f_Hz*L_H)','ohm','Zant=R+j2pi f L'),('Zinterna','conj(Zant)','ohm','Zinterna=conj(Zant)'))
put(11,87,('R','VR_V/I_A','ohm','R=VR/I'),('FP','R/Zmag_ohm','','FP=R/|Z|'))
put(11,88,('S','polar(V_V*I_A,phi_deg)','VA','S=VI /_ phi'),*power_summary())
put(11,89,('S','polar(S_VA,acos(FP))','VA','S=|S| /_ acos(FP)'),('Z','V_V**2/conj(S)','ohm','Z=V^2/conj(S)'),('f','f_Hz','Hz'))
put(11,90,('Smax','Pnom_W/FPnom','VA','|Smax|=Pnom/FPnom'),('P','Pnom_W+Pextra_W','W'),
    ('Q','Pnom_W*tan(acos(FPnom))+Pextra_W*tan(acos(FPextra))','VAR','Some as potencias reativas'),
    ('Qmax','sqrt(Smax**2-P**2)','VAR','Qmax=sqrt(Smax^2-P^2)'),('Qc','Q-Qmax','VAR','Qc=Qload-Qmax'),
    params=[('Pnom_W',2000000),('FPnom',.85),('Pextra_W',300000),('FPextra',.8)])
put(11,91,('S','V_V*I_A','VA'),('FP','P_W/S','','FP=P/(VI)'),('P','P_W','W'),('Q','sqrt(S**2-P**2)','VAR'),*pf_correction())
put(11,93,('Pm','HPmotor*WporHP','W','Pm=HP WporHP'),('Qm','Pm*tan(acos(FPmotor))','VAR'),
    ('Psinc','abs(Qsinc_VAR)/tan(acos(FPsinc))','W','Psinc=|Qsinc|/tan(acos(FP))'),
    ('S','complex(Pm+Pheat_W+Nlamp*Plamp_W+Psinc,Qm+Qsinc_VAR)','VA','St=some P+jQ de cada carga'),*power_summary(),
    params=[('HPmotor',5),('WporHP',745.7),('FPmotor',.8),('Pheat_W',1200),('Nlamp',10),('Plamp_W',120),('Qsinc_VAR',-1600),('FPsinc',.6)])
put(11,94,('P','S_VA*FPold','W','P=|S| FPold'),('Q','S_VA*sqrt(1-FPold**2)','VAR'),('Qalvo','P*tan(acos(FPnovo))','VAR'),('Qc','Q-Qalvo','VAR','Qc=Qold-Qalvo'),('Snovo','P/FPnovo','VA','Snovo=P/FPnovo'),('Folga','S_VA-Snovo','VA'),
    ('CustoCap','Qc/1000*Cap_USDkVAR','USD','CustoCap=Qc[kVAR] tarifa'),('Economia','Folga/1000*Sub_USDkVA','USD','Economia=folga[kVA] tarifa'),('Saldo','Economia-CustoCap','USD','Saldo>0: compensa instalar'),
    params=[('S_VA',1000000),('FPold',.7),('FPnovo',.95),('Cap_USDkVAR',30),('Sub_USDkVA',120)])
put(11,96,('ZL','complex(Zth_R,-Zth_X)','ohm','ZL=conj(Zth)'),('Pmax','Vth_V**2/(4*Zth_R)','W','Pmax=|Vth|^2/(4Rth)'))

put(11,52,('SA','complex(PA_W,PA_W*tan(acos(FPA)))','VA','SA=PA+jPA tan(acos(FPA))'),
    ('SB','polar(SB_VA,-acos(FPB))','VA','B adiantada: Q negativo'),('SC','complex(PC_W,QC_VAR)','VA'),
    ('S','SA+SB+SC','VA','St=SA+SB+SC'),('I','conj(S/c0)','A','I=conj(St/Vs)',2),*power_summary(),
    params=[('PA_W',2000),('FPA',.8),('SB_VA',3000),('FPB',.4),('PC_W',1000),('QC_VAR',500)])
put(11,60,('S','complex(P1_W+P2_W,P1_W*tan(acos(FP1))+P2_W*tan(acos(FP2)))','VA','St=some P+jQ de cada carga'),
    ('Vo','S/conj(c0)','V','Vo=St/conj(Is)',2),*power_summary(),
    params=[('P1_W',20000),('FP1',.8),('P2_W',16000),('FP2',.9)])
put(11,61,('SA','polar(SA_VA,-acos(FPA))','VA'),('SB','complex(PB_W,QB_VAR)','VA'),
    ('SC','complex(PC_W,PC_W*tan(acos(FPC)))','VA'),('S','SA+SB+SC','VA','St=SA+SB+SC'),
    ('Io','conj(S/c0)','A','Io=conj(St/Vs)',2),*power_summary(),
    params=[('SA_VA',2000),('FPA',.707),('PB_W',1200),('QB_VAR',-800),('PC_W',4000),('FPC',.9)])
put(11,62,('Vfim','polar(Vfim_V,Vfim_deg)','V','Tensao RMS na carga distante',2),
    ('S2','complex(P2_W,-P2_W*tan(acos(FP2)))','VA'),('I2','conj(S2/Vfim)','A','I2=conj(S2/Vfim)',2),
    ('Vmeio','Vfim+I2*(z2+z3)','V','Vmeio=Vfim+I2 Zlinha2',2),('S1','complex(P1_W,-P1_W*tan(acos(FP1)))','VA'),
    ('I1','conj(S1/Vmeio)','A','I1=conj(S1/Vmeio)',2),('Vs','Vmeio+(I1+I2)*(z0+z1)','V','Vs=Vmeio+(I1+I2)Zlinha1',2),
    params=[('Vfim_V',120),('Vfim_deg',0),('P1_W',10),('FP1',.9),('P2_W',15),('FP2',.8)])
put(11,63,('S1','complex(P1_W,-P1_W*tan(acos(FP1)))','VA'),('S2','complex(P2_W,P2_W*tan(acos(FP2)))','VA'),
    ('S3','complex(Q3_VAR/tan(acos(FP3)),Q3_VAR)','VA'),('S','S1+S2+S3','VA','St=S1+S2+S3'),
    ('Io','conj(S/c0)','A','Io=conj(St/Vs)',2),*power_summary(),
    params=[('P1_W',12000),('FP1',.866),('P2_W',16000),('FP2',.85),('Q3_VAR',20000),('FP3',.6)])
put(11,64,('IZ','c0/z1','A','IZ=Vs/Zcarga',2),('IV','conj(complex(Pv_W,Qv_VAR)/c0)','A','IV=conj(Sv/Vs)',2),
    ('Is','IZ-IV','A','KCL: Is=IZ-IV',2),params=[('Pv_W',2500),('Qv_VAR',-400)])
put(11,74,('P','P1_W+P2_W','W'),('Q','P1_W*tan(acos(FP1))+P2_W*tan(acos(FP2))','VAR'),
    ('S','complex(P,Q)','VA'),*power_summary()[2:],('C','Q/(omega*abs(c0)**2)','F','FP unitario: C=Q/(w |Vs|^2)'),
    params=[('P1_W',24000),('FP1',.8),('P2_W',40000),('FP2',.95)])
put(11,92,('P','Pmotor_W+Pluz_W','W'),('Q','Pmotor_W*tan(acos(FPmotor))+Qcap_VAR','VAR'),
    ('S','complex(P,Q)','VA'),('I','conj(S/c0)','A','I=conj(St/Vs)',2),*power_summary()[2:],
    params=[('Pmotor_W',60000),('FPmotor',.75),('Qcap_VAR',-20000),('Pluz_W',20000)])

def phase_currents(v,z,delta=False,lines='complex(0,0)'):
    rows=[('ZY',z+'/3' if delta else z,'ohm','Delta -> Y: ZY=Zd/3' if delta else 'Impedancia por fase'),
          ('Ztotal',lines+'+ZY','ohm','Ztotal=Zlinha+ZY'),
          ('Ia',v+'/Ztotal','A','Ia=Van/Ztotal',2),
          ('Ib','Ia*polar(1,-120)','A','Ib=Ia /_ -120deg',2),
          ('Ic','Ia*polar(1,120)','A','Ic=Ia /_ +120deg',2),
          ('VA','Ia*ZY','V','VA=Ia ZY',2),
          ('S','3*abs(Ia)**2*ZY','VA','Scarga=3|Ia|^2 ZY')]
    if delta:rows += [('IAB','Ia*polar(1/sqrt(3),30)','A','IAB=Ia/sqrt(3) /_ +30deg',2)]
    return rows

def totals_and_line(s,v,lines=None):
    rows=[('S',s,'VA','St=some as potencias complexas'),
          ('Ia','conj(S/(sqrt(3)*'+v+'))','A','Ia=conj(St/(sqrt(3)VL))',2),
          ('P','real(S)','W'),('Q','imag(S)','VAR'),
          ('FP','abs(real(S))/abs(S)','','FP=|P|/|S|')]
    if lines:
        rows += [('Slinha','3*abs(Ia)**2*'+lines,'VA','Slinha=3|Ia|^2 Zlinha'),
                 ('Sfonte','S+Slinha','VA','Sfonte=Scarga+Slinha'),
                 ('Vs','%s/sqrt(3)+Ia*%s'%(v,lines),'V','Vs,fase=Vr,fase+Ia Zlinha',2),
                 ('VLfonte','sqrt(3)*abs(Vs)','V','VLfonte=sqrt(3)|Vs,fase|')]
    return rows

put(12,1,('Van_abc','polar(Vab_V/sqrt(3),-30)','V','abc: Van=Vab/sqrt(3) /_ -30',2),
    ('Vbn_abc','Van_abc*polar(1,-120)','V','Vbn=Van /_ -120',2),('Vcn_abc','Van_abc*polar(1,120)','V','Vcn=Van /_ +120',2),
    ('Van_acb','polar(Vab_V/sqrt(3),30)','V','acb: Van=Vab/sqrt(3) /_ +30',2),
    ('Vbn_acb','Van_acb*polar(1,120)','V','Vbn=Van /_ +120',2),('Vcn_acb','Van_acb*polar(1,-120)','V','Vcn=Van /_ -120',2))
put(12,2,('Van','polar(Van_V,Van_deg)','V','',0),('Vcn','polar(Vcn_V,Vcn_deg)','V','',0),
    ('Vbn','-Van-Vcn','V','KVL equilibrada: Vbn=-Van-Vcn',2),('Delta','arg(Vcn/Van)','deg','+120=abc; -120=acb'))
put(12,3,('Vbn','polar(Vbn_V,Vbn_deg)','V','',0),('Vcn','polar(Vcn_V,Vcn_deg)','V','',0),('Van','-Vbn-Vcn','V','Van=-Vbn-Vcn',2),('Delta','arg(Vcn/Vbn)','deg','-120=abc; +120=acb'))
put(12,4,*phase_currents('VL_V/sqrt(3)','polar(Zmag_ohm,Z_deg)'))
put(12,5,('Va','polar(VmA_V,PhA_deg)','V','',0),('Vb','polar(VmB_V,PhB_deg)','V','',0),('Vc','polar(VmC_V,PhC_deg)','V','',0),
    ('Vab','Va-Vb','V','Vab=Van-Vbn',2),('Vbc','Vb-Vc','V','Vbc=Vbn-Vcn',2),('Vca','Vc-Va','V','Vca=Vcn-Van',2))
put(12,8,*phase_currents('polar(Van_V,Van_deg)','complex(ZY_R,ZY_X)',lines='complex(Zlin_R,Zlin_X)'))
put(12,9,*phase_currents('Vph_V','complex(ZY_R,ZY_X)',lines='complex(Zlin_R,Zlin_X)'),('In','-(Ia+Ib+Ic)','A','In=-soma das correntes',2))
put(12,16,('Ica','-polar(Iac_A,Iac_deg)','A','Ica=-Iac',2),('Iab','Ica*polar(1,-120)','A','abc: Iab=Ica /_ -120',2),('Ibc','Iab*polar(1,-120)','A','Ibc=Iab /_ -120',2),
    ('Ia','Iab-Ica','A','Ia=Iab-Ica',2),('Ib','Ibc-Iab','A','Ib=Ibc-Iab',2),('Ic','Ica-Ibc','A','Ic=Ica-Ibc',2),('Zfase','polar(Vab_V,Vab_deg)/Iab','ohm','Zfase=Vab/Iab'))
put(12,17,('Iab','polar(Ia_A/sqrt(3),Ia_deg+30)','A','Iab=Ia/sqrt(3) /_ +30',2),('Ibc','Iab*polar(1,-120)','A','Ibc=Iab /_ -120',2),('Ica','Iab*polar(1,120)','A','Ica=Iab /_ +120',2))
put(12,23,('Iph','VL_V/polar(Zmag_ohm,Z_deg)','A','Delta: Iph=VL/Zd',2),('IL','sqrt(3)*abs(Iph)','A','IL=sqrt(3)|Iph|'),
    ('W1','VL_V*IL*cos(30+Z_deg)','W','W1=VL IL cos(30+phi)'),('W2','VL_V*IL*cos(30-Z_deg)','W','W2=VL IL cos(30-phi)'),('P','W1+W2','W','P=W1+W2'))
put(12,24,*phase_currents('polar(Vab_V/sqrt(3),Vab_deg-30)','polar(Zd_mag,Zd_deg)',True,'complex(Zlin_R,Zlin_X)'))
put(12,27,*phase_currents('polar(Vab_V/sqrt(3),Vab_deg-30)','complex(ZY_R,ZY_X)',lines='complex(Zlin_R,Zlin_X)'))
put(12,28,*phase_currents('VL_V/sqrt(3)','polar(Zmag_ohm,Z_deg)'))
put(12,29,*phase_currents('polar(Van_V,Van_deg)','complex(Zd_R,Zd_X)',True,'complex(Zlin_R,Zlin_X)'))
put(12,31,('P','3*Pph_W','W','Ptotal=3 Pfase'),('Q','P*tan(acos(FP))','VAR'),('S','complex(P,Q)','VA'),
    ('I','conj(S/(sqrt(3)*VL_V))','A','IL=conj(S/(sqrt(3)VL))',2),('C','Q/(2*pi*f_Hz*VL_V**2)','F','Banco Y: C=Q/(w VL^2)'))
put(12,32,('S','complex(P_W,Q_VAR)','VA','Exemplo de potencia equilibrada'),('Z_Y','VL_V**2/conj(S)','ohm','ZY=VL^2/conj(S)'),('Z_D','3*Z_Y','ohm','Zd=3 ZY'),('FP','P_W/abs(S)','','FP=P/|S|'))
put(12,33,('IL','S_VA/(3*Vph_V)','A','IL=|S|/(3Vfase)'),('phi','acos(FP)','deg'),('P','S_VA*FP','W'),('Q','S_VA*sqrt(1-FP**2)','VAR'))
put(12,34,('Z','complex(Z_R,Z_X)','ohm','',0),('S','VL_V**2/conj(Z)','VA','Carga Y: S=VL^2/conj(Z)'),*power_summary())
put(12,35,('ZdY','complex(Zd_R,Zd_X)/3','ohm','ZdY=Zd/3'),('ZY','complex(ZY_R,ZY_X)','ohm','',0),
    ('Yeq','1/ZdY+1/ZY','S','Yeq=1/ZdY+1/ZY'),('I','VL_V/sqrt(3)*Yeq','A','I=Vfase Yeq',2),('S','VL_V**2*conj(Yeq)','VA','S=VL^2 conj(Yeq)'),*power_summary())
put(12,36,*totals_and_line('polar(S_VA,acos(FP))','VLload_V','complex(Zlin_R,Zlin_X)'))
put(12,37,*totals_and_line('complex(P_W,P_W*tan(acos(FP)))','VL_V'))
put(12,41,*totals_and_line('complex(P_W,P_W*tan(acos(FP)))','VL_V'))
put(12,42,('Vph','sqrt(P_W*(ZY_R**2+ZY_X**2)/(3*ZY_R))','V','P=3 Vfase^2 R/|Z|^2'),('VL','sqrt(3)*Vph','V','VL=sqrt(3)Vfase'),('I','Vph/complex(ZY_R,ZY_X)','A','I=Vfase/ZY',2))
put(12,44,*totals_and_line('complex(S_P_W,S_Q_VAR)','VLload_V','complex(Zlin_R,Zlin_X)'),('FPfonte','real(Sfonte)/abs(Sfonte)','','FPfonte=Pfonte/|Sfonte|'))
put(12,45,*totals_and_line('complex(P_W,P_W*tan(acos(FP)))','VLload_V','complex(Zlin_R,Zlin_X)'))
put(12,46,('P_Y','VL_V**2/R_ohm','W','Y: P=VL^2/R'),('P_D','3*P_Y','W','Delta: P=3VL^2/R'))
put(12,47,*totals_and_line('polar(S1_VA,acos(FP1))+polar(S2_VA,-acos(FP2))+P3_W','VL_V'))
put(12,49,('SY','VL_V**2/complex(Z_R,-Z_X)','VA','Y: S=VL^2/conj(Z)'),('SD','3*SY','VA','Delta: S=3 SY'),('PY','real(SY)','W'),('PD','real(SD)','W'))
put(12,50,('S','polar(S_VA,acos(FP))','VA'),('S2','S-P1_W','VA','S2=St-S1'),('Z2','VL_V**2/conj(S2)','ohm','ZY2=VL^2/conj(S2)'))
put(12,52,('Va','Vph_V','V','',0),('Vb','polar(Vph_V,-120)','V','',0),('Vc','polar(Vph_V,120)','V','',0),
    ('Ia','Va/polar(ZA_mag,ZA_deg)','A','Ia=Van/ZA',2),('Ib','Vb/polar(ZB_mag,ZB_deg)','A','Ib=Vbn/ZB',2),('Ic','Vc/polar(ZC_mag,ZC_deg)','A','Ic=Vcn/ZC',2),('In','-(Ia+Ib+Ic)','A','In=-(Ia+Ib+Ic)',2))
put(12,54,('Va','Vph_V','V','',0),('Vb','polar(Vph_V,-120)','V','',0),('Vc','polar(Vph_V,120)','V','',0),
    ('Ia','Va/complex(ZA_R,ZA_X)','A','Ia=Van/ZA',2),('Ib','Vb/complex(ZB_R,ZB_X)','A','Ib=Vbn/ZB',2),('Ic','Vc/complex(ZC_R,ZC_X)','A','Ic=Vcn/ZC',2),
    ('In','-(Ia+Ib+Ic)','A','In=-soma(Ik)',2),('S','Va*conj(Ia)+Vb*conj(Ib)+Vc*conj(Ic)','VA','S=soma(Vk conj(Ik))'))
put(12,67,('Sm','polar(Smotor_VA,acos(FPmotor))','VA','Smotor=|Sm| /_ acos(FP)'),
    ('SA','Sm/3+PA_W','VA','SA=Sm/3+lampada A'),('SB','Sm/3+PB_W','VA'),('SC','Sm/3+PC_W','VA'),
    ('Ia','conj(SA/Vph_V)','A','Ia=conj(SA/Van)',2),('Ib','conj(SB/polar(Vph_V,-120))','A','Ib=conj(SB/Vbn)',2),('Ic','conj(SC/polar(Vph_V,120))','A','Ic=conj(SC/Vcn)',2),
    ('In','-(Ia+Ib+Ic)','A','In=-soma(Ik)',2),('W1','real(SA)','W'),('W2','real(SB)','W'),('W3','real(SC)','W'))
put(12,68,('S','sqrt(3)*VL_V*IL_A','VA','|S|=sqrt(3)VL IL'),('FP','P_W/S','','FP=P/|S|'),('Q','sqrt(S**2-P_W**2)','VAR'),('Vph','VL_V/sqrt(3)','V'))
put(12,69,*totals_and_line('polar(S1_VA,acos(FP1))+polar(S2_VA,acos(FP2))+P3_W','VL_V','complex(Zlin_R,Zlin_X)'))
put(12,70,('P','P1_W+P2_W','W','P=W1+W2'),('Q','sqrt(3)*(P1_W-P2_W)','VAR','Q=sqrt(3)(W1-W2)'),('phi','arg(complex(P,Q))','deg','phi=atan(Q/P)'),('Z','polar(VL_V/(sqrt(3)*IL_A),phi)','ohm','Z=Vfase/IL /_ phi'))
put(12,75,('I1','V1_V/R_ohm','A','I1=V1/R'),('I2','V2_V/R_ohm','A','I2=V2/R'))
put(12,76,('razao','(V2_V/V1_V)**2','','Perda1/Perda2=(V2/V1)^2'))
put(12,77,('Psaida','Sgen_VA*FPgen','W','Psaida=|Sgen| FPgen'),('Plinha','3*Plossph_W','W','Plinha=3 perda/fase'),('Pgerador','Psaida-Pload_W-Plinha','W','Perda gerador=saida-carga-linha'))
put(12,78,('P','P_W','W'),('Q','sqrt(S_VA**2-P**2)','VAR'),('Qalvo','P*tan(acos(FPnovo))','VAR'),('Qc','Q-Qalvo','VAR','Qc=Q-Qalvo'),('CY','Qc/(2*pi*f_Hz*VL_V**2)','F','Y: C=Qc/(w VL^2)'),('CD','CY/3','F','Delta: C=CY/3'))
put(12,79,*phase_currents('polar(Van_V,Van_deg)','complex(ZY_R,ZY_X)',lines='Zlin_R'),('Pperda','3*abs(Ia)**2*Zlin_R','W','Pperda=3|I|^2 Rlinha'))
put(12,80,('St','polar(sqrt(3)*VL_V*IL_A,acos(FPtot))','VA','St=sqrt(3)VL IL /_ acos(FP)'),('S1','polar(S1_VA,acos(FP1))','VA'),('S3','complex(P3_W,-P3_W*tan(acos(FP3)))','VA'),('S2','St-S1-S3','VA','S2=St-S1-S3'),('FP2','abs(real(S2))/abs(S2)','','FP2=|P2|/|S2|'))
put(12,81,*totals_and_line('polar(S1_VA,-acos(FP1))+P2_W+polar(S3_VA,acos(FP3))+complex(P4_W,Q4_VAR)','VLload_V','complex(Zlin_R,Zlin_X)'))
put(12,82,('S1','polar(S1_VA,acos(FP1))','VA'),('S2','3*VLload_V**2/complex(Zd_R,-Zd_X)','VA','Sdelta=3VL^2/conj(Zd)'),*totals_and_line('S1+S2','VLload_V','complex(Zlin_R,Zlin_X)'))
put(12,83,('Pmotor','HP*HP_W/efic','W','Pmotor=HP Watts/HP / eficiencia'),*totals_and_line('complex(Pmotor,Pmotor*tan(acos(FP)))+Pheat_W','VL_V'))
put(12,85,('Rfase','VL_V**2/P_W','ohm','Y: Rfase=VL^2/Ptotal'))

PARAM_FIX['p12_61']=[]
put(12,67,('Sm','polar(Smotor_VA,acos(FPmotor))','VA','Smotor=|Sm| /_ acos(FP)'),
    ('SA','Sm/3+PA_W','VA','SA=Sm/3+lampada A'),('SB','Sm/3+PB_W','VA'),('SC','Sm/3+PC_W','VA'),
    ('Ia','conj(SA/c0)','A','Ia=conj(SA/Van)',2),('Ib','conj(SB/c1)','A','Ib=conj(SB/Vbn)',2),('Ic','conj(SC/c2)','A','Ic=conj(SC/Vcn)',2),
    ('In','-(Ia+Ib+Ic)','A','In=-soma(Ik)',2),('W1','real(SA)','W'),('W2','real(SB)','W'),('W3','real(SC)','W'),
    params=[('Smotor_VA',260000),('FPmotor',.85),('PA_W',24000),('PB_W',15000),('PC_W',9000)])
put(12,84,('Sm','polar(Smotor_VA,acos(FPmotor))','VA','Smotor=|Sm| /_ acos(FP)'),
    ('Va','c0','V','',0),('Vb','c1','V','',0),('Vc','c2','V','',0),
    ('Xc','VLref_V**2/Qcap_VAR','ohm','Xc=Vlinha nominal^2/|Qc|'),('IcAB','(Va-Vb)/complex(0,-Xc)','A','IcAB=(Va-Vb)/(-jXc)',2),
    ('Ia','conj((Sm/3)/Va)+IcAB','A','Ia=Imotor,a+IcAB',2),('Ib','conj((Sm/3)/Vb)-IcAB','A','Ib=Imotor,b-IcAB',2),
    ('Ic','conj((Sm/3+Plamp_W)/Vc)','A','Ic=Imotor,c+Ilampada',2),('In','-(Ia+Ib+Ic)','A','In=-soma(Ik)',2),
    ('S','Va*conj(Ia)+Vb*conj(Ib)+Vc*conj(Ic)','VA','St=soma(Vfase conj(Ifase))'),*power_summary(),
    params=[('Smotor_VA',4000),('FPmotor',.72),('VLref_V',440),('Qcap_VAR',1800),('Plamp_W',800)])

# Small complex systems are expanded once by the authoring compiler. The
# calculator evaluates coefficients and Cramer's determinants after every edit.
def system3(matrix,rhs,prefix=''):
    def det(m):
        a,b,c,d,e,f,g,h,i=m
        return '%s*(%s*%s-%s*%s)-%s*(%s*%s-%s*%s)+%s*(%s*%s-%s*%s)'%(a,e,i,f,h,b,d,i,f,g,c,d,h,e,g)
    rows=[(prefix+'a%d'%k,expr,'','',0) for k,expr in enumerate(matrix)]
    rows += [(prefix+'b%d'%k,expr,'','',0) for k,expr in enumerate(rhs)]
    m=[prefix+'a%d'%k for k in range(9)];b=[prefix+'b%d'%k for k in range(3)]
    rows.append((prefix+'det',det(m),'','det(A)',0))
    for k in range(3):
        mk=list(m)
        for row in range(3):mk[row*3+k]=b[row]
        rows.append((prefix+'x%d'%k,'('+det(mk)+')/'+prefix+'det','','Cramer: xk=det(Ak)/det(A)',0))
    return rows

put(9,61,('Y','1/complex(Z1_R,Z1_X)+1/complex(Z2_R,Z2_X)+1/complex(Z3_R,Z3_X)+1/complex(0,Z4_X)','S','As quatro impedancias em paralelo'),('Zeq','1/Y','ohm','Zeq=1/soma(1/Zk)'))
put(9,63,('Y1','1/complex(R3,X2)','S','',0),('Y2','1/R2','S','',0),
    ('Y4','1/R4','S','',0),('Y5','1/complex(0,XL)','S','',0),('Y6','1/complex(R5,X3)','S','',0),
    *system3(['Y1+Y2','-Y2','-Y1','-Y2','Y2+Y4+Y5','-Y4','-Y1','-Y4','Y1+Y4+Y6'],['1','0','0']),
    ('Zponte','x0','ohm','Injete 1 A; resolva YV=I'),('ZT','complex(R1,X1)+Zponte','ohm','ZT=R1+jX1+Zponte'))
put(9,67,('Za','Ra1+1/(1/complex(0,w_rad_s*La_H)+1/(Ra2+1/complex(0,w_rad_s*Ca_F)))','ohm','(a) Za=R1+[L||(R2+C)]'),
    ('Ya','1/Za','S','Ya=1/Za'),('Zb','1/complex(0,w_rad_s*Cb_F)+1/(1/Rb3+1/Rb2+1/complex(Rb1,w_rad_s*Lb_H))','ohm','(b) Zb=C+[R3||R2||(R1+L)]'),('Yb','1/Zb','S','Yb=1/Zb'))
put(9,69,('Yfim','complex(0,B4_S)+1/(1/complex(0,B2_S)+1/G3_S)','S','Reduza a escada da direita'),
    ('Ymeio','complex(0,B3_S)+1/(1/G2_S+1/complex(0,B1_S)+1/Yfim)','S','Some o shunt e o ramo em serie'),
    ('Yeq','1/(1/G1_S+1/Ymeio)','S','Yeq=1/(1/G1+1/Ymeio)'))
put(9,72,('YC','1/complex(0,XC2)+1/complex(0,XC1+XC3)','S','Capacitores: serie || direto'),
    ('Ya','1/complex(0,XL1)','S','',0),('Yb','1/complex(0,XL3)','S','',0),('Yc','1/complex(0,XL2)','S','',0),
    *system3(['Ya+Yc+YC','-Yc','-YC','-Yc','Yb+Yc+1/R1+1/R2','-1/R1','-YC','-1/R1','YC+1/R1+1/R3'],['Ya','Yb','0']),
    ('Iteste','Ya*(1-x0)+Yb*(1-x1)','A','Vteste=1 V; Iteste=soma correntes'),('Zab','1/Iteste','ohm','Zab=Vteste/Iteste'))
put(9,75,('I','Vin_V/R_ohm','A','Conversor V/I ideal: I=Vin/R'),('Vout','complex(0,XL_ohm)*I','V','Indutor: Vout=jXL I',2),('H','Vout/Vin_V','','H=jXL/R; fase +90deg',2))
put(10,24,('Z1','complex(Z1_R,Z1_X)','ohm','',0),('Z2','complex(Z2_R,Z2_X)','ohm','',0),('Zm','complex(Zm_R,Zm_X)','ohm','',0),
    ('Det','(Z1+Zm)*(Z2+Zm)-Zm**2','','Det=(Z1+Zm)(Z2+Zm)-Zm^2'),
    ('I1','polar(Vs_V,Vs_deg)*(Z2+Zm)/Det','A','I1=Vs(Z2+Zm)/Det',2),('I2','polar(Vs_V,Vs_deg)*Zm/Det','A','I2=Vs Zm/Det',2),('Ic','I1-I2','A','Ramo comum: Ic=I1-I2',2))
put(12,48,('Va','polar(Van_V,Van_deg)','V','',0),('Vb','Va*polar(1,-120)','V','',0),('Vc','Va*polar(1,120)','V','',0),
    ('YL','1/complex(Zlin_R,Zlin_X)','S','',0),('Yab','1/complex(Zab_R,Zab_X)','S','',0),('Ybc','1/complex(Zbc_R,Zbc_X)','S','',0),('Yca','1/complex(Zca_R,Zca_X)','S','',0),
    *system3(['YL+Yab+Yca','-Yab','-Yca','-Yab','YL+Yab+Ybc','-Ybc','-Yca','-Ybc','YL+Ybc+Yca'],['Va*YL','Vb*YL','Vc*YL']),
    ('VAB','x0-x1','V','Resolva nos da carga por KCL',2),('VBC','x1-x2','V','',2),('VCA','x2-x0','V','',2),
    ('Ia','(Va-x0)*YL','A','Ia=(Van-VA)/Zlinha',2),('Ib','(Vb-x1)*YL','A','',2),('Ic','(Vc-x2)*YL','A','',2),
    ('S','VAB*conj(VAB*Yab)+VBC*conj(VBC*Ybc)+VCA*conj(VCA*Yca)','VA','Scarga=soma(Vramo conj(Iramo))'))
