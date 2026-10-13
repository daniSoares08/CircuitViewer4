"""Capitulo 11 completo (problemas 11.1--11.97).

Os casos prioritarios 11.1, 11.8, 11.15, 11.38, 11.41, 11.53 e 11.69
permanecem em ``ch11.py``. Este modulo acrescenta os demais problemas do
livro. Circuitos numericos simples usam a rota de potencia ao vivo depois
de uma edicao. AOPs, wattimetros, formas de onda e exercicios de projeto
preservam a deducao algebrica, mas continuam com valores e fontes editaveis.
"""

from content.ch10_full import _bridge, _loop, _opamp, _port

SUBJECTS = ["Potencia AC", "Max Potencia AC"]


def _bus(source, branches, arrow=None):
    """Fonte e ate quatro ramos paralelos, com colunas independentes."""
    y1, y2 = 78, 194
    xs = [98, 154, 210, 266]
    ops = [("vsrc_v", 40, y1, y2, source),
           ("wire", 40, y1, 280, y1), ("wire", 40, y2, 280, y2)]
    for x, (kind, label) in zip(xs, branches):
        if kind in ("isrc_v", "dis_v"):
            ops.append((kind, x, y1, y2, label, True))
        else:
            ops.append((kind, x, y1, y2, label))
    if arrow:
        ops.append(("arr_h", 52, 58, 110, arrow, True))
    ops.append(("gnd", 160, y2))
    return ops


def _source_port(source, series=(), shunts=()):
    """Rede alimentada a esquerda e aberta nos terminais a-b."""
    y1, y2 = 78, 194
    ops = [("vsrc_v", 40, y1, y2, source),
           ("wire", 40, y2, 286, y2), ("term", 286, y1, "a"),
           ("term", 286, y2, "b"), ("gnd", 160, y2)]
    points = [40, 108, 176, 244, 286]
    x = points[0]
    for i, (kind, label) in enumerate(series):
        nx = points[min(i + 1, len(points) - 1)]
        ops.append((kind, x, y1, nx, label))
        x = nx
    ops.append(("wire", x, y1, 286, y1))
    for x, kind, label in shunts:
        if kind in ("isrc_v", "dis_v"):
            ops.append((kind, x, y1, y2, label, True))
        else:
            ops.append((kind, x, y1, y2, label))
    return ops


def _wave(points, labels=()):
    """Forma de onda diagramatica dentro da area util da calculadora."""
    ops = [("wire", 42, 176, 286, 176), ("wire", 48, 82, 48, 186),
           ("lbl", "t", 290, 172), ("lbl", "x(t)", 30, 70)]
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        ops.append(("wire", x1, y1, x2, y2))
    for text, x, y in labels:
        ops.append(("lbl", text, x, y))
    return ops


def _power_bus(source, branches):
    """Diagrama de cargas: valor numerico editavel e unidade separada."""
    y1, y2 = 78, 194
    xs = [92, 154, 216, 274]
    ops = [("vsrc_v", 36, y1, y2, source),
           ("wire", 36, y1, 286, y1), ("wire", 36, y2, 286, y2)]
    for x, value, note in branches:
        ops.append(("res_v", x, y1, y2, value))
        if note:
            ops.append(("lbl", note, max(2, x - 24), 204))
    ops.append(("gnd", 164, y2))
    return ops


