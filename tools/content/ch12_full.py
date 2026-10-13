"""Capitulo 12 completo (problemas 12.1--12.87).

Os casos prioritarios 12.7, 12.14 e 12.25 permanecem em ``ch12.py`` com
recalculo trifasico ao vivo. Este modulo acrescenta todos os demais itens do
livro. Figuras usam componentes eletricos reais; problemas sem figura usam
parametros escalares nomeados. Assim, todo dado numerico alteravel possui uma
rota de edicao. Receitas live_*.py recalculam as etapas e resultados a partir
dos valores vigentes; as antigas strings solution nao vao para o pacote.
"""

SUBJECTS = ["Trifasico"]


def _yyy(vs, zline, loads, source_note="Fonte Y", load_note="Carga Y"):
    """Tres fases em linhas separadas, com neutros comuns e boa legibilidade."""
    ys = (78, 132, 186)
    ops = [("line", 24, ys[0], 24, ys[-1]),
           ("line", 286, ys[0], 286, ys[-1])]
    for y, source, zl, load in zip(ys, vs, zline, loads):
        ops += [("vsrc_h", 24, y, 78, source),
                ("wire", 78, y, 92, y),
                ("imp_h", 92, y, 148, zl),
                ("wire", 148, y, 178, y),
                ("imp_h", 178, y, 242, load),
                ("wire", 242, y, 286, y)]
    return ops


def _ydelta(vs, zline, loads, source_note="Fonte Y", load_note="Carga delta"):
    """Fonte/linha em tres fileiras e delta retangular sem rotulos cruzados."""
    ys = (78, 132, 186)
    ops = [("line", 24, ys[0], 24, ys[-1])]
    for y, source, zl in zip(ys, vs, zline):
        ops += [("vsrc_h", 24, y, 76, source),
                ("wire", 76, y, 90, y),
                ("imp_h", 90, y, 146, zl),
                ("wire", 146, y, 218, y)]
    ops += [("imp_v", 218, ys[0], ys[1], loads[0]),
            ("imp_v", 218, ys[1], ys[2], loads[1]),
            ("wire", 218, ys[0], 276, ys[0]),
            ("imp_v", 276, ys[0], ys[2], loads[2]),
            ("wire", 218, ys[2], 276, ys[2])]
    return ops


def _mixed(vs, zline, zdelta, zy):
    """Carga delta e carga Y em paralelo, com doze registros editaveis."""
    ys = (78, 132, 186)
    ops = [("line", 8, ys[0], 8, ys[-1]),
           ("line", 292, ys[0], 292, ys[-1])]
    for y, source, zl, load in zip(ys, vs, zline, zy):
        ops += [("vsrc_h", 8, y, 52, source),
                ("wire", 52, y, 60, y),
                ("imp_h", 60, y, 102, zl),
                ("wire", 102, y, 120, y),
                ("imp_h", 218, y, 268, load),
                ("wire", 120, y, 218, y),
                ("wire", 268, y, 292, y)]
    ops += [("imp_v", 120, ys[0], ys[1], zdelta[0]),
            ("imp_v", 120, ys[1], ys[2], zdelta[1]),
            ("wire", 120, ys[0], 174, ys[0]),
            ("imp_v", 174, ys[0], ys[2], zdelta[2]),
            ("wire", 120, ys[2], 174, ys[2])]
    return ops


def _parallel_phase(source, zline, zdelta_y, zy):
    """Equivalente por fase de cargas delta e Y em paralelo."""
    return [
        ("vsrc_v", 38, 78, 194, source),
        ("imp_h", 38, 78, 126, zline),
        ("wire", 126, 78, 306, 78),
        ("wire", 38, 194, 306, 194),
        # Long complex labels are forced to opposite outer sides.  The old
        # x=184/266 placement printed both strings into the same gap.
        ("imp_v", 150, 78, 194, zdelta_y),
        ("imp_v", 290, 78, 194, zy),
        ("gnd", 205, 194),
    ]


def _split(vtop, vbottom, zline, ztop, zbottom, zouter=None):
    """Sistema monofasico trifilar, incluindo o condutor neutro."""
    ys = (76, 134, 192)
    ops = [("lbl", "Sistema trifilar", 8, 48),
           ("vsrc_v", 38, ys[0], ys[1], vtop),
           ("vsrc_v", 38, ys[1], ys[2], vbottom)]
    for y, zl in zip(ys, zline):
        ops += [("wire", 38, y, 76, y), ("imp_h", 76, y, 126, zl),
                ("wire", 126, y, 186, y)]
    ops += [("imp_v", 186, ys[0], ys[1], ztop),
            ("imp_v", 186, ys[1], ys[2], zbottom)]
    if zouter is not None:
        ops += [("wire", 186, ys[0], 270, ys[0]),
                ("imp_v", 270, ys[0], ys[2], zouter),
                ("wire", 186, ys[2], 270, ys[2])]
    return ops


def _watt(vs, loads, names=("W1", "W2", "W3")):
    ys = (78, 132, 186)
    ops = [("line", 24, ys[0], 24, ys[-1]),
           ("line", 286, ys[0], 286, ys[-1])]
    for y, source, load, name in zip(ys, vs, loads, names):
        ops += [("vsrc_h", 24, y, 78, source),
                ("wire", 78, y, 176, y),
                ("imp_h", 196, y, 254, load),
                ("wire", 176, y, 196, y), ("wire", 254, y, 286, y),
                ("lbl", name, 132, y - 16)]
    return ops


def _motor_cap_lamp():
    """Equivalente Y do motor, capacitor a-b e lampada c-n separados."""
    ys = (78, 132, 186)
    ops = [("line", 8, ys[0], 8, ys[-1]),
           ("line", 300, ys[0], 300, 216)]
    for y, source in zip(ys, ("254/_0V", "254/_-120V", "254/_120V")):
        ops += [("vsrc_h", 8, y, 52, source), ("wire", 52, y, 90, y),
                ("wire", 90, y, 220, y),
                ("imp_h", 220, y, 284, "25.1+j24.2"),
                ("wire", 284, y, 300, y)]
    ops += [("wire", 90, ys[0], 120, ys[0]),
            ("imp_v", 120, ys[0], ys[1], "-j107.56"),
            ("wire", 90, ys[1], 120, ys[1]),
            ("wire", 90, ys[2], 120, ys[2]),
            ("res_v", 120, ys[2], 216, "80.67"),
            ("wire", 120, 216, 300, 216)]
    return ops


V120 = ("120/_0V", "120/_-120V", "120/_120V")
V100 = ("100/_0V", "100/_-120V", "100/_120V")
V110 = ("110/_0V", "110/_-120V", "110/_120V")
V240 = ("240/_0V", "240/_-120V", "240/_120V")
ZERO = ("0", "0", "0")