# Figuras eletricas e formas de onda do capitulo. Os blocos de carga usam
# resistores como simbolo visual; a solucao trabalha com P, Q e fator de
# potencia, nao com a resistencia desenhada.
CIRCUITS = {
    "p11_2": [("isrc_v", 132, 78, 194, "2/_0A", True),
                ("cap_v", 54, 78, 194, "0.25F"),
                ("ind_h", 54, 78, 210, "1H"),
                ("res_v", 210, 78, 194, "5"),
                ("wire", 54, 78, 132, 78), ("wire", 54, 194, 210, 194),
                ("gnd", 132, 194), ("lbl", "Xc=-j4", 24, 132)],
    "p11_4": _loop("10V", [("res_h", "4")],
                     [(1, "ind_v", "2H")], right=("cap_v", "0.1F")),
    "p11_5": _loop("8/_-40V", [("res_h", "1"), ("res_h", "2")],
                     [(1, "ind_v", "3H")], right=("cap_v", "0.25F")),
    "p11_6": [("isrc_v", 42, 78, 194, "6A", True),
                ("wire", 42, 78, 132, 78), ("wire", 42, 194, 278, 194),
                ("res_v", 112, 78, 136, "50"),
                ("cap_v", 112, 136, 194, "40uF"),
                ("dvs_h", 132, 78, 214, "20ix", True),
                ("ind_v", 256, 78, 136, "20mH"),
                ("res_v", 256, 136, 194, "10"),
                ("wire", 214, 78, 256, 78), ("arr_v", 92, 96, 150, "ix", False),
                ("gnd", 160, 194)],
    "p11_7": [("vsrc_v", 36, 78, 194, "8/_20V"),
                ("res_h", 36, 78, 112, "4"),
                ("dvs_v", 112, 78, 194, "0.1"),
                ("wire", 112, 78, 174, 78), ("isrc_v", 174, 78, 194, "8A", False),
                ("wire", 174, 78, 218, 78), ("ind_v", 218, 78, 194, "5H"),
                ("cap_h", 218, 78, 270, "0.2F"),
                ("res_v", 270, 78, 194, "10"),
                ("wire", 36, 194, 270, 194), ("arr_h", 64, 58, 106, "Io", True),
                ("gnd", 160, 194)],
    "p11_9": _opamp("10/_30V", [("res_h", "2k"), ("ind_h", "4H")],
                      [("res_h", "10k"), ("ind_h", "6H")], None, True) +
               [("res_v", 260, 109, 148, "20k"),
                ("cap_v", 260, 148, 196, "12nF")],
    "p11_10": _opamp("1V", [("res_h", "10")], [("res_h", "10")]) +
                [("res_v", 260, 109, 196, "10")],
    "p11_12": [("vsrc_v", 38, 78, 194, "165/_0V"),
                 ("res_h", 38, 126, 132, "4"),
                 ("ind_h", 38, 78, 238, "2H"),
                 ("cap_h", 132, 126, 238, "0.333F"),
                 ("res_v", 238, 78, 194, "5"),
                 ("wire", 38, 78, 38, 126), ("wire", 38, 194, 286, 194),
                 ("wire", 132, 126, 286, 126), ("term", 286, 126, "a"),
                 ("term", 286, 194, "b"), ("gnd", 160, 194)],
    "p11_14": _bus("2A", [("ind_v", "1H"), ("res_v", "10"),
                             ("cap_v", "0.1F"), ("res_v", "20")]),
    "p11_16": [("vsrc_v", 32, 108, 194, "10V"),
                 ("res_h", 32, 108, 96, "2"),
                 ("res_h", 96, 108, 194, "4"),
                 ("wire", 194, 108, 270, 108),
                 ("cap_v", 96, 108, 194, "0.05F"),
                 ("ind_v", 194, 108, 194, "1H"),
                 ("wire", 96, 108, 96, 54),
                 ("wire", 96, 54, 194, 54),
                 ("dis_v", 194, 54, 96, "0.5Vo", False),
                 ("wire", 194, 96, 194, 108),
                 ("imp_v", 270, 108, 194, "1"),
                 ("wire", 32, 194, 270, 194),
                 ("lbl", "Vo", 72, 144), ("lbl", "ZL", 286, 146),
                 ("gnd", 150, 194)],
    "p11_17": [("isrc_v", 278, 78, 194, "5/_90A", True),
                 ("cap_v", 80, 78, 136, "0.1F"),
                 ("res_v", 110, 136, 194, "40"),
                 ("res_v", 160, 78, 136, "30"),
                 ("ind_v", 160, 136, 194, "20H"),
                 ("wire", 80, 78, 278, 78), ("wire", 110, 194, 278, 194),
                 ("term", 50, 136, "a"), ("term", 208, 136, "b"),
                 ("wire", 50, 136, 110, 136), ("wire", 160, 136, 208, 136),
                 ("lbl", "ZL", 142, 126), ("gnd", 278, 194)],
    "p11_18": [("imp_v", 48, 58, 126, "40"),
                 ("imp_v", 48, 126, 194, "j30"),
                 ("res_h", 48, 126, 130, "40"),
                 ("vsrc_v", 130, 58, 112, "60/_0V", True),
                 ("wire", 130, 112, 130, 126),
                 ("wire", 130, 126, 130, 140),
                 ("isrc_v", 130, 140, 194, "5/_0A", True),
                 ("imp_v", 270, 58, 126, "-j10"),
                 ("res_h", 130, 126, 270, "80"),
                 ("imp_v", 270, 126, 194, "1"),
                 ("wire", 48, 58, 270, 58),
                 ("wire", 48, 194, 270, 194),
                 ("lbl", "ZL", 286, 146), ("gnd", 180, 194)],
    "p11_19": _bus("33A", [("ind_v", "1H"), ("res_v", "6"),
                              ("cap_v", "0.5F"), ("res_v", "10")]),
    "p11_20": [("vsrc_v", 32, 108, 194, "165V"),
                 ("res_h", 32, 108, 98, "40"),
                 ("wire", 98, 108, 176, 108),
                 ("imp_v", 118, 108, 194, "j20"),
                 ("imp_v", 168, 108, 194, "-j10"),
                 ("dvs_h", 176, 108, 240, "4Io", True),
                 ("wire", 240, 108, 286, 108),
                 ("imp_v", 248, 108, 194, "-j10"),
                 ("res_v", 286, 108, 194, "1"),
                 ("wire", 32, 194, 286, 194),
                 ("arr_h", 40, 82, 88, "Io", True),
                 ("lbl", "RL", 298, 146), ("gnd", 204, 194)],
    "p11_21": [("vsrc_v", 40, 78, 194, "120/_60V"),
                 ("res_h", 40, 78, 110, "100"),
                 ("cap_h", 110, 78, 180, "0.1F"),
                 ("res_v", 110, 78, 136, "40"),
                 ("ind_v", 110, 136, 194, "30H"),
                 ("res_v", 220, 78, 194, "50"),
                 ("isrc_v", 266, 78, 194, "2/_90A", True),
                 ("wire", 180, 78, 286, 78), ("wire", 40, 194, 286, 194),
                 ("term", 286, 78, "a"), ("term", 286, 194, "b"),
                 ("gnd", 160, 194)],

    # 11.22--11.35: formas de onda. Somente geometria; nao ha componente.
    "p11_22": _wave([(48,176),(70,110),(92,92),(114,110),(136,176),
                       (158,110),(180,92),(202,110),(224,176)]),
    "p11_23": _wave([(48,176),(48,96),(102,96),(102,176),(190,176),
                       (190,96),(244,96),(244,176)], [("Vp",28,92),("T",184,184)]),
    "p11_24": _wave([(48,110),(96,110),(96,164),(144,164),(144,110),
                       (192,110),(192,164),(240,164),(240,110)]),
    "p11_25": _wave([(48,96),(88,96),(88,160),(128,160),(128,176),
                       (168,176),(168,96),(208,96),(208,160),(248,160)]),
    "p11_26": _wave([(48,144),(92,144),(92,96),(136,96),(136,144),
                       (180,144),(180,96),(224,96),(224,144),(270,144)]),
    "p11_27": _wave([(48,176),(96,96),(96,176),(144,96),(144,176),
                       (192,96),(192,176),(240,96),(240,176)]),
    "p11_28": _wave([(48,176),(88,96),(88,176),(148,176),(188,96),
                       (188,176),(248,176),(282,108)]),
    "p11_29": _wave([(48,136),(88,88),(128,136),(168,184),(208,136),
                       (248,88),(282,130)]),
    "p11_30": _wave([(48,176),(92,96),(92,158),(136,158),(136,176),
                       (180,96),(180,158),(224,158),(224,176),(270,96)]),
    "p11_31": _wave([(48,176),(92,96),(92,188),(136,188),(136,176),
                       (180,96),(180,188),(224,188),(224,176),(270,96)]),
    "p11_32": _wave([(48,176),(70,170),(92,150),(114,96),(114,176),
                       (158,176),(180,170),(202,150),(224,96),(224,176)]),
    "p11_33": _wave([(48,176),(74,96),(126,96),(152,176),(192,176),
                       (218,96),(270,96),(286,150)]),
    "p11_34": _wave([(48,176),(126,108),(166,108),(166,176),
                       (244,108),(282,108)]),
    "p11_35": _wave([(48,154),(82,154),(82,130),(116,130),(116,96),
                       (184,96),(184,130),(218,130),(218,154),(252,154),(252,176)]),

    "p11_44": _loop("100V", [("res_h", "30"), ("cap_h", "40uF"),
                                ("res_h", "20")],
                     [(2, "ind_v", "60mH")], right=("dvs_v", "4ix")) +
               [("arr_v", 184, 96, 148, "ix", False)],
    "p11_51": [("vsrc_v", 40, 78, 194, "16/_45V"),
                 ("res_h", 40, 78, 126, "2"),
                 ("wire", 126, 78, 278, 78), ("wire", 40, 194, 278, 194),
                 ("imp_v", 166, 78, 194, "10-j5"),
                 ("imp_v", 270, 78, 194, "8+j6"), ("gnd", 160, 194)],
    "p11_52": _power_bus("120/_45V", [(92,"2k","A"),
                                        (170,"3k","B"), (248,"1k","C")]),
    "p11_54": _loop("8/_-20V", [], [(0,"imp_v","4-j3")],
                     right=("ind_v", "5H")),
    "p11_55": _loop("10V", [("cap_h", "0.1F"), ("ind_h", "1H")],
                     [(1,"res_v","10")], right=("vsrc_v", "6V")),
    "p11_56": _bus("2/_30A", [("res_v","5"), ("imp_v","6+j4"),
                                 ("imp_v","6-j2")]),
    "p11_57": _loop("24V", [("res_h","4"), ("cap_h","1F"),
                              ("res_h","2")],
                     [(1,"res_v","1"), (2,"ind_v","2H")],
                     right=("dis_v","2Vo")) +
               [("vo", 96, 110, 174, "Vo")],
    "p11_58": [("vsrc_v", 36, 78, 194, "0.2V"),
                 ("res_h", 36, 78, 106, "500"), ("wire", 106, 78, 106, 194),
                 ("dis_v", 154, 78, 194, "20Io", False),
                 ("res_v", 224, 78, 194, "4k"),
                 ("cap_h", 154, 78, 224, "0.333mF"),
                 ("ind_h", 224, 78, 278, "1H"),
                 ("res_v", 278, 78, 194, "10k"),
                 ("wire", 36, 194, 278, 194), ("arr_h", 54, 58, 102, "Io", True),
                 ("gnd", 160, 194)],
    "p11_59": _loop("240V", [("res_h","50"), ("ind_h","30H")],
                     [(1,"cap_v","0.05F"), (1,"isrc_v","4A")],
                     right=("res_v","40")),
    "p11_60": _power_bus("6A", [(112,"20k","PF .8 atr"),
                                  (228,"16k","PF .9 atr")]),
    "p11_61": _power_bus("100/_90V", [(88,"2k","PF.707 ad"),
                                        (170,"1.2k","Q=-.8k"),
                                        (252,"4k","PF.9 atr")]),
    "p11_62": _loop("120V", [("res_h","0.2"), ("ind_h","40mH"),
                               ("res_h","0.3"), ("ind_h","150mH")],
                     [(2,"res_v","10"), (4,"res_v","15")]),
    "p11_63": _power_bus("220V", [(84,"12k","PF.866 ad"),
                                    (164,"16k","PF.85 atr"),
                                    (250,"20k","Q20k atr")]),
    "p11_64": _bus("120V", [("imp_v","8+j12"), ("isrc_v","2A")]),
    "p11_65": _opamp("4V", [("res_h","100k")], (),
                      ("res_v","50k"), True) + [("cap_v",184,112,196,"1nF")],
    "p11_66": _opamp("4/_45V", [("res_h","4k"), ("imp_h","j3000")],
                      [("res_h","2k"), ("imp_h","j4000")], None) +
               [("res_v",260,109,148,"6k"),
                ("cap_v",260,148,196,"0.5mF")],
    "p11_67": _opamp("0.6/_-70V", [("res_h","8"), ("ind_h","3H")],
                      [("res_h","10"), ("cap_h","0.1F")],
                      ("res_v","12")),
    "p11_68": _loop("1A", [("res_h","10"), ("ind_h","1H"),
                              ("cap_h","0.1F")]),
    "p11_74": _power_bus("120V", [(116,"24k","PF .8 atr"),
                                    (226,"40k","PF .95 atr")]),
    "p11_75": [("vsrc_v",40,78,194,"240V"),
                 ("wire",40,78,286,78), ("wire",40,194,286,194),
                 ("imp_v",80,78,194,"80-j50"),
                 ("imp_v",170,78,194,"120+j70"),
                 ("imp_v",270,78,194,"60"), ("gnd",160,194)],
    "p11_76": _loop("12V", [("res_h","4"), ("cap_h","0.333F")],
                     [(2,"ind_v","2H"), (2,"res_v","8")],
                     right=("isrc_v","3/_30A")) +
               [("lbl", "WM", 180, 54),
                ("arr_h", 216, 62, 270, "Iw", False),
                ("vo", 176, 112, 176, "Vw")],
    "p11_77": _loop("120V", [("res_h","6"), ("ind_h","4H")],
                     [(2,"cap_v","0.1F")], right=("res_v","15")) +
               [("lbl", "WM", 242, 54),
                ("arr_h", 176, 62, 232, "Iw", True),
                ("vo", 190, 112, 176, "Vw")],
    "p11_78": [("vsrc_v", 32, 100, 194, "20V"),
                 ("res_h", 32, 100, 96, "10"),
                 ("wire", 96, 100, 132, 100),
                 ("res_h", 132, 100, 188, "5"),
                 ("ind_h", 188, 100, 246, "1H"),
                 ("wire", 246, 100, 282, 100),
                 ("res_v", 246, 100, 194, "4"),
                 ("cap_v", 282, 100, 194, "83.333mF"),
                 ("wire", 32, 194, 282, 194),
                 ("lbl", "WM", 148, 58),
                 ("arr_h", 98, 76, 130, "Iw", True),
                 ("vo", 116, 122, 176, "Vw"),
                 ("gnd", 164, 194)],
    "p11_79": [("vsrc_v", 30, 100, 194, "10V"),
                 ("res_h", 30, 100, 100, "40"),
                 ("wire", 100, 100, 150, 100),
                 ("res_h", 150, 68, 240, "20"),
                 ("wire", 150, 100, 150, 68),
                 ("wire", 240, 68, 240, 100),
                 ("ind_h", 150, 100, 240, "10mH"),
                 ("dis_v", 130, 100, 194, "2Io", False),
                 ("cap_v", 270, 100, 194, "500uF"),
                 ("wire", 240, 100, 270, 100),
                 ("wire", 30, 194, 270, 194),
                 ("arr_h", 170, 48, 226, "Io", True),
                 ("arr_h", 106, 80, 144, "Iw", True),
                 ("lbl", "WM", 108, 116),
                 ("vo", 112, 132, 178, "Vw"),
                 ("gnd", 190, 194)],
    "p11_80": [("vsrc_v", 40, 90, 194, "110V"),
                 ("wire", 40, 90, 260, 90),
                 ("imp_v", 260, 90, 194, "6.4"),
                 ("wire", 40, 194, 260, 194),
                 ("lbl", "WM", 142, 112),
                 ("arr_h", 86, 68, 218, "Iw", True),
                 ("vo", 226, 112, 174, "Vw"),
                 ("lbl", "PF=.825", 238, 204),
                 ("gnd", 150, 194)],
    "p11_85": [("vsrc_v", 42, 78, 136, "120V"),
                 ("vsrc_v", 42, 136, 194, "120V"),
                 ("wire", 42, 78, 270, 78), ("wire", 42, 136, 166, 136),
                 ("wire", 42, 194, 270, 194),
                 ("res_v", 150, 78, 136, "10"),
                 ("wire", 166, 136, 200, 136),
                 ("res_v", 200, 136, 164, "10"),
                 ("ind_v", 200, 164, 194, "15mH"),
                 ("res_v", 270, 78, 194, "30"), ("gnd", 102, 136)],
    "p11_92": _power_bus("550V", [(86,"60k","M PF.75"),
                                    (168,"20k","C -20kVAR"),
                                    (252,"20k","Luz 20kW")]),
    "p11_95": _loop("4.6V", [("res_h","10"), ("cap_h","40nF"),
                               ("res_h","4"), ("ind_h","80mH")]),
    "p11_97": [("vsrc_v",40,78,194,"240V"),
                 ("res_h",40,78,100,"0.1"), ("ind_h",100,78,170,"1H"),
                 ("wire",170,78,270,78), ("res_v",270,78,136,"100"),
                 ("ind_v",270,136,194,"20H"), ("wire",170,194,270,194),
                 ("ind_h",100,194,170,"1H"), ("res_h",40,194,100,"0.1"),
                 ("gnd",160,194)],
}

CIRCUITS['p11_65']=[op for op in CIRCUITS['p11_65'] if op!=('wire',190,117,190,196)]
CIRCUITS['p11_65'] += [('wire',190,117,252,117),('wire',252,117,252,109)]
CIRCUITS['p11_97']=[('gnd',40,194) if op[0]=='gnd' else
    ('imp_h',op[1],op[2],op[3],'j1') if op[0]=='ind_h' else
    ('imp_v',op[1],op[2],op[3],'j20') if op[0]=='ind_v' else op
    for op in CIRCUITS['p11_97']]

CIRCUITS['p11_7']=[op for op in CIRCUITS['p11_7'] if op!=('wire',112,78,174,78)]
CIRCUITS['p11_7']=[('dis_v',174,78,194,'8Io',False) if op[0]=='isrc_v' else op for op in CIRCUITS['p11_7']]
CIRCUITS['p11_7']=[('dvs_v',112,78,194,'0.1Vo') if op[0]=='dvs_v' else op for op in CIRCUITS['p11_7']]
CIRCUITS['p11_9']=[('vsrc_v',30,93,149,'10/_30V'),('imp_v',74,149,206,'2k+j4k'),
    ('imp_h',158,190,286,'10k+j6k'),('imp_v',298,109,206,'20k-j12k'),
    ('opamp',158,80,True),('wire',30,93,158,93),('wire',74,149,158,149),
    ('wire',158,117,158,190),('wire',286,190,286,109),('wire',220,109,298,109),
    ('wire',30,149,30,206),('wire',30,206,298,206),('gnd',180,206)]