CIRCUITS = {
    "p12_6": _yyy(V120, ("1+j2",) * 3, ("12+j9",) * 3,
                    load_note="Exemplo Y-Y"),
    "p12_10": _yyy(("440/_0V", "440/_-120V", "440/_120V"),
                     ("2",) * 3, ("25-j10", "20", "10+j5"),
                     load_note="Y sem neutro"),
    "p12_11": _ydelta(("240/_0V", "240/_-120V", "240/_120V"), ZERO,
                        ("2-j3",) * 3),
    "p12_12": _ydelta(V120, ZERO, ("18+j12",) * 3,
                        load_note="Exemplo Y-delta"),
    "p12_13": _ydelta(V110, ("2",) * 3, ("9-j6",) * 3),
    "p12_15": _parallel_phase("121.24/_-30V", "1+j1", "8-j10", "12+j5"),
    "p12_18": _ydelta(("220/_60V", "220/_-60V", "220/_180V"), ZERO,
                        ("12+j9",) * 3),
    "p12_19": _ydelta(("173/_0V", "173/_-120V", "173/_120V"), ZERO,
                        ("30+j10",) * 3, source_note="Fonte delta"),
    "p12_20": _ydelta(("120/_-30V", "120/_-150V", "120/_90V"), ZERO,
                        ("12+j9",) * 3, source_note="Exemplo delta"),
    "p12_21": _ydelta(("132.79/_-30V", "132.79/_-150V", "132.79/_90V"),
                        ZERO, ("10+j8",) * 3, source_note="Delta 230V"),
    "p12_22": _parallel_phase("254/_-30V", "2", "4-j1.667", "4+j6"),
    "p12_26": _yyy(("120.09/_-30V", "120.09/_-150V", "120.09/_90V"),
                     ("1+j1",) * 3, ("12+j9",) * 3,
                     source_note="Delta 208V", load_note="Exemplo delta-Y"),
    "p12_30": _yyy(("120.09/_0V", "120.09/_-120V", "120.09/_120V"),
                     ZERO, ("30/_45",) * 3),
    "p12_38": _yyy(V110, ("1+j2",) * 3, ("9+j12",) * 3),
    "p12_39": _ydelta(("57.735/_-30V", "57.735/_-150V", "57.735/_90V"),
                        ("5",) * 3, ("8-j6", "10", "4+j3"),
                        source_note="Delta 100V"),
    "p12_40": _ydelta(V100, ("1+j0.5",) * 3, ("21-j24",) * 3),
    "p12_51": _ydelta(("138.56/_-30V", "138.56/_-150V", "138.56/_90V"),
                        ZERO, ("8+j6", "4.2-j2.2", "10"),
                        source_note="Delta 240V"),
    "p12_53": _yyy(V120, ZERO, ("j20", "30+j20", "-j40"),
                     load_note="Exemplo desequilibrado"),
    "p12_55": _ydelta(("138.56/_-30V", "138.56/_-150V", "138.56/_90V"),
                        ZERO, ("j25", "30/_30", "40")),
    "p12_56": _ydelta(V120, ZERO, ("j10", "20", "-j15"),
                        load_note="Exemplo sem neutro"),
    "p12_57": _yyy(V110, ZERO, ("80+j50", "20+j30", "60-j40"),
                     load_note="Y sem neutro"),
    "p12_59": _yyy(V100, ZERO, ("0.2mF", "40", "10mH"),
                     load_note="Carga RLC em Y"),
    "p12_60": _split("220/_0V", "220/_0V", ("4", "4", "4"),
                       "15-j10", "30+j20", "12+j5"),
    "p12_61": _yyy(V240, ("4+j3",) * 3, ("10+j15",) * 3,
                     load_note="Y + capacitores"),
    "p12_62": _yyy(V120, ("1+j0.754",) * 3,
                     ("20", "-j26.5", "j18.85"),
                     load_note="Exemplo PSpice"),
    "p12_63": _ydelta(("220/_0V", "220/_-120V", "220/_120V"),
                        ("2+j1",) * 3, ("40+j20", "50-j30", "25"),
                        load_note="Carga desequilibrada"),
    "p12_65": _ydelta(("240/_10V", "240/_-110V", "240/_130V"),
                        ("0.6+j0.5",) * 3, ("30-j20",) * 3),
    "p12_66": _watt(("120/_0V", "120/_-120V", "120/_120V"),
                      ("40", "48", "60")),
    "p12_67": _watt(V120, ("86.8", "138.9", "95.4")),
    "p12_71": _watt(("120.09/_-30V", "120.09/_-150V", "120.09/_90V"),
                      ("20", "10-j10", "12+j5"), names=("W1", "W2", "")),
    "p12_73": _watt(("240/_60V", "240/_-120V", "240/_0V"),
                      ("10+j30",) * 3, names=("W1", "W2", "")),
    "p12_74": _watt(("120.09/_-30V", "120.09/_-150V", "120.09/_90V"),
                      ("60-j30",) * 3, names=("W1", "W2", "")),
    "p12_84": _motor_cap_lamp(),
    "p12_86": _split("120/_0V", "120/_0V", ("1", "1", "1"),
                       "24-j2", "15+j4"),
    "p12_87": _split("115/_0V", "115/_0V", ("1", "2", "1"),
                       "20", "30", "15+j18.85"),
}

# Estes problemas pedem uma segunda analise/simulacao de uma rede anterior.
# Repetir a topologia aqui deixa a rede inteira editavel no proprio item, sem
# obrigar o aluno a voltar ao primeiro enunciado.
CIRCUITS["p12_43"] = list(CIRCUITS["p12_15"])
CIRCUITS["p12_58"] = list(CIRCUITS["p12_10"])
CIRCUITS["p12_64"] = list(CIRCUITS["p12_39"])
CIRCUITS["p12_72"] = list(CIRCUITS["p12_11"])

# 12.61 has three delta capacitors, not a spare scalar which the circuit
# solver never sees. Draw each branch and expose its actual impedance.
CIRCUITS['p12_61'] = _mixed(V240,('4+j3',)*3,('-j36',)*3,('10+j15',)*3)
# Route the A-C branch around the outside: no label over the B conductor.
CIRCUITS['p12_61'] = [op for op in CIRCUITS['p12_61'] if op not in
    [('wire',120,78,174,78),('imp_v',174,78,186,'-j36'),('wire',120,186,174,186)]]
CIRCUITS['p12_61'] += [('wire',120,78,120,64),('wire',120,64,306,64),
    ('wire',306,64,306,210),('imp_h',120,210,306,'-j36'),('wire',120,186,120,210)]
# Three-wattmeter method includes the neutral. Two-wattmeter figures do not.
CIRCUITS['p12_66'] += [('wire',24,186,24,210),('wire',24,210,286,210),('wire',286,186,286,210)]
for _id,_vs,_loads in [('p12_71',('120.088856/_-30V','120.088856/_-150V','120.088856/_90V'),('20','10-j10','12+j5')),
                       ('p12_73',('138.564065/_-30V','138.564065/_90V','138.564065/_-150V'),('10+j30',)*3)]:
    _ops=_ydelta(_vs,ZERO,_loads)
    # Wider delta columns accommodate both complex labels.
    _shift={218:196,276:300}
    CIRCUITS[_id]=[(op[0],_shift.get(op[1],op[1]),op[2],_shift.get(op[3],op[3]),op[4])
        if op[0]=='wire' else (op[0],_shift.get(op[1],op[1]),*op[2:]) for op in _ops]
    CIRCUITS[_id] += [('lbl','W1: a-b, Ia; W2: c-b, Ic',12,218)]
CIRCUITS['p12_74']=_watt(('120.088856/_30V','120.088856/_150V','120.088856/_-90V'),
    ('60-j30',)*3,names=('W1','','W2'))
# Power-rated loads are edited in watts/VA/PF, not as fictitious resistances.
# Only the real voltage-source registers remain in these word problems.
for _id in ('p12_67','p12_84'):
    CIRCUITS[_id]=[op for op in CIRCUITS[_id] if op[0] not in ('imp_h','imp_v','res_v')]
    CIRCUITS[_id] += [('lbl','Motor e cargas: Dados atuais',12,218)]


STATEMENTS = {
    1: ["Gerador Y: Vab=400 V.", "Ache as tensoes de fase para", "sequencias abc e acb."],
    2: ["Van=120/_30 V e Vcn=120/_-90 V.", "Ache a sequencia e Vbn."],
    3: ["Vbn=440/_130 V e Vcn=440/_10 V.", "Ache a sequencia e Van."],
    4: ["Sequencia abc, VL=440 V e carga Y", "Z=40/_30 ohm. Ache Ia, Ib e Ic."],
    5: ["vAN=120cos(wt+32), vBN=120cos(wt-88)", "e vCN=120cos(wt+152) V.", "Obtenha vAB, vBC e vCA."],
    6: ["Elabore e resolva um exemplo de", "conexao Y-Y equilibrada."],
    8: ["Y-Y abc: Van=100/_20 V, Zlinha=", "0.6+j1.2 e ZY=10+j14 ohm.", "Ache correntes e tensoes da carga."],
    9: ["Y-Y quadrifilar: Vfase=120 V,", "Zlinha=1+j2 e ZY=19+j13 ohm.", "Ache correntes de linha e neutro."],
    10: ["Na rede Y-Y desequilibrada da figura,", "ache a corrente na linha neutra."],
    11: ["Fonte Y positiva: Van=240/_0 V e", "carga delta Zp=2-j3 ohm.", "Ache VL e IL."],
    12: ["Elabore e resolva um exemplo de", "conexao Y-delta equilibrada."],
    13: ["Fonte Y de 110 V/fase, linhas 2 ohm", "e delta 9-j6 ohm/fase.", "Ache IL e a potencia media da carga."],
    15: ["VL=210 V; Zlinha=1+j1, Zdelta=", "24-j30 e ZY=12+j5 ohm.", "Ache a magnitude da corrente total."],
    16: ["Delta: IAC=5/_-30 A, sequencia", "positiva e VAB=110/_0 V.", "Ache correntes de linha e Zfase."],
    17: ["Carga delta equilibrada: Ia=5/_-25 A.", "Ache IAB, IBC e ICA."],
    18: ["Van=220/_60 V, sequencia positiva,", "delta Z=12+j9 ohm.", "Ache IAB, IBC e ICA."],
    19: ["Fonte delta de 173 V e carga delta", "30+j10 ohm/fase.", "Ache correntes de fase e linha."],
    20: ["Elabore e resolva um exemplo de", "conexao delta-delta equilibrada."],
    21: ["Fonte delta de 230 V e carga delta", "10+j8 ohm/fase. Ache IAC e IbB."],
    22: ["Fonte delta 440 V; Zlinha=2 ohm;", "Zdelta=12-j5 e ZY=4+j6 ohm.", "Ache Ia, Ib e Ic."],
    23: ["VL=202 V e delta Zp=25/_60 ohm.", "Ache IL e a potencia total pelo", "metodo dos dois wattimetros."],
    24: ["Fonte delta Vab=416/_30 V; linha", "1+j1 e delta 60/_30 ohm.", "Ache correntes de fase e linha."],
    26: ["Elabore e resolva um exemplo de", "fonte delta alimentando carga Y."],
    27: ["Fonte delta Vab=208/_0 V, linha", "2+j1 e carga Y 6+j4 ohm.", "Ache VL na carga."],
    28: ["Carga Y: VL=440 V, sequencia positiva", "e Zfase=25/_30 ohm.", "Ache correntes e tensoes de fase."],
    29: ["Y-delta: Van=240/_0 V, Zdelta=", "51-j45 e Zlinha=.4+j1.2 ohm.", "Ache S total da carga."],
    30: ["Carga Y: VL=208 V e", "Zfase=30/_45 ohm.", "Ache a potencia media total."],
    31: ["Delta em 240 V: cada fase absorve", "6 kW, FP=.8 atrasado, 60 Hz.", "Ache Zfase, IL e C por fase."],
    32: ["Elabore e resolva um exemplo de", "potencia trifasica equilibrada."],
    33: ["Carga Y recebe 4.8 kVA, Vfase=208 V", "e FP=.9 atrasado.", "Ache IL e VL da fonte."],
    34: ["Carga Y: Zfase=10-j16 ohm e VL=220 V.", "Ache IL e S total absorvida."],
    35: ["Em VL=230 V: delta 60+j30 ohm", "em paralelo com Y 40-j10 ohm.", "Ache IL, S total e FP."],
    36: ["Linha: VLcarga=4.2 kV, Zlinha=4+j1", "ohm/fase; carga 1 MVA, FP=.75 atr.", "Ache S, perda e VL na entrada."],
    37: ["Carga Y: P=12 kW, FP=.6 adiantado", "e VL=208 V. Ache IL e Zfase."],
    38: ["Fonte 110 V/fase, linha 1+j2 e", "carga Y 9+j12 ohm.", "Ache S total da carga."],
    39: ["Na rede delta desequilibrada da", "figura, ache a potencia real da carga."],
    40: ["Fonte 100 V/fase, linha 1+j.5 e", "delta 21-j24 ohm/fase.", "Ache a potencia media da carga."],
    41: ["Carga delta: P=5 kW, FP=.8 atrasado", "e VL=400 V. Ache a corrente de linha."],
    42: ["Carga Y 30+j40 ohm/fase recebe 7.2 kW.", "Ache IL e VL."],
    43: ["Para a rede do Problema 12.15,", "ache S complexa das cargas."],
    44: ["Linha 1+j3 ohm/fase alimenta delta", "com S=12+j5 kVA e VLcarga=240 V.", "Ache VLfonte e FP da fonte."],
    45: ["Carga Y: 450 kW, FP=.708 atrasado,", "VLcarga=440 V; linha .5+j2 ohm/fase.", "Ache a tensao de linha no gerador."],
    46: ["Tres resistores de 100 ohm em Y ou", "delta, alimentados por VL=110 V.", "Compare as potencias medias."],
    47: ["Cargas: 250kVA/.8 atr, 300kVA/.95 ad", "e 450kVA/FP1; VL=13.8 kV.", "Ache IL e FP da fonte."],
    48: ["Van=240/_0 V; linha 2+j3 ohm; delta", "Zab=40+j15, Zbc=60, Zca=18-j12.", "Ache correntes e S da fonte."],
    49: ["Carga por fase 20+j10 ohm, VL=220 V.", "Ache P total em delta e em Y."],
    50: ["Duas cargas Y em VL=240 V recebem", "8 kVA, FP=.6 atr. Uma consome 3 kW", "em FP1. Ache Zfase da outra."],
    51: ["Delta 240 V com carga desequilibrada:", "Z1=8+j6, Z2=4.2-j2.2, Z3=10 ohm.", "Ache correntes de fase e linha."],
    52: ["Y-Y quadrifilar: tensoes de 120 V e", "ZA=20/_60, ZB=30/_0, ZC=40/_30.", "Ache a corrente no neutro."],
    53: ["Elabore e resolva um exemplo de", "sistema trifasico desequilibrado."],
    54: ["Fonte Y de 210 V/fase; carga Y:", "ZA=80, ZB=60+j90, ZC=-j80 ohm.", "Com neutro, ache correntes e S."],
    55: ["VL=240 V, sequencia positiva; delta", "desequilibrado conforme a figura.", "Ache correntes de fase e S total."],
    56: ["Elabore e resolva um exemplo de", "sistema trifasico desequilibrado."],
    57: ["Fonte Y 110 V/fase e carga Y sem", "neutro: 80+j50, 20+j30, 60-j40.", "Ache as correntes de linha."],
    58: ["Resolva o Problema 12.10 por", "simulacao fasorial."],
    59: ["Fonte Y 100 V/fase, 60 Hz; carga Y", "R=40, C=.2mF e L=10mH.", "Ache VAN, VBN e VCN na carga."],
    60: ["Sistema trifilar: fontes 220 V, linhas", "4 ohm; Z1=15-j10, Z2=30+j20 e", "Z3=12+j5 ohm. Ache Io."],
    61: ["Fonte Y 240 V/fase, linha 4+j3, carga", "Y 10+j15 e capacitores -j36 ohm.", "Ache IaA e VBN."],
    62: ["Elabore e resolva um exemplo de", "simulacao de circuito trifasico."],
    63: ["Sistema desequilibrado: Zlinha=2+j1,", "Z1=40+j20, Z2=50-j30 e Z3=25 ohm.", "Ache IaA e IaC por simulacao."],
    64: ["Para a rede do Problema 12.39,", "ache correntes de linha e de fase", "por simulacao."],
    65: ["Na rede trifasica equilibrada da figura,", "ache IaA, IbB e IcC por simulacao."],
    66: ["Sistema Y quadrifilar, VL=208 V e", "cargas 40, 48 e 60 ohm.", "Ache Vn, correntes e leituras W."],
    67: ["Motor 260kVA/.85 atr em 120 V/fase", "mais lampadas 24, 15 e 9 kW.", "Ache W por linha e corrente neutra."],
    68: ["Alternador Y: VL=330 V, IL=8.4 A e", "Ptotal=4.5 kW. Ache VA, FP,", "corrente e tensao de fase."],
    69: ["Cargas: 16kVA/.85 atr, 12kVA/.6 atr", "e 8kW/FP1; VL=208 V; linha .4+j.8.", "Ache correntes e S das cargas."],
    70: ["Dois wattimetros: P1=1200 W, P2=400 W;", "VL=240 V, IL=6 A, carga Y.", "Ache FP e Z por fase."],
    71: ["Dois wattimetros medem a carga", "desequilibrada da figura, Vab=208/_0 V.", "Ache leituras e potencia aparente."],
    72: ["Ligue dois wattimetros na carga delta", "do Problema 12.11. Ache as leituras."],
    73: ["Para a rede Y com Z=10+j30 ohm e", "fontes indicadas, ache W1 e W2."],
    74: ["VL=208 V e carga Y 60-j30 ohm/fase.", "Ache as leituras dos wattimetros."],
    75: ["Corpo de 600 ohm: ache a corrente ao", "tocar 12 V e 120 V sem aterramento."],
    76: ["Mostre que, para mesma potencia, as", "perdas I^2R sao maiores em 120 V", "do que em 240 V."],
    77: ["Gerador entrega 3.6 kVA/.85 atr; carga", "recebe 2.5 kW e linha perde 80 W/fase.", "Ache as perdas no gerador."],
    78: ["Carga Y: VL=440 V, P=51 kW, S=60 kVA,", "60 Hz. Corrija o FP para .95 atrasado.", "Ache C em paralelo por fase."],
    79: ["Van=255/_0 V; linha 2 ohm/fase; carga", "Y 12+j5 ohm/fase. Ache correntes", "e tensoes de fase na carga."],
    80: ["Cargas: 6kVA/.83 atr, desconhecida e", "8kW/.7071 ad; VL=208 V, IL=84.6 A", "e FP total .8 atr. Ache a desconhecida."],
    81: ["Quatro cargas: 150kVA/.8 ad, 100kW/FP1,", "200kVA/.6 atr e 80kW+j95kVAR; linha", ".02+j.05 e VLcarga=480 V. Ache VLfonte."],
    82: ["VLcarga=2.4 kV; linha 2+j6 ohm/fase;", "carga Y 400kVA/.8 atr em paralelo com", "delta 10+j8. Ache VLfonte e Sfonte."],
    83: ["Motor 120HP, eficiencia .95, FP=.707 atr", "em paralelo com aquecedor 80kW/FP1.", "Com VL=480 V, ache IL."],
    84: ["Motor delta 4kVA/.72 atr em VL=440 V,", "capacitor 1.8kVAR entre a-b e lampada", "800W entre c-n. Ache Ia,Ib,Ic,In."],
    85: ["Projete aquecedor Y puramente resistivo", "para 27 kW em VL=240 V.", "Ache a resistencia por fase."],
    86: ["Sistema trifilar 120 V, linhas 1 ohm,", "cargas 24-j2 e 15+j4 ohm.", "Ache IaA, IbB e InN."],
    87: ["Sistema trifilar 115 V, 60 Hz, com", "linhas e cargas da figura. Ache In e", "a potencia complexa de cada fonte."],
}