CIRCUITS['p11_10']=[('vsrc_v',18,108,206,'1V'),('res_h',174,124,230,'10'),
    ('res_h',230,80,292,'10'),('res_h',174,58,292,'10'),
    ('opamp',112,95,True),('opamp',230,111,False),
    ('wire',18,108,112,108),('wire',112,132,174,132),('wire',174,58,174,132),
    ('wire',230,80,230,124),('wire',292,58,292,140),
    ('wire',60,108,60,180),('wire',60,180,230,180),('wire',230,180,230,148),
    ('wire',18,206,292,206),('gnd',174,206)]
CIRCUITS['p11_12']=[op for op in CIRCUITS['p11_12'] if op not in
    [('wire',132,126,286,126),('term',286,126,'a')]]
CIRCUITS['p11_12'] += [('wire',132,126,132,164),('term',132,164,'a')]
CIRCUITS['p11_12'] += [('wire',238,78,238,126)]
CIRCUITS['p11_17'] += [('wire',80,136,110,136)]
CIRCUITS['p11_14']=[('isrc_v',40,78,194,'2A',True),('ind_v',92,78,194,'1H'),
    ('res_v',150,78,194,'10'),('cap_h',170,78,225,'0.1F'),('res_h',225,78,286,'20'),
    ('imp_v',286,78,194,'10'),('wire',40,78,170,78),('wire',40,194,286,194),('gnd',190,194)]
CIRCUITS['p11_19']=[('isrc_v',166,78,194,'33A',True),('res_h',48,78,118,'3'),
    ('imp_v',48,78,194,'j1'),('res_v',224,78,194,'6'),('imp_h',238,78,286,'-j2'),
    ('res_v',286,78,194,'10'),('wire',118,78,238,78),('wire',48,194,286,194),('gnd',150,194)]

# Rated loads are powers, not resistors measured in ohms. Keep the source
# editable and carry each P/Q/PF rating in the scalar bank instead.
for _n in (52,60,61,63,74,92):
    _id='p11_%d'%_n
    CIRCUITS[_id]=[op for op in CIRCUITS[_id] if op[0] not in ('res_v','lbl')]
    CIRCUITS[_id] += [('lbl','Cargas: P, Q e FP em Dados atuais',14,214)]
    if _n==60:CIRCUITS[_id]=[('isrc_v',36,78,194,'6A',True) if op[0]=='vsrc_v' else op for op in CIRCUITS[_id]]
CIRCUITS['p11_64']=[op for op in CIRCUITS['p11_64'] if op[0]!='isrc_v']
CIRCUITS['p11_64'] += [('lbl','Is e calculada, nao e um dado',14,214)]
CIRCUITS['p11_62']=[('res_h',38,78,98,'0.2'),('imp_h',98,78,158,'j0.04'),
    ('res_h',158,78,218,'0.3'),('imp_h',218,78,278,'j0.15'),
    ('term',38,78,'Vs'),('term',278,78,'Vfim'),('wire',38,194,278,194),('gnd',160,194),
    ('lbl','Cargas P1/FP1 e P2/FP2 nos dados',14,214)]
CIRCUITS['p11_54']=[('vsrc_v',40,78,194,'8/_-20V'),('res_v',140,78,136,'4'),
    ('cap_v',140,136,194,'0.333333F'),('ind_v',270,78,194,'5H'),
    ('wire',40,78,270,78),('wire',40,194,270,194),('gnd',200,194)]
CIRCUITS['p11_56']=_loop('2/_30A',[('imp_h','3+j4')],[(0,'res_v','5'),(1,'imp_v','-j2')],right=('res_v','6'))
CIRCUITS['p11_58']=[('cap_h',*op[1:4],'0.333333uF') if op[0]=='cap_h' else op for op in CIRCUITS['p11_58']]
CIRCUITS['p11_67']=_opamp('0.6/_-70V',[('res_h','8'),('ind_h','3H')],[('res_h','10')],('res_v','12'))
CIRCUITS['p11_67'] += [('cap_h',190,36,252,'0.1F'),('wire',190,36,190,58),('wire',252,36,252,58)]
# The given load is |Z|=6.4 with FP=.825 lagging, not a 6.4-ohm resistor.
CIRCUITS['p11_80']=[('imp_v',260,90,194,'5.28+j3.616905') if op[0]=='imp_v' else op for op in CIRCUITS['p11_80']]