RESULTS = {
    1: "(a) 231/_-30, 231/_-150, 231/_90 V; (b) 231/_30, 231/_150, 231/_-90 V.",
    2: "Sequencia acb; Vbn=120/_150 V.",
    3: "Sequencia abc; Van=440/_-110 V.",
    4: "Ia=6.35/_-60 A; Ib=6.35/_-180 A; Ic=6.35/_60 A.",
    5: "vAB=207.8cos(wt+62), vBC=207.8cos(wt-58), vCA=207.8cos(wt-178) V.",
    6: "Exemplo: Ia=7.047/_-40.24 A; Ib=7.047/_-160.24 A; Ic=7.047/_79.76 A.",
    8: "Ia=5.396/_-35.11 A; Ib=5.396/_-155.11 A; Ic=5.396/_84.89 A; |Vfase,carga|=92.84 V.",
    9: "Ia=4.8/_-36.87 A; Ib=4.8/_-156.87 A; Ic=4.8/_83.13 A; In=0.",
    10: "Vn=143.63/_96.75 V; Ia=16.62/_2.99 A; Ib=25.53/_-111.2 A; Ic=24.09/_107.8 A; In=0.",
    11: "VL=415.7 V; IL=199.69 A.",
    12: "Exemplo: ZY=6+j4; Ia=16.64/_-33.69 A; correntes restantes defasadas de 120 graus.",
    13: "IL=20.43 A; Pcarga=3.744 kW.",
    15: "Zeq,carga=7.812-j2.046 ohm; |IL|=13.66 A.",
    16: "Ia=8.66/_0, Ib=8.66/_-120, Ic=8.66/_120 A; Zfase=22/_-30 ohm.",
    17: "IAB=2.887/_5 A; IBC=2.887/_-115 A; ICA=2.887/_125 A.",
    18: "IAB=25.40/_53.13 A; IBC=25.40/_-66.87 A; ICA=25.40/_173.13 A.",
    19: "Ifase=5.47/_-18.43, /_-138.43, /_101.57 A; Ilinha=9.474/_-48.43, /_-168.43, /_71.57 A.",
    20: "Exemplo: Ifase=13.87/_-36.87 A; Ilinha=24.02/_-66.87 A; P=6.922 kW.",
    21: "IAC=17.96/_-98.66 A; IbB=31.1/_171.34 A.",
    22: "Ia=46.79/_-33.32 A; Ib=46.79/_-153.32 A; Ic=46.79/_86.68 A.",
    23: "IL=13.995 A; Ptotal=W1+W2=2.448 kW.",
    24: "Ilinha=11.24/_-30.98, /_-150.98, /_89.02 A; Ifase=6.489/_-0.98, /_-120.98, /_119.02 A.",
    26: "Exemplo: Ia=7.32/_-67.57 A; Ib e Ic sao Ia defasada em -120 e +120 graus.",
    27: "VL na carga=91.79 V.",
    28: "Van=254.0/_-30 V; Ia=10.16/_-60 A; Ib=10.16/_-180 A; Ic=10.16/_60 A.",
    29: "Scarga=(5.197+j4.586) kVA.",
    30: "Pcarga=1.020 kW.",
    31: "Zfase=6.144+j4.608 ohm; IL=18.04 A; C=207.2 uF por fase.",
    32: "Exemplo: I=9.238 A; S=5.12+j3.84 kVA; FP=.8 atrasado.",
    33: "IL=7.69 A; VL=360.3 V.",
    34: "Ia=6.732/_27.99 A; Scarga=1.36-j2.176 kVA.",
    35: "Ia=14.61-j5.953 A; St=10.081+j4.108 kVA; FP=.9261 atrasado.",
    36: "Scarga=750+j661.44 kVA; perda=226.76 kW; VLfonte=5.092 kV.",
    37: "IL=55.51 A; ZY=1.298-j1.731 ohm.",
    38: "Ia=6.394/_-54.46 A; Scarga=1.104+j1.472 kVA.",
    39: "Pcarga=431.1 W.",
    40: "Ia=9.119/_43.15 A; Pcarga=1.746 kW.",
    41: "IL=9.021 A.",
    42: "IL=8.944 A; VL=774.6 V.",
    43: "Scargas=4.373-j1.145 kVA.",
    44: "VLfonte=375.42 V; Sfonte=14.934+j13.802 kVA; FP=.7344 atrasado.",
    45: "VLgerador=2.109/_24.83 kV.",
    46: "Pdelta=363 W; PY=121 W; delta absorve tres vezes mais.",
    47: "IL=39.19 A RMS; FP=.9982 atrasado.",
    48: "Ia=24.34/_-12.65 A; Ib=10.81/_-142.6 A; Ic=19.27/_141.9 A; Sfonte=12.385+j.552 kVA.",
    49: "Pdelta=5.808 kW; PY=1.9356 kW.",
    50: "S2=1.8+j6.4 kVA; Zfase=2.35+j8.34 ohm.",
    51: "IAB=19.2-j14.4, IBC=-42.76+j27.09, ICA=-12-j20.78 A; Ia=31.2+j6.38, Ib=-61.96+j41.48, Ic=30.76-j47.86 A.",
    52: "Ia=6/_60 A; Ib=4/_0 A; Ic=3/_-150 A; In=5.748/_-140.0 A.",
    53: "Exemplo: Ia=6/_-90, Ib=3.328/_-153.69, Ic=3/_-150 A; St=332.3+j581.5 VA.",
    54: "Ia=2.625/_0, Ib=1.941/_-176.31, Ic=2.625/_-150 A; St=777.4-j212.0 VA.",
    55: "IAB=9.6/_-90, IBC=6/_120, ICA=8/_-150 A; St=3.103+j3.264 kVA.",
    56: "Exemplo: Vn=389.5/_-81.41 V; Ia=39.01/_-9.12, Ib=15.25/_112.8, Ic=33.54/_-166.41 A.",
    57: "Ia=1.9585/_-18.1 A; Ib=1.4656/_-130.55 A; Ic=1.947/_117.8 A.",
    58: "Os valores da simulacao coincidem com 12.10: In=0 e as tres correntes fecham a KCL.",
    59: "VAN=220.6/_-34.56 V; VBN=214.1/_-81.49 V; VCN=49.91/_-50.59 V.",
    60: "Io=19.53/_-15.17 A.",
    61: "IaA=11.15/_37 A; VBN=230.8/_-133.4 V.",
    62: "Exemplo: Vn=276.64/_17.42 V; Ia=7.903/_-152.15, Ib=14.512/_-62.27, Ic=16.539/_89.19 A.",
    63: "IaA=18.67/_158.9 A; IaC=12.38/_144.1 A.",
    64: "Ia=6.682/_-38.33, Ib=7.296/_-141.2, Ic=8.725/_87.07 A; IAB=4.540/_34.18, IBC=2.795/_-133.7, ICA=6.857/_102.5 A.",
    65: "IaA=11.02/_12 A; IbB=11.02/_-108 A; IcC=11.02/_132 A.",
    66: "Vfase=120 V; I1=3/_0, I2=2.5/_-120, I3=2/_120 A; In=.866/_150 A; W=360,300,240 W; P=900 W.",
    67: "W1=97.67 kW; W2=88.67 kW; W3=82.67 kW; |In|=108.97 A.",
    68: "|S|=4.801 kVA; FP=.9373; Ifase=8.4 A; Vfase=190.53 V.",
    69: "Ia=94.32/_-62.05 A; Ib=94.32/_177.95 A; Ic=94.32/_57.95 A; Scargas=28.8+j18.03 kVA.",
    70: "FP=.7559 atrasado; Zfase=17.46+j15.12 ohm.",
    71: "W1=2.590 kW; W2=4.808 kW; |St|=8.335 kVA.",
    72: "W1=74.41 kW; W2=5.342 kW; soma=79.75 kW.",
    73: "W1=2.360 kW; W2=-632.8 W.",
    74: "IL=1.790 A; leituras=371.7 W e 205.2 W; soma=576.9 W.",
    75: "(a) 20 mA; (b) 200 mA.",
    76: "Pperda(120)/Pperda(240)=4.",
    77: "Perdas no gerador=320 W.",
    78: "Qc=14.844 kVAR total; C=203.4 uF por fase.",
    79: "I=17.15/_-19.65, /_-139.65, /_100.35 A; Vcarga=223/_2.97, /_-117.03, /_122.97 V.",
    80: "Sdesconhecida=11.40+j22.94 kVA; |S|=25.62 kVA; FP=.445 atrasado.",
    81: "VLfonte=516 V.",
    82: "Scarga=1.374+j1.083 MVA; VLfonte=6.745 kV; Sfonte=2.436+j4.270 MVA.",
    83: "IL=183.42 A.",
    84: "Ia=1.736/_-3.29, Ib=5.825/_-121.0, Ic=7.827/_92.27 A; In=3.149/_-60 A.",
    85: "ZY=2.133 ohm por fase.",
    86: "IaA=4.869/_3.67 A; IbB=7.149/_166.9 A; InN=2.856/_-42.55 A.",
    87: "In=1.448/_-176.6 A; S1=1.252+j.7116 kVA; S2=1.085+j.7212 kVA.",
}


# Dados numericos que nao pertencem a um simbolo eletrico desenhado.  Cada
# nome tem no maximo 12 caracteres (limite do AppVar v2) e cada lista fica
# abaixo do antigo teto de 16; receitas podem ampliar ate 64. Valores complexos sao
# separados em partes R/X para que qualquer parcela possa ser alterada.
PARAMS = {
    1: [("Vab_V", 400.0)],
    2: [("Van_V", 120.0), ("Van_deg", 30.0),
        ("Vcn_V", 120.0), ("Vcn_deg", -90.0)],
    3: [("Vbn_V", 440.0), ("Vbn_deg", 130.0),
        ("Vcn_V", 440.0), ("Vcn_deg", 10.0)],
    4: [("VL_V", 440.0), ("Zmag_ohm", 40.0), ("Z_deg", 30.0)],
    5: [("VmA_V", 120.0), ("PhA_deg", 32.0),
        ("VmB_V", 120.0), ("PhB_deg", -88.0),
        ("VmC_V", 120.0), ("PhC_deg", 152.0)],
    8: [("Van_V", 100.0), ("Van_deg", 20.0),
        ("Zlin_R", 0.6), ("Zlin_X", 1.2),
        ("ZY_R", 10.0), ("ZY_X", 14.0)],
    9: [("Vph_V", 120.0), ("Zlin_R", 1.0), ("Zlin_X", 2.0),
        ("ZY_R", 19.0), ("ZY_X", 13.0)],
    16: [("Iac_A", 5.0), ("Iac_deg", -30.0),
         ("Vab_V", 110.0), ("Vab_deg", 0.0)],
    17: [("Ia_A", 5.0), ("Ia_deg", -25.0)],
    23: [("VL_V", 202.0), ("Zmag_ohm", 25.0), ("Z_deg", 60.0)],
    24: [("Vab_V", 416.0), ("Vab_deg", 30.0),
         ("Zlin_R", 1.0), ("Zlin_X", 1.0),
         ("Zd_mag", 60.0), ("Zd_deg", 30.0)],
    27: [("Vab_V", 208.0), ("Vab_deg", 0.0),
         ("Zlin_R", 2.0), ("Zlin_X", 1.0),
         ("ZY_R", 6.0), ("ZY_X", 4.0)],
    28: [("VL_V", 440.0), ("Zmag_ohm", 25.0), ("Z_deg", 30.0)],
    29: [("Van_V", 240.0), ("Van_deg", 0.0),
         ("Zd_R", 51.0), ("Zd_X", -45.0),
         ("Zlin_R", 0.4), ("Zlin_X", 1.2)],
    31: [("VL_V", 240.0), ("Pph_W", 6000.0),
         ("FP", 0.8), ("f_Hz", 60.0)],
    32: [("VL_V", 400.0), ("P_W", 5120.0), ("Q_VAR", 3840.0)],
    33: [("S_VA", 4800.0), ("Vph_V", 208.0), ("FP", 0.9)],
    34: [("Z_R", 10.0), ("Z_X", -16.0), ("VL_V", 220.0)],
    35: [("VL_V", 230.0), ("Zd_R", 60.0), ("Zd_X", 30.0),
         ("ZY_R", 40.0), ("ZY_X", -10.0)],
    36: [("VLload_V", 4200.0), ("Zlin_R", 4.0), ("Zlin_X", 1.0),
         ("S_VA", 1000000.0), ("FP", 0.75)],
    37: [("P_W", 12000.0), ("FP", 0.6), ("VL_V", 208.0)],
    41: [("P_W", 5000.0), ("FP", 0.8), ("VL_V", 400.0)],
    42: [("P_W", 7200.0), ("ZY_R", 30.0), ("ZY_X", 40.0)],
    44: [("Zlin_R", 1.0), ("Zlin_X", 3.0),
         ("S_P_W", 12000.0), ("S_Q_VAR", 5000.0), ("VLload_V", 240.0)],
    45: [("P_W", 450000.0), ("FP", 0.708), ("VLload_V", 440.0),
         ("Zlin_R", 0.5), ("Zlin_X", 2.0)],
    46: [("R_ohm", 100.0), ("VL_V", 110.0)],
    47: [("S1_VA", 250000.0), ("FP1", 0.8),
         ("S2_VA", 300000.0), ("FP2", 0.95),
         ("P3_W", 450000.0), ("VL_V", 13800.0)],
    48: [("Van_V", 240.0), ("Van_deg", 0.0),
         ("Zlin_R", 2.0), ("Zlin_X", 3.0),
         ("Zab_R", 40.0), ("Zab_X", 15.0),
         ("Zbc_R", 60.0), ("Zbc_X", 0.0),
         ("Zca_R", 18.0), ("Zca_X", -12.0)],
    49: [("Z_R", 20.0), ("Z_X", 10.0), ("VL_V", 220.0)],
    50: [("VL_V", 240.0), ("S_VA", 8000.0),
         ("FP", 0.6), ("P1_W", 3000.0)],
    52: [("Vph_V", 120.0),
         ("ZA_mag", 20.0), ("ZA_deg", 60.0),
         ("ZB_mag", 30.0), ("ZB_deg", 0.0),
         ("ZC_mag", 40.0), ("ZC_deg", 30.0)],
    54: [("Vph_V", 210.0), ("ZA_R", 80.0), ("ZA_X", 0.0),
         ("ZB_R", 60.0), ("ZB_X", 90.0),
         ("ZC_R", 0.0), ("ZC_X", -80.0)],
    61: [("Xcap_ohm", -36.0)],
    67: [("Smotor_VA", 260000.0), ("FPmotor", 0.85),
         ("Vph_V", 120.0), ("PA_W", 24000.0),
         ("PB_W", 15000.0), ("PC_W", 9000.0)],
    68: [("VL_V", 330.0), ("IL_A", 8.4), ("P_W", 4500.0)],
    69: [("S1_VA", 16000.0), ("FP1", 0.85),
         ("S2_VA", 12000.0), ("FP2", 0.6),
         ("P3_W", 8000.0), ("VL_V", 208.0),
         ("Zlin_R", 0.4), ("Zlin_X", 0.8)],
    70: [("P1_W", 1200.0), ("P2_W", 400.0),
         ("VL_V", 240.0), ("IL_A", 6.0)],
    75: [("R_ohm", 600.0), ("V1_V", 12.0), ("V2_V", 120.0)],
    76: [("V1_V", 120.0), ("V2_V", 240.0)],
    77: [("Sgen_VA", 3600.0), ("FPgen", 0.85),
         ("Pload_W", 2500.0), ("Plossph_W", 80.0)],
    78: [("VL_V", 440.0), ("P_W", 51000.0), ("S_VA", 60000.0),
         ("f_Hz", 60.0), ("FPnovo", 0.95)],
    79: [("Van_V", 255.0), ("Van_deg", 0.0), ("Zlin_R", 2.0),
         ("ZY_R", 12.0), ("ZY_X", 5.0)],
    80: [("S1_VA", 6000.0), ("FP1", 0.83),
         ("P3_W", 8000.0), ("FP3", 0.7071),
         ("VL_V", 208.0), ("IL_A", 84.6), ("FPtot", 0.8)],
    81: [("S1_VA", 150000.0), ("FP1", 0.8),
         ("P2_W", 100000.0), ("S3_VA", 200000.0), ("FP3", 0.6),
         ("P4_W", 80000.0), ("Q4_VAR", 95000.0),
         ("Zlin_R", 0.02), ("Zlin_X", 0.05), ("VLload_V", 480.0)],
    82: [("VLload_V", 2400.0), ("Zlin_R", 2.0), ("Zlin_X", 6.0),
         ("S1_VA", 400000.0), ("FP1", 0.8),
         ("Zd_R", 10.0), ("Zd_X", 8.0)],
    83: [("HP", 120.0), ("HP_W", 746.0), ("efic", 0.95),
         ("FP", 0.707), ("Pheat_W", 80000.0), ("VL_V", 480.0)],
    84: [("Smotor_VA", 4000.0), ("FPmotor", 0.72), ("VL_V", 440.0),
         ("Qcap_VAR", 1800.0), ("Plamp_W", 800.0)],
    85: [("P_W", 27000.0), ("VL_V", 240.0)],
}