STATEMENTS = {
    2: ["Determine a potencia media fornecida ou", "absorvida por cada elemento."],
    3: ["R=60 ohm em paralelo com C=90uF,", "v=160cos(2000t). Ache P medio."],
    4: ["Formule e resolva um exemplo sobre", "potencias instantanea e media."],
    5: ["Para vs=8cos(2t-40deg), determine", "a potencia media de cada elemento."],
    6: ["Com is=6cos(1000t) A, determine", "a potencia no resistor de 50 ohm."],
    7: ["Determine a potencia media absorvida", "pelo resistor de 10 ohm."],
    9: ["Com Vs=10/_30 V, determine a potencia", "media no resistor de 20 kohm."],
    10: ["No circuito com AOPs, determine a", "potencia media em cada resistor R."],
    11: ["Com R=10k, C=200nF e corrente dada,", "determine a potencia media da porta."],
    12: ["Ache ZL para maxima potencia e calcule", "a potencia maxima absorvida."],
    13: ["Zth=120+j60 ohm e Vth,pico=165 V.", "Determine a potencia maxima disponivel."],
    14: ["Formule um exemplo sobre maxima", "transferencia de potencia media."],
    16: ["Determine Pmax da carga e a potencia", "entregue ao ZL indicado."],
    17: ["Ache ZL para maxima potencia e calcule", "a potencia media maxima."],
    18: ["Determine ZL para maxima transferencia", "de potencia media."],
    19: ["Ajuste o resistor R para potencia maxima", "e determine R e Pmax."],
    20: ["Ajuste RL para potencia maxima e", "determine RL e Pmax."],
    21: ["Sendo a carga puramente resistiva,", "determine RL para potencia maxima."],
    22: ["Determine o valor RMS da senoide", "deslocada mostrada na figura."],
    23: ["Formule um exemplo de calculo RMS", "usando a onda pulsada da figura."],
    24: ["Determine o valor RMS da onda", "quadrada de +5 V e -5 V."],
    25: ["Determine o valor RMS do sinal", "periodico mostrado na figura."],
    26: ["Determine o valor RMS da tensao", "retangular entre 10 V e 20 V."],
    27: ["Calcule o valor RMS da corrente", "dente de serra de pico 5 A."],
    28: ["Ache Vrms da onda e a potencia media", "em um resistor de 2 ohm."],
    29: ["Ache Irms da onda triangular e a", "potencia em um resistor de 12 ohm."],
    30: ["Calcule o valor RMS da forma de onda", "rampa de 2 V e patamar de -1 V."],
    31: ["Determine o valor RMS da rampa de 2 V", "seguida pelo patamar de -4 V."],
    32: ["Determine Irms para i=10t^2 em 0<t<1", "e zero em 1<t<2."],
    33: ["Determine Irms da onda trapezoidal", "de pico 5 A e periodo 6 s."],
    34: ["Determine o valor eficaz da rampa ate", "6 seguida por um patamar."],
    35: ["Determine Vrms da onda em degraus", "10, 20, 30, 20 e 10 V."],
    36: ["Calcule o RMS das quatro funcoes", "DC+senoides dadas no enunciado."],
    37: ["Formule um exemplo de RMS da soma", "de correntes de frequencias distintas."],
    39: ["Motor Z=4.2+j3.6 em 220 V, 60 Hz:", "ache FP, P, Q e C para FP=1."],
    40: ["Formule um exemplo sobre potencia", "aparente e fator de potencia."],
    42: ["Fonte 110 V, S=120 VA, FP=.707 atr.", "Ache S, I, Z e os valores R e L."],
    43: ["Formule um exemplo que explique", "potencia complexa."],
    44: ["Para vs=100cos(2000t), determine a", "potencia complexa liberada pela fonte."],
    45: ["v=20+60cos100t e i=1-.5sen100t.", "Ache Vrms, Irms e potencia media."],
    46: ["Para os quatro pares de fasores, ache", "S, |S|, P, Q e o tipo de FP."],
    47: ["Determine S, P e Q nos quatro casos", "senoidais e fasoriais."],
    48: ["Determine a potencia complexa nos", "quatro casos especificados."],
    49: ["Determine a potencia complexa nos", "quatro casos especificados."],
    50: ["Obtenha a impedancia total nos tres", "casos de potencia fornecidos."],
    51: ["Calcule FP, P, Q, |S| e S para todo", "o circuito da figura."],
    52: ["Some as cargas A, B e C; ache o FP", "total e a corrente da fonte."],
    54: ["Determine a potencia complexa absorvida", "por cada elemento do circuito."],
    55: ["Formule um exemplo de conservacao", "de potencia complexa em CA."],
    56: ["Obtenha a potencia complexa liberada", "pela fonte de corrente."],
    57: ["Ache P, Q e S liberados pela fonte", "de corrente dependente."],
    58: ["Determine a potencia complexa entregue", "ao resistor de 10 kohm."],
    59: ["Calcule a potencia reativa no indutor", "e no capacitor."],
    60: ["Com a fonte de 6 A e duas cargas,", "determine Vo e o FP de entrada."],
    61: ["Determine Io e a potencia complexa", "total fornecida."],
    62: ["Com 120 V na carga, determine a tensao", "Vs considerando as impedancias da linha."],
    63: ["Determine Io para as tres cargas em", "paralelo alimentadas em 220 V."],
    64: ["Ache Is quando a fonte de 120 V fornece", "2.5 kW e 0.4 kVAR adiantado."],
    65: ["Para vs=4cos(10^4t), determine a", "potencia media no resistor de 50k."],
    66: ["Determine a potencia media absorvida", "pelo resistor de 6 kohm."],
    67: ["Ache S liberada pela fonte e a potencia", "media no resistor de 12 ohm."],
    68: ["Obtenha a potencia complexa fornecida", "pela fonte no RLC serie."],
    70: ["Formule um exemplo sobre correcao", "do fator de potencia."],
    71: ["Some as tres cargas; determine Zeq,", "FP total e corrente da fonte."],
    72: ["Ache o FP da segunda carga e o elemento", "para corrigir o FP total para .9."],
    73: ["Para P=10kW e Q resultante, ache S, I", "e a correcao do FP para .96."],
    74: ["Ache o FP das duas cargas e C em", "paralelo para obter FP unitario."],
    75: ["Para as tres impedancias em paralelo,", "ache S total e fator de potencia."],
    76: ["Determine a leitura do wattimetro no", "circuito da Figura 11.91."],
    77: ["Determine a leitura do wattimetro no", "circuito da Figura 11.92."],
    78: ["Determine a leitura do wattimetro no", "circuito da Figura 11.93."],
    79: ["Determine a leitura do wattimetro no", "circuito da Figura 11.94."],
    80: ["Ache a corrente da carga e a leitura", "do wattimetro para ZL=6.4, FP=.825."],
    81: ["Formule um exemplo de correcao de", "fator de potencia nao unitario."],
    82: ["Aquecedor de 5kW e motor de 30kVA:", "ache S, Q e C para FP=.9."],
    83: ["Com Vp=210/_60 e Ip=8/_25, ache", "P, |S|, Q e fator de potencia."],
    84: ["Calcule o custo anual e a tarifa unica", "equivalente para o consumidor."],
    85: ["No sistema residencial trifilar, ache", "I1, I2, In, S total e FP."],
    86: ["Carga 75 ohm + 4uH em 4.12MHz:", "determine a impedancia interna."],
    87: ["Com |Z|=3k, I=50mA e VR=80V,", "determine o fator de potencia."],
    88: ["Linha de 110 V fornece 2 A com fase", "55deg. Ache P e potencia aparente."],
    89: ["Aquecedor 210V, 12kVA, FP=.78 atr:", "ache S complexa e a impedancia."],
    90: ["Dimensione o banco de capacitores para", "nao sobrecarregar o turbogerador."],
    91: ["Motor 220V, 15A, 60Hz e 2700W:", "ache FP e C para FP unitario."],
    92: ["Planta de 550V: motor 60kW FP=.75,", "cap 20kVAR e luz 20kW. Ache totais."],
    93: ["Some motor, aquecedor, lampadas e motor", "sincrono; ache P, Q e FP geral."],
    94: ["Subestacao 1MVA, FP .7 para .95:", "avalie capacitor, capacidade e custo."],
    95: ["Ache a frequencia de maxima potencia", "e P no alto-falante para Vs=4.6V."],
    96: ["Fonte Vth=146V e Zth=40-j8 ohm:", "ache ZL otimo e a potencia maxima."],
    97: ["Para Vs=240/_0 V, determine a potencia", "media absorvida pela carga."],
}