PROJECTS = {6, 12, 20, 26, 32, 53, 56, 62}
SEQUENCE = {1, 2, 3, 5}
PF_CORRECTION = {31, 78}
WATTMETERS = {23, 66, 67, 70, 71, 72, 73, 74}
UNBALANCED = {10, 39, 48, 51, 52, 54, 55, 56, 57, 58, 59, 60,
              61, 62, 63, 64, 66, 67, 71, 84, 86, 87}
POWER = {23, 29, 30, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43,
         44, 45, 46, 47, 49, 50, 68, 69, 77, 80, 81, 82, 83, 85}


SPECIAL = {
    6: ["1) Adote Vfase=120 V, Zlinha=1+j2.",
        "2) Escolha ZY=12+j9 ohm por fase.",
        "3) Ztotal=13+j11 ohm.",
        "4) Ia=120/(13+j11); gire mais/menos 120 graus."],
    10: ["1) Some Zlinha a cada impedancia de fase.",
         "2) Sem neutro: Vn=sum(Vk/Zk)/sum(1/Zk).",
         "3) Ik=(Vk-Vn)/Zk; confira Ia+Ib+Ic=0."],
    12: ["1) Adote fonte Y de 120 V/fase.",
         "2) Escolha carga delta 18+j12 ohm/fase.",
         "3) Converta: ZY=(18+j12)/3=6+j4.",
         "4) Ia=120/(6+j4); gire mais/menos 120 graus."],
    15: ["1) Converta delta: Zdy=(24-j30)/3.",
         "2) Zeq=Zdy||(12+j5)=7.812-j2.046.",
         "3) Ia=Vfase/(Zlinha+Zeq)."],
    16: ["1) Ica=-Iac=5/_150 A.",
         "2) Em delta positivo, Iab=5/_30 A.",
         "3) Ia=Iab-Ica; gire 120 graus.",
         "4) Zfase=Vab/Iab."],
    17: ["1) Em delta: Ia=sqrt(3) Iab/_-30.",
         "2) Logo Iab=Ia/sqrt(3)/_-30.",
         "3) Ibc e Ica sao giros de 120 graus."],
    20: ["1) Adote fonte e carga delta, VL=208 V.",
         "2) Escolha Zdelta=12+j9 ohm/fase.",
         "3) Ifase=VL/Zdelta; Ilinha=sqrt(3)Ifase/_-30.",
         "4) P=3 VL^2 Re(Z)/|Z|^2."],
    22: ["1) Zdelta/3=4-j1.667 ohm.",
         "2) Zeq=(4-j1.667)||(4+j6).",
         "3) Van=440/sqrt(3)/_-30 V.",
         "4) Ia=Van/(2+Zeq); gire 120 graus."],
    24: ["1) Van=Vab/sqrt(3)/_-30=240/_0 V.",
         "2) Zdelta/3=20/_30 ohm.",
         "3) Ia=Van/(1+j1+Zdelta/3).",
         "4) Volte ao delta para IAB,IBC,ICA."],
    26: ["1) Adote Vab=208/_0 V e linha 1+j1.",
         "2) Escolha carga Y 12+j9 ohm/fase.",
         "3) Van=208/sqrt(3)/_-30 V.",
         "4) Ia=Van/(13+j10); gire mais/menos 120 graus."],
    32: ["1) Adote VL=400 V e carga Y 20+j15 ohm.",
         "2) Vfase=400/sqrt(3); I=Vfase/(20+j15).",
         "3) S=3|I|^2(20+j15).",
         "4) FP=P/|S|."],
    35: ["1) Converta o delta para Y: 20+j10.",
         "2) Some as admitancias das duas cargas.",
         "3) Ia=Vfase vezes Yeq.",
         "4) St=3 Vfase vezes conjugado(Ia)."],
    36: ["1) Scarga=1M(.75+j sqrt(1-.75^2)).",
         "2) I=conjugado[S/(sqrt(3) VL)].",
         "3) Pperda=3|I|^2 Rlinha.",
         "4) Vs,fase=Vr,fase+I Zlinha."],
    39: ["1) Resolva os tres nos A,B,C por KCL.",
         "2) Corrente de linha=(Vfonte-Vcarga)/5.",
         "3) Some |Iramo|^2 R de cada ramo."],
    44: ["1) I=conjugado[S/(sqrt(3) VL)].",
         "2) Vs,fase=VL/sqrt(3)+I(1+j3).",
         "3) Sfonte=Scarga+3|I|^2(1+j3).",
         "4) FP=Re(Sfonte)/|Sfonte|."],
    45: ["1) Scarga=450k(.708+j sqrt(1-.708^2)).",
         "2) I=conjugado[Scarga/(sqrt(3) vezes 440)].",
         "3) Vs,fase=440/sqrt(3)+I(.5+j2).",
         "4) VLgerador=sqrt(3) vezes Vs,fase."],
    47: ["1) Converta cada carga para P+jQ.",
         "2) Carga adiantada entra com Q negativo.",
         "3) St=S1+S2+S3.",
         "4) I=conjugado[St/(sqrt(3) VL)]; FP=P/|S|."],
    48: ["1) Escreva KCL simultanea em A,B,C.",
         "2) Inclua Zab,Zbc,Zca e Zlinha.",
         "3) Ik=(Vk,fonte-Vk,carga)/Zlinha.",
         "4) Sfonte=sum(Vk vezes conjugado(Ik))."],
    49: ["1) Pdelta=3 VL^2 R/|Z|^2.",
         "2) Em Y, Vfase=VL/sqrt(3).",
         "3) PY=3 Vfase^2 R/|Z|^2.",
         "4) Logo Pdelta=3 PY."],
    50: ["1) St=8k(.6+j.8)=4.8+j6.4 kVA.",
         "2) S2=St-3k=1.8+j6.4 kVA.",
         "3) Zfase=3 Vfase^2/conjugado(S2)."],
    51: ["1) IAB=VAB/Z1, IBC=VBC/Z2.",
         "2) ICA=VCA/Z3.",
         "3) Ia=IAB-ICA; Ib=IBC-IAB.",
         "4) Ic=ICA-IBC; confira soma zero."],
    52: ["1) Ia=Van/ZA; Ib=Vbn/ZB; Ic=Vcn/ZC.",
         "2) Pela KCL, In=-(Ia+Ib+Ic).",
         "3) Confira In+Ia+Ib+Ic=0."],
    53: ["1) Adote fonte Y de 120 V e neutro ligado.",
         "2) Escolha ZA=j20, ZB=30+j20, ZC=-j40.",
         "3) Ik=Vkn/Zk para cada fase.",
         "4) St=sum(Vkn vezes conjugado(Ik))."],
    54: ["1) Neutros ligados: cada fase e independente.",
         "2) Ik=Vkn/Zk para A, B e C.",
         "3) St=sum(Vkn vezes conjugado(Ik))."],
    55: ["1) Cada ramo delta recebe uma tensao de linha.",
         "2) IAB=VAB/ZAB, IBC=VBC/ZBC.",
         "3) ICA=VCA/ZCA; St=sum(V I*)."],
    56: ["1) Adote fonte Y 120 V e carga sem neutro:",
         "2) ZA=j10, ZB=20 e ZC=-j15 ohm.",
         "3) Vn=sum(Vk/Zk)/sum(1/Zk).",
         "4) Ik=(Vk-Vn)/Zk; confira soma zero."],
    57: ["1) Carga Y sem neutro: ache Vn por KCL.",
         "2) Vn=sum(Vk/Zk)/sum(1/Zk).",
         "3) Ik=(Vk-Vn)/Zk; confira soma zero."],
    59: ["1) Em 60 Hz: Zc=1/(jwC), Zl=jwL.",
         "2) Resolva o neutro flutuante por KCL.",
         "3) VKN=Vk-Ik Zk para cada fase."],
    60: ["1) Modele os tres condutores de 4 ohm.",
         "2) Escreva KCL nos nos A,N,B.",
         "3) Resolva o sistema complexo 3x3.",
         "4) Io=(VA-VB)/Z3."],
    61: ["1) Monte cada linha como 4+j3 ohm.",
         "2) Inclua a carga 10+j15 e -j36.",
         "3) Resolva A,B,C,N por KCL.",
         "4) Leia IaA e VBN no sistema."],
    62: ["1) Adote fonte Y 120 V, 60 Hz e Zlinha=1+j.754.",
         "2) Use ZA=20, ZB=-j26.5 e ZC=j18.85.",
         "3) Resolva o neutro flutuante por KCL.",
         "4) No simulador, confira Ia+Ib+Ic=0."],
    63: ["1) Converta a fonte para fasores RMS.",
         "2) Resolva os nos da carga e correntes de linha.",
         "3) IaC e obtida pela queda no ramo A-C."],
    64: ["1) Resolva A,B,C com linhas de 5 ohm.",
         "2) Ilinha=(Vfonte-Vcarga)/5.",
         "3) IAB=(VA-VB)/(8-j6), e analogos."],
    66: ["1) Vfase=208/sqrt(3)=120 V.",
         "2) Ik=Vk/Rk e In=-(I1+I2+I3).",
         "3) Cada wattimetro le Vfase^2/Rk.",
         "4) Some as tres leituras."],
    67: ["1) Motor: Sm=260(.85+j.5268) kVA.",
         "2) Divida Sm igualmente entre as fases.",
         "3) Some a lampada de cada fase.",
         "4) Wk=Re(Sk); In=-soma(Ik)."],
    68: ["1) |S|=sqrt(3) VL IL.",
         "2) FP=P/|S|.",
         "3) Em Y, Ifase=Ilinha.",
         "4) Vfase=VL/sqrt(3)."],
    69: ["1) Converta cada carga em P+jQ.",
         "2) Some Scargas e obtenha Ia=conjugado(S/3Van).",
         "3) Ib e Ic sao giros de 120 graus.",
         "4) A impedancia de linha nao altera Scargas."],
    70: ["1) P=P1+P2=1600 W.",
         "2) tan(phi)=sqrt(3)(P1-P2)/(P1+P2).",
         "3) |Zfase|=(VL/sqrt(3))/IL.",
         "4) Z=|Z|/_phi."],
    71: ["1) Resolva as correntes da carga delta.",
         "2) W1=Re(Vab vezes conjugado(Ia)).",
         "3) W2=Re(Vcb vezes conjugado(Ic)).",
         "4) |St|=|sum(Vfase Iramo*)|."],
    72: ["1) Ache IL a partir de Vlinha e Zdelta.",
         "2) W1=VL IL cos(30+phi).",
         "3) W2=VL IL cos(30-phi).",
         "4) W1+W2=Ptotal."],
    73: ["1) Calcule as tres correntes de linha.",
         "2) Use a polaridade de cada bobina indicada.",
         "3) W=Re(Vbobina vezes conjugado(Ibobina))."],
    74: ["1) IL=(208/sqrt(3))/|60-j30|.",
         "2) phi=arg(60-j30)=-26.565 graus.",
         "3) W1,W2=VL IL cos(30 mais/menos phi)."],
    75: ["1) Use a lei de Ohm: I=V/R.",
         "2) Para 12 V: I=12/600.",
         "3) Para 120 V: I=120/600."],
    76: ["1) Para carga nominal P, I=P/V.",
         "2) Pperda=I^2R=P^2 R/V^2.",
         "3) Divida a perda em 120 V pela de 240 V."],
    77: ["1) Pgerador,saida=3.6k vezes .85=3.060 kW.",
         "2) Perda na linha=3 vezes 80=240 W.",
         "3) Pentrada,carga+linha=2.740 kW.",
         "4) Perda no gerador=3.060-2.740 kW."],
    78: ["1) Q=sqrt(S^2-P^2)=31.607 kVAR.",
         "2) Qalvo=P tan(acos .95)=16.763 kVAR.",
         "3) Qc=Q-Qalvo; por fase Qc/3.",
         "4) C=(Qc/3)/(2 pi f Vfase^2)."],
    83: ["1) Pmotor,ent=(120 vezes 746)/.95.",
         "2) Smotor=Pmotor,ent/.707 com atraso.",
         "3) Some Saquecedor=80+j0 kVA.",
         "4) IL=|St|/(sqrt(3) vezes 480)."],
    80: ["1) |St|=sqrt(3) VL IL; St=|St|(.8+j.6).",
         "2) S1=6k(.83+j sqrt(1-.83^2)).",
         "3) S3=8-j8 kVA.",
         "4) S2=St-S1-S3."],
    81: ["1) Converta as quatro cargas para P+jQ.",
         "2) I=conjugado[St/(sqrt(3) VLcarga)].",
         "3) Vs,fase=Vr,fase+I(.02+j.05).",
         "4) VLfonte=sqrt(3)|Vs,fase|."],
    82: ["1) S1=320+j240 kVA.",
         "2) S2=3 VL^2/conjugado(10+j8).",
         "3) I=conjugado[Scarga/(sqrt(3) VL)].",
         "4) Some a queda e 3|I|^2 Zlinha."],
    84: ["1) Motor: IL=4k/(sqrt(3)440), atraso acos .72.",
         "2) Capacitor: Iab=conjugado(-j1.8k/Vab).",
         "3) Lampada: Ic=conjugado(800/Vcn).",
         "4) Some por linha; In=-soma(Ia,Ib,Ic)."],
    85: ["1) Em Y, P=3 Vfase^2/Rfase.",
         "2) Como Vfase=VL/sqrt(3), P=VL^2/Rfase.",
         "3) Rfase=240^2/27000."],
    86: ["1) Defina tensoes desconhecidas VA,VN,VB.",
         "2) Inclua os tres resistores de linha de 1 ohm.",
         "3) Resolva as tres KCL complexas.",
         "4) Correntes saem pelas quedas nas linhas."],
    87: ["1) Em 60 Hz, ZL=15+j18.85 ohm.",
         "2) Resolva VA,VN,VB por KCL.",
         "3) In e a queda no resistor neutro/2.",
         "4) Para cada fonte, S=V vezes conjugado(I)."],
}