RESULTS = {
    2: "P5=9.412 W; QL=1.882; QC=-12.235 VAR.",
    3: "P=Vrms^2/R=213.3 W; PC=0.",
    5: "P1=1.416 W; P2=5.097 W; PL=PC=0.",
    6: "ix=.783+j2.219 A; P50=276.9 W.",
    7: "P10=160 W.", 9: "P20k=22.42 mW.",
    10: "P nos tres resistores = 0 W.",
    11: "P=3.472 W.",
    12: "ZL=0.823+j0.864 ohm; Pmax=8.460 kW.",
    13: "ZL=120-j60 ohm; Pmax=28.36 W.",
    16: "ZL=1.670-j3.648 ohm; Pmax=10.57 W.",
    17: "ZL=20-j10 ohm; Pmax=31.25 W.",
    18: "ZL=21.23-j20.15 ohm.",
    19: "R=|Zth|; Pmax=258.5 W.",
    20: "RL=6.793 ohm; Pmax=43.03 W.",
    21: "RL=|Zth|=19.58 ohm.",
    22: "Irms=4/sqrt(2)=2.828 A.",
    23: "Vrms=Vp/sqrt(3).",
    24: "Vrms=5 V.", 25: "Vrms=3.266.",
    26: "Vrms=sqrt((10^2+20^2)/2)=15.81 V.",
    27: "Irms=5/sqrt(3)=2.887 A.",
    28: "Vrms=2.921 V; P=4.267 W.",
    29: "Irms=17.321 A; P=3.600 kW.",
    30: "Vrms=sqrt(7/6)=1.080 V.",
    31: "Vrms=sqrt(26/3)=2.944 V.",
    32: "Irms=sqrt(10)=3.162 A.",
    33: "Irms=3.333 A.", 34: "Frms=sqrt(20)=4.472.",
    35: "Vrms=sqrt(1400/3)=21.60 V.",
    36: "RMS: 10 A; 4.528 V; 9.055 A; 4.528 V.",
    39: "FP=.7592; P=6.643kW; Q=5.695kVAR; C=312uF.",
    42: "S=84.84+j84.84 VA; I=1.091/_-45 A.",
    44: "Sforn=96.87-j19.28 VA.",
    45: "Vrms=46.90V; Irms=1.061A; P=20W.",
    46: "S: 110/_-30; 1550/_15; 288/_15; 1360/_-45 VA.",
    47: "S:112+j194; 226-j226; 111+j64; 7.07+j7.07kVA.",
    48: "S:269-j150; 4.129-j2k; 396.9+j450; 1k+j680 VA.",
    49: "S:4+j2.375; 1.6-j1.2; .463+j1.270 kVA; 111-j166VA.",
    50: "Z:30.98-j23.23; 10.42+j13.89; 1.6+j2.77 ohm.",
    51: "St=31.12+j2.936 VA; FP=.9956 atrasado.",
    52: "St=4.2-j.749kVA; FP=.9845 ad; I=35.55/_55.1A.",
    54: "S4-j3=10.24-j7.68; Sj5=j12.8 VA.",
    56: "V=3.585+j2.356 V; Sfonte=8.566+j.496 VA.",
    57: "Sdep=50.45-j33.64 VA.",
    58: "S10k=51.2 mW+j0 VAR.",
    59: "QL=339.2 VAR; QC=-1.413 kVAR.",
    60: "Vo=6+j3.791 kV; FP=.845 atrasado.",
    61: "St=6.614-j.277 kVA; Io=66.2/_92.4 A.",
    62: "Vs=120.060/_0.039 deg V.",
    63: "St=43+j22.99 kVA; Io=221.6/_-28.1 A.",
    64: "Is=-16.218-j10.256 A=19.19/_-147.69 A.",
    65: "Vo,rms=2 V; P50k=80 uW.",
    66: "|Vo|=3.578 V RMS; P6k=1.920 mW.",
    67: "Sfonte=14.4+j10.8 mVA; P12=3 mW.",
    68: "S=Irms^2[R+j(wL-1/wC)].",
    71: "St=286.8+j10kVA; FP=.9994 atr; I=2391/_-2deg A.",
    72: "FP2=.9487 atr; C=117.5 uF.",
    73: "|S|=12.21kVA; I=50.86A; C=188uF.",
    74: "FP=.899; C=5.739 mF para FP=1.",
    75: "St=1.8359-j.1147kVA; FP=.9981 ad.",
    76: "W=-18.95 W com as polaridades marcadas.",
    77: "W=157.69 W.", 79: "W=50 mW.",
    78: "W=4.690 W.",
    80: "I=17.19 A; W=1.560 kW.",
    82: "St=29.6+j17.17kVA; C=130.6uF para FP=.9.",
    83: "P=688.1W; |S|=840VA; Q=481.8VAR; FP=.819.",
    84: "Custo=US$120000/ano; tarifa=US$0.10/kWh.",
    85: "P=4.451kW; Q=.617kVAR; FP=.9905 atrasado.",
    86: "Zinterna=75-j103.55 ohm.", 87: "FP=0.5333.",
    88: "P=126.2 W; |S|=220 VA.",
    89: "S=9.36+j7.51kVA; Z=2.866+j2.300 ohm.",
    90: "Banco necessario: aproximadamente 968 kVAR.",
    91: "FP=.8182 atrasado; C=1.398 mF.",
    92: "St=80+j32.92kVA; FP=.9247; I=157.3A.",
    93: "St=7.329+j1.196kVA; FP=.9869 atrasado.",
    94: "Qc=484.1kVAR; economia liquida aprox. US$17.1 mil.",
    95: "f=2.814 kHz; P=431.8 mW.",
    96: "ZL=40+j8 ohm; Pmax=133.2 W.",
    97: "I=2.339 A; Pcarga=547.3 W.",
}


PROJECTS = {4, 14, 23, 37, 40, 43, 55, 70, 81}
RMS_SET = set(range(22, 38))
COMPLEX_SET = set(range(42, 69))
PF_SET = set(range(71, 76)) | set(range(82, 95))
WATTMETER_SET = set(range(76, 81))
MAX_SET = set(range(12, 22))
DIAGRAM_ONLY = RMS_SET
VISUAL_ONLY = ({4, 5, 6, 7, 9, 10, 14, 16, 17, 18, 19, 20, 21,
                44, 51, 52, 54, 55, 57, 58, 59, 60, 61, 62, 63, 64,
                65, 66, 67, 68, 74, 75, 76, 77, 78, 79, 80, 85, 92, 95}
               | DIAGRAM_ONLY)

OMEGA = {
    2: 1.0, 4: 1.0, 5: 2.0, 6: 1000.0, 7: 1.0, 9: 1.0,
    10: 1.0, 12: 1.0, 14: 1.0, 16: 4.0, 17: 1.0, 18: 1.0,
    19: 1.0, 20: 1.0, 21: 1.0, 44: 2000.0, 51: 1.0,
    54: 1.0, 55: 1.0, 56: 1.0, 57: 1.0, 58: 1000.0,
    59: 1.0, 60: 1.0, 61: 1.0, 62: 1.0, 63: 1.0, 64: 1.0,
    65: 10000.0, 66: 1.0, 67: 2.0, 68: 1.0, 74: 377.0,
    75: 1.0, 76: 1.0, 77: 2.0, 78: 4.0, 79: 100.0,
    80: 1.0, 85: 377.0, 92: 377.0, 95: 17677.7, 97: 1.0,
}

# Dados dos problemas sem componente eletrico registrado.  Formas de onda
# usam parametros de nivel/periodo; problemas de potencia usam P, Q, S, FP e
# fasores separados.  Projetos abertos recebem os valores do exemplo que a
# propria resolucao apresenta, para que MODE nunca abra um exercicio numerico
# somente para leitura.
PARAMS = {
    3: [("R_ohm", 60.0), ("C_F", 0.00009),
        ("Vpk_V", 160.0), ("w_rad_s", 2000.0)],
    11: [("R_ohm", 10000.0), ("C_F", 0.0000002),
         ("Ipk_A", 0.033), ("w_rad_s", 377.0), ("I_deg", 22.0)],
    13: [("Zth_R", 120.0), ("Zth_X", 60.0), ("Vth_pk_V", 165.0)],
    22: [("Ipk_A", 4.0), ("dc_A", 0.0)],
    23: [("Vp_V", 4.0), ("duty", 0.333333), ("T_s", 1.0)],
    24: [("Vhi_V", 5.0), ("Vlo_V", -5.0), ("duty", 0.5)],
    25: [("Fhi", 4.0), ("Flo", -4.0), ("T_s", 5.0)],
    26: [("V1_V", 10.0), ("V2_V", 20.0), ("duty", 0.5)],
    27: [("Ipk_A", 5.0), ("T_s", 1.0)],
    28: [("Vpk_V", 4.0), ("R_ohm", 2.0), ("T_s", 4.0)],
    29: [("Ipk_A", 30.0), ("R_ohm", 12.0), ("T_s", 4.0)],
    30: [("Vramp_V", 2.0), ("Vlow_V", -1.0), ("T_s", 2.0)],
    31: [("Vramp_V", 2.0), ("Vlow_V", -4.0), ("T_s", 2.0)],
    32: [("K_A_s2", 10.0), ("t1_s", 1.0), ("T_s", 2.0)],
    33: [("Ipk_A", 5.0), ("T_s", 6.0)],
    34: [("Fpk", 6.0), ("T_s", 2.0)],
    35: [("V1_V", 10.0), ("V2_V", 20.0), ("V3_V", 30.0),
         ("T_s", 5.0)],
    36: [("Ia_dc_A", 10.0), ("Vb_dc_V", 4.0), ("Vb_ac_V", 3.0),
         ("wb", 5.0), ("Ic_dc_A", 8.0), ("Ic_ac_A", 6.0),
         ("wc", 2.0), ("Vd_sin_V", 5.0), ("Vd_cos_V", 4.0)],
    37: [("I1_A", 3.0), ("f1_Hz", 60.0),
         ("I2_A", 4.0), ("f2_Hz", 180.0)],
    39: [("Z_R", 4.2), ("Z_X", 3.6), ("V_V", 220.0),
         ("f_Hz", 60.0), ("FPnovo", 1.0)],
    40: [("V_V", 120.0), ("I_A", 10.0), ("phi_deg", 30.0)],
    42: [("V_V", 110.0), ("S_VA", 120.0),
         ("FP", 0.707), ("f_Hz", 60.0)],
    43: [("V_V", 120.0), ("V_deg", 0.0),
         ("I_A", 5.0), ("I_deg", -30.0)],
    45: [("Vdc_V", 20.0), ("Vac_pk_V", 60.0), ("w_rad_s", 100.0),
         ("Idc_A", 1.0), ("Iac_pk_A", -0.5)],
    46: [("Va_V", 220.0), ("Va_deg", 30.0),
         ("Ia_A", 0.5), ("Ia_deg", 60.0),
         ("Vb_V", 250.0), ("Vb_deg", -10.0),
         ("Ib_A", 6.2), ("Ib_deg", 25.0),
         ("Vc_V", 120.0), ("Vc_deg", 0.0),
         ("Ic_A", 2.4), ("Ic_deg", 15.0),
         ("Vd_V", 160.0), ("Vd_deg", 45.0),
         ("Id_A", 8.5), ("Id_deg", 90.0)],
    47: [("Va_pk_V", 112.0), ("Va_deg", 10.0),
         ("Ia_pk_A", 4.0), ("Ia_deg", -50.0),
         ("Vb_pk_V", 160.0), ("Vb_deg", 0.0),
         ("Ib_pk_A", 4.0), ("Ib_deg", 45.0),
         ("Vc_V", 80.0), ("Vc_deg", 60.0),
         ("Zc_mag", 50.0), ("Zc_deg", 30.0),
         ("Id_A", 10.0), ("Id_deg", 60.0),
         ("Zd_mag", 100.0), ("Zd_deg", 45.0)],
    48: [("Pa_W", 269.0), ("Qa_VAR", -150.0),
         ("Qb_VAR", -2000.0), ("FPb", 0.9),
         ("Sc_VA", 600.0), ("Qc_VAR", 450.0),
         ("Vd_V", 220.0), ("Pd_W", 1000.0), ("Zd_deg", 40.0)],
    49: [("Pa_W", 4000.0), ("FPa", 0.86),
         ("Sb_VA", 2000.0), ("Pb_W", 1600.0),
         ("Vc_V", 208.0), ("Vc_deg", 20.0),
         ("Ic_A", 6.5), ("Ic_deg", -50.0),
         ("Vd_V", 120.0), ("Vd_deg", 30.0),
         ("Zd_R", 40.0), ("Zd_X", -60.0)],
    50: [("Pa_W", 1000.0), ("FPa", 0.8), ("Va_V", 220.0),
         ("Pb_W", 1500.0), ("Qb_VAR", 2000.0), ("Ib_A", 12.0),
         ("Sc_VA", 4500.0), ("Sc_deg", 60.0),
         ("Vc_V", 120.0), ("Vc_deg", 45.0)],
    70: [("P_W", 10000.0), ("Q_VAR", 7500.0),
         ("V_V", 240.0), ("f_Hz", 60.0), ("FPnovo", 0.95)],
    71: [("V_V", 120.0), ("Q1_VAR", 60000.0), ("FP1", 0.85),
         ("P2_W", 90000.0), ("Q2_VAR", -50000.0),
         ("P3_W", 100000.0), ("FP3", 1.0)],
    72: [("Ptot_W", 2400.0), ("FPtot", 0.8), ("V_V", 120.0),
         ("f_Hz", 60.0), ("P1_W", 1500.0),
         ("FP1", 0.707), ("FPnovo", 0.9)],
    73: [("V_V", 240.0), ("f_Hz", 60.0), ("P_W", 10000.0),
         ("Qcap_VAR", -15000.0), ("Qind_VAR", 22000.0),
         ("FPnovo", 0.96)],
    81: [("P_W", 10000.0), ("Q_VAR", 7500.0),
         ("V_V", 240.0), ("f_Hz", 60.0), ("FPnovo", 0.9)],
    82: [("V_V", 240.0), ("f_Hz", 60.0), ("Pheat_W", 5000.0),
         ("Smotor_VA", 30000.0), ("FPmotor", 0.82), ("FPnovo", 0.9)],
    83: [("V_V", 210.0), ("V_deg", 60.0),
         ("I_A", 8.0), ("I_deg", 25.0)],
    84: [("Energia_kWh", 1200000.0), ("Demanda_VA", 2400000.0),
         ("tar_kWh", 0.04), ("dem_USDkVA", 30.0)],
    86: [("R_ohm", 75.0), ("L_H", 0.000004), ("f_Hz", 4120000.0)],
    87: [("Zmag_ohm", 3000.0), ("I_A", 0.05), ("VR_V", 80.0)],
    88: [("V_V", 110.0), ("I_A", 2.0), ("phi_deg", 55.0)],
    89: [("V_V", 210.0), ("f_Hz", 60.0),
         ("S_VA", 12000.0), ("FP", 0.78)],
    90: [("Pload_W", 800000.0), ("Qload_VAR", 1568000.0),
         ("Smax_VA", 1000000.0)],
    91: [("V_V", 220.0), ("I_A", 15.0), ("f_Hz", 60.0),
         ("P_W", 2700.0), ("FPnovo", 1.0)],
    93: [("P1_W", 3000.0), ("Q1_VAR", 2000.0),
         ("P2_W", 2000.0), ("Q2_VAR", 0.0),
         ("P3_W", 1000.0), ("Q3_VAR", 0.0),
         ("P4_W", 1329.0), ("Q4_VAR", -804.0), ("V_V", 240.0)],
    94: [("S_VA", 1000000.0), ("FPold", 0.7), ("FPnovo", 0.95)],
    96: [("Vth_V", 146.0), ("Zth_R", 40.0), ("Zth_X", -8.0)],
}