def _solution(number):
    if number in SPECIAL:
        lines = list(SPECIAL[number])
    elif number in SEQUENCE:
        lines = ["1) Fixe um fasor de referencia.",
                 "2) Sequencia positiva gira -120 graus;",
                 "   sequencia negativa gira +120 graus.",
                 "3) Use Vxy=Vxn-Vyn e sqrt(3)."]
    elif number in PF_CORRECTION:
        lines = ["1) Obtenha P+jQ da carga original.",
                 "2) Qalvo=P tan(acos FP alvo).",
                 "3) Qc=Qalvo-Q; divida entre as fases.",
                 "4) |Qc,fase|=w C Vfase^2."]
    elif number in WATTMETERS:
        lines = ["1) Resolva tensoes e correntes RMS.",
                 "2) Respeite a polaridade de cada bobina.",
                 "3) W=Re[Vbobina vezes conjugado(Ibobina)].",
                 "4) A soma fornece a potencia ativa."]
    elif number in UNBALANCED:
        lines = ["1) Trabalhe com fasores RMS por fase.",
                 "2) Escreva KCL nos nos nao aterrados.",
                 "3) Resolva o sistema complexo.",
                 "4) Confira KCL: soma das linhas e zero."]
    elif number in POWER:
        lines = ["1) Em Y, Vfase=VL/sqrt(3); em delta, Vfase=VL.",
                 "2) S=3 Vfase vezes conjugado(Ifase).",
                 "3) Ilinha=conjugado[S/(sqrt(3) VL)].",
                 "4) FP=P/|S|; sinal de Q indica atraso/avanco."]
    else:
        lines = ["1) Determine Vfase: em Y use Vkn; em delta,",
                 "   Van=Vab/sqrt(3)/_-30.",
                 "2) Para carga delta use ZY=Zdelta/3;",
                 "   para carga Y preserve a impedancia.",
                 "3) Ia=Van/(Zlinha+ZY).",
                 "4) Obtenha Ib e Ic por giros de 120 graus."]
    lines.append("= " + RESULTS[number])
    if "p12_%d" % number in CIRCUITS or number in PARAMS:
        lines.append("# Edicao: use Dados atuais e repita as mesmas equacoes.")
    return lines


SKIP = {7, 14, 25}
EXERCISES = []
for number in range(1, 88):
    if number in SKIP:
        continue
    ex_id = "p12_%d" % number
    exercise = {
        "id": ex_id,
        "title": "Problema 12.%d" % number,
        "subject": "Trifasico",
        "priority": 100 + number,
        "source": "Livro, Cap.12, Problema 12.%d" % number,
        "statement": STATEMENTS[number],
        "static": True,
        "solution": _solution(number),
    }
    if number in PARAMS:
        exercise["params"] = PARAMS[number]
    if ex_id in CIRCUITS or number in PARAMS:
        exercise["engine"] = {"visual_only": True, "omega": 2 * 3.14159265 * 60}
    EXERCISES.append(exercise)