def _solution(number):
    special = {
        6: ["1) w=1000; ZC=-j25 e ZL=j20.",
            "2) ix=Va/(50-j25).",
            "3) Superno: ix+Vb/(10+j20)=Is.",
            "4) Va-Vb=20ix; Is=6/sqrt(2).",
            "5) P50=|ix|^2 vezes 50."],
        10: ["1) AOP ideal: V+=V- e Ient=0.",
             "2) O primeiro seguidor fixa V1=V.",
             "3) No segundo, V-=V+=V.",
             "4) A KCL em V- resulta Vo=V.",
             "5) Assim, a queda em cada R e zero."],
        16: ["1) Use RMS: Vs=10/sqrt(2) V; w=4.",
             "2) Com ZL aberto, ache Vth.",
             "3) Vth=8.405/_56.31 V.",
             "4) Fonte anulada e teste dao Zth.",
             "5) ZL=conj(Zth); Pmax=|Vth|^2/(4Rth)."],
        18: ["1) Anule 60V (curto) e 5A (aberto).",
             "2) ZRN=80||(-j10).",
             "3) ZNB=(40||40)+j30.",
             "4) Zth=ZRN+ZNB; ZL=conj(Zth)."],
        20: ["1) Abra RL e resolva o superno A-B.",
             "2) Vth=-1.101-j25.953 V.",
             "3) Com Vs=0 e teste, ache Zth.",
             "4) Para RL real, RL=|Zth|.",
             "5) P=|Vth|^2 RL/|Zth+RL|^2."],
        44: ["1) Vs=100/sqrt(2) V; w=2000.",
             "2) ZC=-j12.5; ZL=j120.",
             "3) Vb=4ix; ix=Va/(j120).",
             "4) Is=(Vs-Va)/(30-j12.5).",
             "5) Sforn=Vs vezes conjugado(Is)."],
        57: ["1) Defina Vo=Va e Idep=2Va.",
             "2) Aplique KCL nos nos A, B e C.",
             "3) Vc=-8.759+j11.912 V.",
             "4) Sdep=Vc vezes conjugado(2Va)."],
        58: ["1) Io=0.2/500=0.4 mA.",
             "2) Idep=20Io=8 mA.",
             "3) Zramo=10k-j2k; resolva Va.",
             "4) I10k=Va/Zramo; S=|I10k|^2 10k."],
        64: ["1) IZ=120/(8+j12).",
             "2) Sv=2.5k-j0.4k VA (adiantado).",
             "3) Iv=conjugado(Sv/120).",
             "4) Pela KCL, Is=IZ-Iv."],
        76: ["1) Zs=4-j3; Yp=1/8+1/(j2).",
             "2) Va=(12/Zs+Is)/(1/Zs+Yp).",
             "3) Va=.755+j11.323; Ic=-3/_30 A.",
             "4) W=Re[Va vezes conjugado(Ic)]."],
        78: ["1) Vs=20/sqrt(2) V; w=4.",
             "2) Zp=4||(-j3)=1.44-j1.92.",
             "3) Zd=5+j4+Zp=6.44+j2.08.",
             "4) I=Vs/(10+Zd); Vw=I Zd.",
             "5) W=Re[Vw vezes conjugado(I)]."],
        84: ["1) Energia=1200MWh=1.2M kWh.",
             "2) Parcela energia=1.2M vezes US$0.04.",
             "3) Demanda=2400kVA vezes US$30/ano.",
             "4) Tarifa unica=custo total/energia."],
        86: ["1) Zant=75+jw(4uH).",
             "2) w=2pi(4.12MHz).",
             "3) Para Pmax: Zinterna=conj(Zant)."],
        87: ["1) R=VR/I=80/0.05=1.6 kohm.",
             "2) FP=R/|Z|=1.6/3."],
        88: ["1) |S|=Vrms Irms=110 vezes 2.",
             "2) P=|S|cos55deg."],
        95: ["1) Rtotal=10+4=14 ohm.",
             "2) Ressonancia: wL=1/(wC).",
             "3) f=1/[2pi sqrt(LC)].",
             "4) P4ohm=(Vs/Rtotal)^2 vezes 4."],
        96: ["1) Para Pmax: ZL=conj(Zth).",
             "2) Logo ZL=40+j8 ohm.",
             "3) Pmax=|Vth|^2/(4Rth)."],
    }
    if number in special:
        lines = special[number]
    elif number in RMS_SET:
        lines = ["1) Identifique um periodo T.",
                 "2) Integre x(t)^2 em cada trecho.",
                 "3) Xrms=sqrt[(1/T) integral x^2 dt]."]
    elif number in MAX_SET:
        lines = ["1) Remova a carga e calcule Vth.",
                 "2) Anule fontes e determine Zth.",
                 "3) Para Z complexo: ZL=conj(Zth).",
                 "4) Pmax=|Vth,rms|^2/(4 Rth)."]
    elif number in WATTMETER_SET:
        lines = ["1) Resolva a rede em fasores RMS.",
                 "2) Ache I na bobina de corrente.",
                 "3) Ache V na bobina de potencial.",
                 "4) Leitura=Re[V vezes conjugado(I)]."]
    elif number in PF_SET or number in {40, 70, 81}:
        lines = ["1) Converta cada carga em P+jQ.",
                 "2) Some St=Pt+jQt.",
                 "3) FP=Pt/|St|; I=conj(St/V).",
                 "4) Qc=Pt tan(phi alvo)-Qt."]
    elif number in COMPLEX_SET:
        lines = ["1) Use valores RMS e fasores.",
                 "2) S=V vezes conjugado(I)=P+jQ.",
                 "3) Em Z: S=|V|^2/conjugado(Z).",
                 "4) Verifique soma Sforn=soma Sabs."]
    elif number in PROJECTS:
        lines = ["1) Escolha dados coerentes para a rede.",
                 "2) Calcule fasores ou valores RMS.",
                 "3) Use S=V vezes conjugado(I).",
                 "= Confira que soma(Sforn)=soma(Sabs)."]
    else:
        lines = ["1) Converta os sinais para fasores RMS.",
                 "2) Resolva tensoes e correntes da rede.",
                 "3) P=Re[V vezes conjugado(I)].",
                 "4) Reativos ideais tem potencia media zero."]
    if number in RESULTS:
        lines.append("= " + RESULTS[number])
    else:
        lines.append("= Substitua os dados nas expressoes acima.")
    if number in PARAMS or (number in VISUAL_ONLY and number not in DIAGRAM_ONLY):
        lines.append("# Edicao: use Dados atuais e repita as equacoes.")
    return lines


def _last_component_index(ops):
    kinds = {"res_h", "res_v", "cap_h", "cap_v", "ind_h", "ind_v",
             "imp_h", "imp_v", "vsrc_h", "vsrc_v", "isrc_h", "isrc_v",
             "dvs_h", "dvs_v", "dis_v"}
    found = [i for i, op in enumerate(ops) if op[0] in kinds]
    return found[-1] if found else None


SKIP = {1, 8, 15, 38, 41, 53, 69}
TARGET_OP = {56: 0, 97: 4}
DEP_RESOLVE = {
    6: {5: {"kind": "current", "branch_op_index": 3}},
    7: {2: {"kind":"voltage","node_op_index":7},
        3: {"kind":"current","branch_op_index":1}},
    16: {8: {"kind": "voltage", "node_op_index": 4}},
    20: {5: {"kind": "current", "branch_op_index": 1}},
    44: {5: {"kind": "current", "branch_op_index": 1}},
    57: {6: {"kind": "voltage", "node_op_index": 1}},
    58: {3: {"kind": "current", "branch_op_index": 1}},
    79: {7: {"kind": "current", "branch_op_index": 3}},
}
EXERCISES = []
for number in range(1, 98):
    if number in SKIP:
        continue
    ex_id = "p11_%d" % number
    exercise = {
        "id": ex_id,
        "title": "Problema 11.%d" % number,
        "subject": "Max Potencia AC" if number in MAX_SET else "Potencia AC",
        "priority": 100 + number,
        "source": "Livro, Cap.11, Problema 11.%d" % number,
        "statement": STATEMENTS[number],
        "static": True,
        "solution": _solution(number),
    }
    if number in PARAMS:
        exercise["params"] = PARAMS[number]
    if ex_id in CIRCUITS:
        engine = {"omega": OMEGA.get(number, 1.0)}
        if number in (44,65,67,68,77,78,79):engine['peak']=True
        if number in DIAGRAM_ONLY:
            engine["diagram_only"] = True
            engine["visual_only"] = True
        elif number in VISUAL_ONLY:
            engine["visual_only"] = True
        elif number in MAX_SET:
            engine["port_labels"] = ["a", "b"]
        else:
            target = TARGET_OP.get(number, _last_component_index(CIRCUITS[ex_id]))
            if target is not None:
                engine["target_op_index"] = target
        if number in DEP_RESOLVE:
            engine["dep_resolve"] = DEP_RESOLVE[number]
        exercise["engine"] = engine
    elif number in PARAMS:
        exercise["engine"] = {"visual_only": True}
    EXERCISES.append(exercise)
