"""Capitulo 10 completo (problemas 10.1--10.96).

Os problemas prioritarios 10.1, 10.7 e 10.26 permanecem em ``ch10.py``.
Este modulo completa o capitulo com figuras vetoriais editaveis. Redes
numericas comuns usam o motor CA ao vivo. Problemas de projeto, provas
simbolicas e circuitos com AOP ideal preservam uma deducao algebrica que
continua sendo o procedimento correto depois da troca dos valores.
"""

from copy import deepcopy

SUBJECTS = ["Analise Nodal AC", "Analise Malhas AC", "Superposicao AC", "Thevenin AC"]


def _loop(source, series, shunts=(), right=None, arrow=None):
    """Rede em dois barramentos, compacta e sem textos sobre componentes."""
    y1, y2 = 78, 194
    left, right_x = 40, 278
    n_series = len(series)
    n_nodes = n_series + 1
    by_node = [[] for _ in range(n_nodes)]
    for node, kind, label in shunts:
        by_node[min(max(node, 0), n_nodes - 1)].append((kind, label))

    # A node with parallel branches receives a short horizontal bus.  This
    # keeps every vertical symbol and its label in its own column instead of
    # drawing several components on top of each other.
    slot_counts = []
    for node in range(n_nodes):
        slots = len(by_node[node])
        if node == 0:
            slots += 1                    # source at the left
        if node == n_nodes - 1 and (right or not by_node[node]):
            slots += 1                    # right branch or closing wire
        slot_counts.append(max(1, slots))
    spacing = 70
    region_widths = [spacing * (slots - 1) for slots in slot_counts]
    used_by_regions = sum(region_widths)
    series_span = ((right_x - left - used_by_regions) / n_series
                   if n_series else 0)
    if n_series and series_span < 42:
        spacing = max(18, int((right_x - left - 42 * n_series) /
                              max(1, sum(slots - 1 for slots in slot_counts))))
        region_widths = [spacing * (slots - 1) for slots in slot_counts]
        used_by_regions = sum(region_widths)
        series_span = (right_x - left - used_by_regions) / n_series

    starts, ends = [], []
    cursor = float(left)
    for node in range(n_nodes):
        starts.append(round(cursor))
        cursor += region_widths[node]
        ends.append(round(cursor))
        if node < n_series:
            cursor += series_span

    ops = []
    source_kind = "isrc_v" if "A" in source and "V" not in source else "vsrc_v"
    if source_kind == "isrc_v":
        ops.append((source_kind, starts[0], y1, y2, source, True))
    else:
        ops.append((source_kind, starts[0], y1, y2, source))

    for node in range(n_nodes):
        if starts[node] != ends[node]:
            ops.append(("wire", starts[node], y1, ends[node], y1))
        offset = 1 if node == 0 else 0
        for index, (kind, label) in enumerate(by_node[node]):
            x = starts[node] + spacing * (offset + index)
            if kind in ("isrc_v", "dis_v"):
                ops.append((kind, x, y1, y2, label, True))
            else:
                ops.append((kind, x, y1, y2, label))

    for i, (kind, label) in enumerate(series):
        ops.append((kind, ends[i], y1, starts[i + 1], label))
    if not series:
        ops.append(("wire", starts[0], y1, ends[0], y1))

    last_x = ends[-1]
    if right:
        kind, label = right
        if kind in ("isrc_v", "dis_v"):
            ops.append((kind, last_x, y1, y2, label, True))
        else:
            ops.append((kind, last_x, y1, y2, label))
    elif not by_node[-1]:
        ops.append(("wire", last_x, y1, last_x, y2))

    ops += [("wire", starts[0], y2, last_x, y2), ("gnd", 160, y2)]
    if arrow:
        orient, label = arrow
        if orient == "h":
            ops.append(("arr_h", 55, 58, 108, label, True))
        elif label.lower().startswith("v"):
            ops.append(("pm", 306, 96, 178))
            ops.append(("lbl", label, 292, 156))
        else:
            ops.append(("arr_v", 292, 98, 174, label, False))
    return ops


def _parallel(source, branches, output="V"):
    """Fonte a esquerda e ramos paralelos bem espacos."""
    y1, y2 = 78, 194
    source_op = ("isrc_v",40,y1,y2,source,True) if "A" in source and "V" not in source else ("vsrc_v",40,y1,y2,source)
    ops = [source_op,
           ("wire", 40, y1, 280, y1), ("wire", 40, y2, 280, y2)]
    xs = [92, 150, 208, 270]
    for x, (kind, label) in zip(xs, branches):
        ops.append((kind, x, y1, y2, label))
    ops += [("vo", 304, 96, 178, output), ("gnd", 160, y2)]
    return ops


def _port(branches, source=None):
    """Rede paralela vista pelos terminais a-b."""
    y1, y2 = 78, 194
    ops = [("term", 286, y1, "a"), ("term", 286, y2, "b"),
           ("wire", 42, y1, 286, y1), ("wire", 42, y2, 286, y2)]
    if source:
        kind, label, up = source
        ops.append((kind, 42, y1, y2, label, up))
    xs = [96, 154, 212, 268]
    for x, (kind, label) in zip(xs, branches):
        ops.append((kind, x, y1, y2, label))
    ops.append(("gnd", 180, y2))
    return ops


def _opamp(source, input_parts, feedback_parts=(), load=None, noninv_top=False):
    """AOP ideal em uma pagina; externos continuam todos editaveis."""
    ops = [("vsrc_v", 36, 112, 196, source), ("wire", 36, 196, 286, 196)]
    x = 36
    end = 184
    step = (end - x) // max(1, len(input_parts))
    for i, (kind, label) in enumerate(input_parts):
        nx = end if i + 1 == len(input_parts) else x + step
        ops.append((kind, x, 112, nx, label))
        x = nx
    ops += [("wire", end, 112, 190, 93), ("opamp", 190, 80, noninv_top),
            ("wire", 190, 117, 190, 196), ("wire", 252, 109, 286, 109),
            ("vo", 304, 112, 184, "Vo"), ("gnd", 190, 196)]
    if feedback_parts:
        fx = 190
        ops += [("wire", 190, 93, 190, 58), ("wire", 252, 109, 252, 58)]
        span = 62 // len(feedback_parts)
        for i, (kind, label) in enumerate(feedback_parts):
            nx = 252 if i + 1 == len(feedback_parts) else fx + span
            ops.append((kind, fx, 58, nx, label))
            fx = nx
    if load:
        ops.append((load[0], 286, 109, 196, load[1]))
    return ops


def _bridge(source, top_left, top_right, bottom_left, bottom_right, middle=None):
    source_op = ("isrc_v",38,78,194,source,True) if "A" in source and "V" not in source else ("vsrc_v",38,78,194,source)
    ops = [source_op,
           (top_left[0], 38, 78, 150, top_left[1]),
           (top_right[0], 150, 78, 274, top_right[1]),
           (bottom_left[0], 38, 194, 150, bottom_left[1]),
           (bottom_right[0], 150, 194, 274, bottom_right[1]),
           ("wire", 274, 78, 274, 194), ("gnd", 274, 194)]
    if middle:
        ops.append((middle[0], 150, 78, 194, middle[1]))
    return ops


CIRCUITS = {
    # 10.1--10.19: analise nodal.  10.1 e 10.7 estao em ch10.py.
    "p10_2": _loop("4/_0V", [("res_h", "2")],
                    [(1, "imp_v", "-j5"), (1, "imp_v", "j4")], arrow=("v", "Vo")),
    "p10_3": _loop("16/_-90V", [("res_h", "4"), ("cap_h", "83.33mF"),
                                  ("ind_h", "2H")],
                    [(2, "res_v", "1"), (2, "isrc_v", "2/_0A")],
                    right=("res_v", "6"), arrow=("v", "Vo")),
    "p10_4": _loop("16/_-100V", [("ind_h", "1H"), ("cap_h", "0.25F")],
                    [(1, "isrc_v", "0.5A")], right=("res_v", "1"), arrow=("v", "Vo")),
    "p10_5": _loop("25V", [("res_h", "2k"), ("cap_h", "2uF")],
                    [(1, "ind_v", "0.25H")], right=("dvs_v", "10"), arrow=("v", "Vo")),
    "p10_6": _loop("12V", [("res_h", "20"), ("imp_h", "j10")],
                    [(1, "isrc_v", "3A")], right=("res_v", "20"), arrow=("v", "Vx")),
    "p10_8": [("isrc_v", 40, 78, 194, "6/_15A", True),
               ("wire", 40, 78, 128, 78), ("res_v", 80, 78, 194, "20"),
               ("cap_v", 124, 78, 194, "50uF"),
               ("res_h", 128, 78, 240, "40"), ("ind_v", 240, 78, 194, "0.1H"),
               ("isrc_h", 240, 120, 128, "0.1A", False),
               ("wire", 128, 78, 128, 120), ("wire", 240, 78, 240, 120),
               ("wire", 40, 194, 240, 194), ("arr_h", 148, 58, 218, "io", True),
               ("gnd", 150, 194)],
    "p10_9": _loop("10V", [("res_h", "20"), ("cap_h", "50uF"),
                            ("ind_h", "10mH")],
                    [(1, "res_v", "20"), (2, "isrc_v", "4A")],
                    right=("res_v", "30"), arrow=("v", "Vo")),
    "p10_10": _loop("36/_-90A", [("cap_h", "2uF")],
                     [(0, "res_v", "2k"), (0, "ind_v", "50mH"),
                      (1, "isrc_v", "0.1A")], right=("res_v", "4k"), arrow=("v", "Vo")),
    "p10_11": [("vsrc_v", 40, 78, 194, "8/_-60V"),
                ("cap_h", 40, 78, 90, "0.25F"), ("wire", 90, 78, 220, 78),
                ("res_v", 100, 78, 194, "2"), ("ind_v", 155, 78, 194, "1H"),
                ("cap_v", 210, 78, 194, "0.5F"), ("ind_h", 220, 78, 278, "2H"),
                ("isrc_v", 278, 78, 194, "1A", True), ("wire", 40, 194, 278, 194),
                ("arr_v", 292, 98, 174, "Io", False), ("gnd", 160, 194)],
    "p10_12": _loop("5A", [("res_h", "2")],
                     [(0, "res_v", "4"), (1, "cap_v", "0.1F")],
                     right=("ind_v", "1H")) +
               [("arr_v", 180, 100, 172, "Io", False)],
    "p10_13": _loop("40/_30V", [("imp_h", "-j2"), ("imp_h", "8+j6")],
                     [(1, "res_v", "3")], right=("res_v", "10"), arrow=("v", "Vx")),
    "p10_14": _port([("imp_v", "-j2"), ("res_v", "10"),
                       ("imp_v", "j2"), ("imp_v", "-j5")],
                      source=("isrc_v", "20/_30A", True)),
    "p10_15": _loop("20/_-90V", [("res_h", "2"), ("imp_h", "j1")],
                     [(1, "imp_v", "-j2"), (2, "isrc_v", "10A")],
                     right=("res_v", "4"), arrow=("v", "I")),
    "p10_16": _loop("2A", [("imp_h", "j4")],
                     [(0, "res_v", "5"), (1, "imp_v", "-j3")],
                     right=("isrc_v", "3/_45A"), arrow=("v", "Vx")),
    "p10_17": _bridge("100/_20V", ("imp_h", "j4"), ("res_h", "1"),
                       ("res_h", "3"), ("imp_h", "-j2"), ("res_v", "2")),
    "p10_18": _loop("4/_45A", [("imp_h", "8+j6"), ("imp_h", "4+j5")],
                     [(0, "res_v", "2"), (1, "imp_v", "-j1"),
                      (1, "isrc_v", "8A")], right=("imp_v", "-j2"), arrow=("v", "Vo")),
    "p10_19": _loop("12V", [("res_h", "4")],
                     [(0, "imp_v", "j2"), (1, "imp_v", "-j4")],
                     right=("isrc_v", "2.4A"), arrow=("v", "Vo")),

    # 10.20--10.23: funcoes de transferencia.
    "p10_20": _loop("10V", [("res_h", "2")],
                     [(1, "ind_v", "1H")], right=("cap_v", "0.25F"), arrow=("v", "Vo")),
    "p10_21": _loop("10V", [("res_h", "2"), ("ind_h", "1H")],
                     right=("cap_v", "0.25F"), arrow=("v", "Vo")),
    "p10_22": _loop("10V", [("res_h", "2")],
                     [(1, "res_v", "3"), (1, "ind_v", "1H")],
                     right=("cap_v", "0.25F"), arrow=("v", "Vo")),
    "p10_23": _loop("10V", [("res_h", "2")],
                     [(1, "ind_v", "1H"), (1, "cap_v", "0.25F")],
                     right=("cap_v", "0.5F"), arrow=("v", "V")),

    # 10.24--10.39: malhas.  10.26 esta em ch10.py.
    "p10_25": _loop("10V", [("res_h", "4"), ("ind_h", "2H")],
                     [(1, "cap_v", "0.25F")], right=("vsrc_v", "6/_-90V"), arrow=("v", "io")),
    "p10_27": _loop("40/_30V", [("imp_h", "j10"), ("res_h", "40")],
                     [(1, "imp_v", "-j20")], right=("vsrc_v", "50V"), arrow=("h", "I1")),
    "p10_28": _loop("10V", [("res_h", "1"), ("ind_h", "1H"),
                             ("ind_h", "1H"), ("res_h", "1")],
                     [(2, "cap_v", "1F"), (2, "res_v", "1")],
                     right=("vsrc_v", "20/_-30V"), arrow=("h", "i1")),
    "p10_29": _bridge("10V", ("imp_h", "j4"), ("res_h", "3"),
                       ("res_h", "1"), ("imp_h", "-j2"), ("res_v", "2")),
    "p10_30": _loop("120/_90V", [("res_h", "20"), ("ind_h", "0.4H"),
                                  ("ind_h", "0.2H")],
                     [(1, "ind_v", "0.3H"), (2, "cap_v", "50uF")],
                     right=("res_v", "10"), arrow=("v", "Vo")),
    "p10_31": _loop("100/_120V", [("res_h", "80"), ("imp_h", "j60"),
                                   ("res_h", "20")],
                     [(1, "imp_v", "-j40"), (2, "imp_v", "-j40")],
                     right=("vsrc_v", "60/_-30V"), arrow=("h", "Io")),
    "p10_32": _loop("4/_-30A", [("imp_h", "j4")],
                     [(0, "res_v", "2"), (1, "dvs_v", "3")],
                     right=("imp_v", "-j2"), arrow=("v", "Io")),
    "p10_36": _loop("2A", [("imp_h", "j4"), ("imp_h", "-j3")],
                     [(1, "res_v", "2")], right=("vsrc_v", "12V"), arrow=("v", "Vo")),
    "p10_37": _parallel("120/_-90V", [("imp_v", "80-j35"),
                                       ("imp_v", "80-j35")], "I"),
    "p10_38": _bridge("10/_90V", ("res_h", "2"), ("imp_h", "-j4"),
                       ("res_h", "1"), ("res_h", "1"), ("imp_v", "j2")),
    "p10_39": _bridge("12/_64V", ("res_h", "20"), ("imp_h", "j16"),
                       ("res_h", "10"), ("imp_h", "-j25"), ("res_v", "8")),

    # 10.40--10.54: superposicao e transformacao de fontes.
    "p10_40": _loop("10V", [("res_h", "4"), ("res_h", "2")],
                     [(1, "ind_v", "1H")], right=("vsrc_v", "8V"), arrow=("v", "io")),
    "p10_41": _loop("6V", [("cap_h", "0.25F")], right=("res_v", "2"), arrow=("v", "Vo")),
    "p10_42": _loop("10V", [("ind_h", "1H"), ("res_h", "2")],
                     [(1, "res_v", "4"), (1, "cap_v", "0.25F")],
                     right=("vsrc_v", "5V"), arrow=("h", "Io")),
    "p10_43": _loop("5/_10A", [("cap_h", "0.125F"), ("res_h", "3")],
                     [(0, "ind_v", "4H")], right=("vsrc_v", "10/_-60V"), arrow=("h", "ix")),
    "p10_44": _loop("12/_10A", [("res_h", "20"), ("ind_h", "5H")],
                     [(0, "res_v", "16")], right=("vsrc_v", "50/_-90V"), arrow=("v", "Vx")),
    "p10_45": _loop("16/_30V", [("res_h", "20"), ("ind_h", "0.3H")],
                     right=("vsrc_v", "6/_-90V"), arrow=("h", "i")),
    "p10_46": [("vsrc_v", 40, 78, 194, "12V"), ("res_h", 40, 78, 104, "6"),
                ("wire", 104, 78, 210, 78), ("cap_v", 120, 78, 194, "83.33mF"),
                ("isrc_v", 190, 78, 194, "4A", True), ("ind_h", 210, 78, 278, "2H"),
                ("vsrc_v", 278, 78, 194, "10V"), ("wire", 40, 194, 278, 194),
                ("pm", 306, 96, 178), ("lbl", "Vo", 292, 156),
                ("gnd", 160, 194)],
    "p10_47": _loop("10/_-120V", [("res_h", "1"), ("cap_h", "0.1667F"),
                                   ("vsrc_h", "24V"), ("ind_h", "2H")],
                     [(2, "res_v", "2"), (3, "isrc_v", "2A")],
                     right=("res_v", "4"), arrow=("v", "io")),
    "p10_48": _bridge("50V", ("cap_h", "20uF"), ("res_h", "100"),
                       ("ind_h", "40mH"), ("vsrc_h", "24V"), ("res_v", "80")),
    "p10_49": _loop("8/_-60A", [("res_h", "3"), ("ind_h", "5mH"),
                                 ("cap_h", "1mF")],
                     [(0, "res_v", "5")], arrow=("h", "i")),
    "p10_50": _loop("10V", [("res_h", "2"), ("ind_h", "1H")],
                     [(1, "cap_v", "0.25F")], right=("res_v", "4"), arrow=("v", "Vo")),
    "p10_52": _loop("60V", [("res_h", "2"), ("imp_h", "j4"), ("imp_h", "-j2")],
                     [(2, "res_v", "6")], right=("isrc_v", "5/_90A"), arrow=("v", "Ix")),
    "p10_53": _loop("20V", [("res_h", "4"), ("imp_h", "-j3"), ("imp_h", "j4")],
                     [(1, "imp_v", "j2"), (2, "res_v", "2")],
                     right=("imp_v", "-j2"), arrow=("v", "Vo")),

    # 10.55--10.68: Thevenin e Norton.
    "p10_55": [("vsrc_v", 40, 78, 194, "50/_30V"),
                ("imp_h", 40, 78, 130, "j20"), ("res_h", 130, 78, 220, "10"),
                ("imp_v", 130, 78, 194, "-j10"), ("term", 276, 78, "a"),
                ("term", 276, 194, "b"), ("wire", 220, 78, 276, 78),
                ("wire", 40, 194, 276, 194), ("gnd", 170, 194)],
    "p10_56": [("isrc_v", 40, 78, 194, "2A", True),
                ("res_h", 40, 78, 112, "6"), ("imp_h", 112, 78, 175, "j4"),
                ("imp_h", 112, 116, 175, "-j2"), ("wire", 112, 78, 112, 116),
                ("wire", 175, 78, 175, 116), ("term", 278, 78, "a"),
                ("term", 278, 194, "b"), ("wire", 175, 78, 278, 78),
                ("wire", 40, 194, 278, 194), ("gnd", 180, 194)],
    "p10_57": [("vsrc_v", 40, 78, 194, "10V"), ("res_h", 40, 78, 105, "2"),
                ("cap_h", 105, 78, 170, "0.25F"), ("ind_v", 170, 78, 194, "1H"),
                ("res_h", 170, 78, 235, "3"), ("term", 282, 78, "a"),
                ("term", 282, 194, "b"), ("wire", 235, 78, 282, 78),
                ("wire", 40, 194, 282, 194), ("gnd", 190, 194)],
    "p10_58": _port([("imp_v", "8-j6"), ("imp_v", "j10")],
                      source=("isrc_v", "5/_45A", True)),
    "p10_59": [("dis_v", 54, 78, 194, "0.2", True),
                ("ind_v", 118, 78, 194, "40H"), ("imp_h", 118, 78, 190, "-j2"),
                ("res_h", 190, 78, 260, "10"), ("wire", 260, 78, 286, 78),
                ("term", 286, 78, "a"),
                ("term", 286, 194, "b"), ("wire", 54, 78, 118, 78),
                ("wire", 54, 194, 286, 194), ("gnd", 170, 194)],
    "p10_60": [("vsrc_v", 38, 78, 194, "20V"), ("res_h", 38, 78, 104, "10"),
                ("imp_v", 104, 78, 194, "j5"), ("imp_h", 104, 78, 180, "-j4"),
                ("isrc_v", 180, 78, 194, "4A", True), ("res_v", 258, 78, 194, "4"),
                ("wire", 180, 78, 284, 78), ("wire", 38, 194, 284, 194),
                ("term", 284, 78, "a"), ("term", 284, 194, "b"), ("gnd", 160, 194)],
    "p10_61": [("isrc_v", 40, 78, 194, "2A", True), ("imp_v", 104, 78, 194, "-j3"),
                ("res_h", 104, 78, 205, "4"), ("dis_v", 205, 78, 194, "1.5", True),
                ("term", 282, 78, "a"), ("term", 282, 194, "b"),
                ("wire", 40, 78, 104, 78), ("wire", 205, 78, 282, 78),
                ("wire", 40, 194, 282, 194), ("gnd", 160, 194)],
    "p10_62": _loop("12V", [("res_h", "4"), ("ind_h", "2H"), ("cap_h", "0.125F")],
                     [(1, "cap_v", "0.25F"), (2, "isrc_v", "3A")],
                     right=("res_v", "2"), arrow=("v", "Vo")),
    "p10_63": [("isrc_v", 42, 78, 194, "4/_30A", True),
                ("ind_v", 112, 78, 194, "10H"), ("res_v", 178, 78, 194, "2k"),
                ("cap_h", 178, 78, 255, "5uF"), ("term", 286, 78, "a"),
                ("term", 286, 194, "b"), ("wire", 42, 78, 178, 78),
                ("wire", 255, 78, 286, 78), ("wire", 42, 194, 286, 194),
                ("gnd", 180, 194)],
    "p10_64": [("isrc_v", 40, 78, 194, "3/_60A", True),
                ("res_v", 118, 78, 136, "60"), ("imp_v", 118, 136, 194, "j80"),
                ("res_v", 238, 78, 136, "40"), ("imp_v", 238, 136, 194, "-j30"),
                ("term", 118, 136, "a"), ("term", 238, 136, "b"),
                ("wire", 40, 78, 238, 78), ("wire", 40, 194, 238, 194),
                ("gnd", 180, 194)],
    "p10_65": _loop("10V", [("res_h", "2"), ("vsrc_h", "6V")],
                     [(0, "cap_v", "0.25F"), (1, "ind_v", "1H")],
                     right=("cap_v", "0.5F")) +
                [("arr_v", 230, 98, 174, "io", False)],
    "p10_66": [("isrc_v", 40, 78, 194, "2/_-90A", True),
                ("cap_h", 40, 78, 110, "10mF"), ("res_v", 110, 78, 194, "10"),
                ("vsrc_h", 110, 78, 184, "12V"), ("ind_v", 184, 78, 194, "0.5H"),
                ("dis_v", 248, 78, 194, "2", True), ("term", 284, 78, "a"),
                ("term", 284, 194, "b"), ("wire", 184, 78, 284, 78),
                ("wire", 40, 194, 284, 194), ("gnd", 180, 194)],
    "p10_67": _bridge("60/_45V", ("imp_h", "13-j5"), ("res_h", "12"),
                       ("res_h", "10"), ("imp_h", "8+j6"), None),
    "p10_68": [("vsrc_v", 38, 78, 194, "6/_-90V"), ("res_h", 38, 78, 116, "4"),
                ("dvs_v", 116, 78, 194, "0.333"), ("dis_v", 188, 78, 194, "4", True),
                ("cap_v", 236, 78, 194, "50mF"), ("ind_v", 278, 78, 194, "1H"),
                ("term", 298, 78, "a"), ("term", 298, 194, "b"),
                ("wire", 188, 78, 298, 78), ("wire", 38, 194, 298, 194),
                ("gnd", 160, 194)],

    # 10.69--10.80: AOPs. O simbolo do AOP e mantido; a deducao e algebrica.
    "p10_69": _opamp("10V", [("cap_h", "0.1F")], [("res_h", "10")]),
    "p10_70": _opamp("10V", [("res_h", "2")], [("res_h", "10"), ("cap_h", "0.1F")]),
    "p10_71": _opamp("8/_30V", [("res_h", "2k")],
                      [("res_h", "10k"), ("cap_h", "0.5uF")]),
    "p10_72": _opamp("4V", [("res_h", "50k")], (), ("res_v", "100k"), True) +
               [("cap_v", 184, 112, 196, "1nF")],
    "p10_73": _opamp("10V", [("res_h", "10k"), ("res_h", "20k")],
                      [("cap_h", "10nF")]) + [("cap_v", 184, 112, 196, "20nF")],
    "p10_74": _opamp("10V", [("res_h", "10k"), ("cap_h", "10nF")],
                      [("res_h", "20k"), ("cap_h", "20nF")]),
    "p10_75": _opamp("10V", [("cap_h", "1nF"), ("cap_h", "1nF")],
                      [("res_h", "100k")]) +
               [("res_v", 110, 112, 196, "20k"), ("res_v", 286, 109, 196, "40k")],
    "p10_76": _opamp("2/_30V", [("cap_h", "0.25mF"), ("res_h", "10k")],
                      [("res_h", "20k")]) + [("cap_v", 184, 112, 196, "0.5mF")],
    "p10_77": _opamp("10V", [("res_h", "10k")],
                      [("res_h", "20k"), ("cap_h", "0.1uF")]) +
               [("cap_v", 184, 112, 196, "0.1uF")],
    "p10_78": _opamp("2/_-90V", [("res_h", "10k"), ("cap_h", "0.5uF")],
                      [("res_h", "20k")]) + [("cap_v", 110, 112, 196, "0.25uF")],
    "p10_79": _opamp("5V", [("res_h", "10k"), ("cap_h", "0.1uF")],
                      [("res_h", "20k")]) + [("cap_v", 286, 109, 196, "0.2uF")],
    "p10_80": _opamp("4/_-60V", [("cap_h", "0.1uF")],
                      [("res_h", "20k")]) + [("res_h", 252, 109, 286, "10k")],

    # 10.81--10.88: redes para simulacao CA.
    "p10_81": _loop("24V", [("imp_h", "-j2"), ("res_h", "25")],
                     [(1, "res_v", "30"), (1, "imp_v", "j4")],
                     right=("res_v", "40"), arrow=("v", "Vo")),
    "p10_83": _loop("2A", [("res_h", "2"), ("res_h", "8")],
                     [(0, "res_v", "4"), (1, "res_v", "6"),
                      (1, "ind_v", "10mH")], right=("cap_v", "4uF"), arrow=("v", "Vo")),
    "p10_84": _loop("3A", [("imp_h", "-j2")],
                     [(0, "imp_v", "j4"), (1, "dis_v", "2")],
                     right=("res_v", "2"), arrow=("v", "Vo")),
    "p10_85": _bridge("2A", ("res_h", "4"), ("res_h", "3"),
                       ("res_h", "2"), ("res_h", "4"), ("ind_v", "1H")),
    "p10_86": _loop("60/_30V", [("imp_h", "j10"), ("imp_h", "j10")],
                     [(1, "imp_v", "-j4")], right=("isrc_v", "4A"), arrow=("v", "V3")) +
               [("res_h", 40, 52, 278, "8"),
                ("wire", 40, 52, 40, 78), ("wire", 278, 52, 278, 78)],
    "p10_87": _loop("4A", [("imp_h", "-j4"), ("res_h", "2"), ("res_h", "1")],
                     [(0, "res_v", "8"), (2, "imp_v", "j6")],
                     right=("isrc_v", "2A"), arrow=("v", "V3")),
    "p10_88": _loop("6V", [("res_h", "4"), ("cap_h", "20mF")],
                     [(2, "dvs_v", "0.5")], right=("res_v", "10"), arrow=("v", "Vo")),

    # 10.89--10.96: aplicacoes e osciladores (deducoes simbolicas).
    "p10_89": _opamp("10V", [("res_h", "10k"), ("res_h", "20k")],
                      [("res_h", "30k"), ("cap_h", "0.1uF")]),
    "p10_90": _bridge("10V", ("res_h", "10k"), ("res_h", "20k"),
                       ("cap_h", "10nF"), ("cap_h", "10nF"), ("res_v", "10k")),
    "p10_91": _opamp("10V", [("ind_h", "0.4mH"), ("cap_h", "2nF"),
                              ("res_h", "10k")], [("res_h", "80k")]),
    "p10_92": _opamp("10V", [("ind_h", "10uH"), ("cap_h", "2nF")],
                      [("res_h", "1000k")]) + [("res_v", 184, 112, 196, "10k")],
    "p10_93": [("opamp", 190, 72, False), ("res_h", 190, 52, 252, "100k"),
                ("wire", 190, 52, 190, 85), ("wire", 252, 52, 252, 101),
                ("wire", 252, 101, 282, 101), ("wire", 190, 109, 190, 194),
                ("ind_h", 96, 146, 220, "1mH"), ("cap_v", 96, 146, 194, "10nF"),
                ("cap_v", 220, 146, 194, "10nF"), ("wire", 220, 146, 252, 101),
                ("wire", 96, 146, 190, 109), ("wire", 96, 194, 220, 194),
                ("vo", 304, 108, 182, "Vo"), ("gnd", 190, 194)],
    "p10_94": [("opamp", 190, 72, False), ("res_h", 190, 52, 252, "100k"),
                ("wire", 190, 52, 190, 85), ("wire", 252, 52, 252, 101),
                ("wire", 252, 101, 282, 101), ("wire", 190, 109, 190, 194),
                ("ind_h", 96, 146, 220, "1.013mH"),
                ("cap_v", 96, 146, 194, "20nF"), ("cap_v", 220, 146, 194, "20nF"),
                ("wire", 220, 146, 252, 101), ("wire", 96, 146, 190, 109),
                ("wire", 96, 194, 220, 194), ("vo", 304, 108, 182, "Vo"),
                ("gnd", 190, 194)],
    "p10_95": [("opamp", 190, 72, False), ("res_h", 190, 52, 252, "100k"),
                ("wire", 190, 52, 190, 85), ("wire", 252, 52, 252, 101),
                ("wire", 252, 101, 282, 101), ("wire", 190, 109, 190, 194),
                ("cap_h", 96, 146, 220, "10nF"), ("ind_v", 96, 146, 194, "1mH"),
                ("ind_v", 220, 146, 194, "1mH"), ("wire", 220, 146, 252, 101),
                ("wire", 96, 146, 190, 109), ("wire", 96, 194, 220, 194),
                ("vo", 304, 108, 182, "Vo"), ("gnd", 190, 194)],
    "p10_96": [("opamp", 190, 72, False), ("res_h", 190, 52, 252, "20k"),
                ("wire", 190, 52, 190, 85), ("wire", 252, 52, 252, 101),
                ("wire", 252, 101, 282, 101), ("wire", 190, 109, 190, 194),
                ("res_h", 82, 146, 142, "10k"), ("ind_h", 142, 146, 220, "1mH"),
                ("ind_v", 82, 146, 194, "1mH"), ("res_v", 142, 146, 194, "10k"),
                ("wire", 220, 146, 252, 101), ("wire", 82, 146, 190, 109),
                ("wire", 82, 194, 190, 194), ("vo", 304, 108, 182, "Vo"),
                ("gnd", 190, 194)],
}

# Nas duas figuras de malha RLC, a seta fica dentro da malha para nao ocupar
# a mesma faixa dos rotulos dos dois indutores superiores.
for _mesh_id in ("p10_28",):
    CIRCUITS[_mesh_id] = [
        ("arr_h", 52, 116, 104, op[4], True)
        if op[0] == "arr_h" else op
        for op in CIRCUITS[_mesh_id]
    ]


# Exercicios que reutilizam exatamente a figura indicada no enunciado.
for _dst, _src in {33: 15, 34: 28, 35: 30, 51: 42, 54: 7, 82: 19}.items():
    # 10.7 e 10.26 ficam em outro modulo; 10.54 recebe uma copia explicita
    # adiante para nao depender de CIRCUITS entre modulos.
    if "p10_%d" % _src in CIRCUITS:
        CIRCUITS["p10_%d" % _dst] = deepcopy(CIRCUITS["p10_%d" % _src])

# 10.54 referencia o 10.7, que pertence ao modulo prioritario ch10.py.
CIRCUITS["p10_54"] = [
    ("vsrc_v", 42, 78, 194, "120/_-15V"),
    ("res_h", 42, 78, 112, "40"), ("imp_h", 112, 78, 185, "j20"),
    ("wire", 185, 78, 282, 78), ("isrc_v", 200, 78, 194, "6/_30A", False),
    ("imp_v", 240, 78, 194, "-j30"), ("res_v", 280, 78, 194, "50"),
    ("wire", 42, 194, 282, 194), ("lbl", "V", 188, 60), ("gnd", 200, 194),
]

# Colpitts/Hartley: the former abbreviated picture shorted the tank to the
# grounded non-inverting input. Keep the real input resistor and tank nodes.
def _tank(kind,left,right):
    return [('opamp',190,72,False),('res_h',190,52,252,'100k'),
            ('wire',190,52,190,85),('wire',252,52,252,101),
            ('res_h',96,85,190,'10k'),('wire',96,85,96,146),
            ('wire',190,109,190,194),('wire',252,101,252,146),
            (kind[0],96,146,252,kind[1]),(left[0],96,146,194,left[1]),
            (right[0],252,146,194,right[1]),('wire',96,194,252,194),
            ('gnd',190,194),('vo',304,108,182,'Vo')]
CIRCUITS['p10_93']=_tank(('ind_h','1mH'),('cap_v','10nF'),('cap_v','10nF'))
CIRCUITS['p10_94']=_tank(('ind_h','1.013mH'),('cap_v','20nF'),('cap_v','20nF'))
CIRCUITS['p10_95']=_tank(('cap_h','10nF'),('ind_v','1mH'),('ind_v','1mH'))
CIRCUITS['p10_96']=[op for op in CIRCUITS['p10_96'] if op!=('wire',190,109,190,194)]
CIRCUITS['p10_96'] += [('res_v',172,52,194,'10k'),('wire',172,52,190,52)]
# Followers must feed their output back to the minus input, not ground it.
for _key in ('p10_72',):
    CIRCUITS[_key]=[op for op in CIRCUITS[_key] if op!=('wire',190,117,190,196)]
    CIRCUITS[_key]+=[('wire',190,117,252,117),('wire',252,117,252,109)]
# 10.56(a): the current source is connected at a-b, and the 6 ohm branch
# returns to b; otherwise a constant current has no return path at all.
CIRCUITS['p10_56']=[op for op in CIRCUITS['p10_56'] if op[0]!='isrc_v']
CIRCUITS['p10_56'] += [('wire',40,78,40,194),('isrc_v',278,78,194,'2A',True)]
CIRCUITS['p10_48']=[('vsrc_v',40,78,136,'50V'),('cap_h',40,78,170,'20uF'),
    ('res_v',278,78,136,'100'),('ind_h',40,136,170,'40mH'),
    ('vsrc_v',278,136,194,'24V'),('res_v',170,78,136,'80'),
    ('isrc_v',40,136,194,'2/_-90A',True),('res_v',170,136,194,'60'),
    ('wire',170,78,278,78),('wire',40,194,278,194),('gnd',110,194),
    ('arr_v',304,86,122,'Io',True)]
# Complete numerical inputs for the oscillator/inductance demonstrations.
CIRCUITS['p10_89'] += [('res_v',286,109,196,'40k')]
CIRCUITS['p10_91'] += [('res_v',286,109,196,'20k')]
CIRCUITS['p10_92'] += [('res_v',286,109,196,'100k')]
CIRCUITS['p10_90']=[('vsrc_v',30,78,194,'10V'),
    ('res_h',30,78,88,'10k'),('cap_h',88,78,150,'10nF'),
    ('res_v',150,120,194,'10k'),('cap_v',100,120,194,'10nF'),
    ('res_v',270,78,136,'20k'),('res_v',270,136,194,'10k'),
    ('wire',30,78,30,58),('wire',30,58,270,58),('wire',270,58,270,78),
    ('wire',150,78,150,120),('wire',100,120,150,120),('wire',30,194,270,194),
    ('term',176,120,'a'),('wire',150,120,176,120),('term',286,136,'b'),
    ('wire',270,136,286,136),('gnd',210,194)]

# True series branches (the former compact figures incorrectly paralleled
# both elements). Component order is kept stable for the live equations.
for _key, _first, _second in [('p10_22',('res_v','3'),('ind_v','1H')),
                              ('p10_23',('ind_v','1H'),('cap_v','0.25F'))]:
    CIRCUITS[_key]=[('vsrc_v',40,78,194,'10V'),
        (_first[0],160,78,136,_first[1]),(_second[0],160,136,194,_second[1]),
        ('res_h',40,78,160,'2'),('cap_v',270,78,194,'0.25F' if _key=='p10_22' else '0.5F'),
        ('wire',160,78,270,78),('wire',40,194,270,194),('gnd',210,194),('vo',302,98,174,'Vo')]
CIRCUITS['p10_46']=[('isrc_v',*op[1:4],'4/_-90A',True) if op[0]=='isrc_v' else op for op in CIRCUITS['p10_46']]
CIRCUITS['p10_67'] += [('term',150,78,'a'),('term',150,194,'b')]

def _sallen(source,zfirst,zsecond,zfeedback,zground,rf=None,rg=None):
    """Two input impedances, positive feedback, and a true non-inverter."""
    ops=[('vsrc_v',30,112,196,source),
        (zfirst[0],30,112,102,zfirst[1]),(zsecond[0],102,112,174,zsecond[1]),
        (zfeedback[0],102,58,270,zfeedback[1]),(zground[0],174,112,196,zground[1]),
        ('wire',102,112,102,58),('wire',174,112,190,93),('opamp',190,80,True),
        ('wire',252,109,270,109),('wire',270,58,270,109),
        ('wire',30,196,286,196),('gnd',100,196),('vo',302,116,180,'Vo')]
    if rf:
        ops += [(rf[0],212,158,286,rf[1]),(rg[0],212,158,196,rg[1]),
                ('wire',190,117,212,158),('wire',270,109,286,109),('wire',286,109,286,158)]
    else:ops += [('wire',190,117,252,117),('wire',252,117,252,109)]
    return ops

CIRCUITS['p10_71']=[('vsrc_v',30,93,196,'8/_30V'),('res_v',170,158,196,'2k'),
    ('res_h',190,158,286,'10k'),('cap_h',190,180,286,'0.5uF'),
    ('opamp',190,80,True),('wire',30,93,190,93),('wire',170,158,190,158),
    ('wire',190,117,190,180),('wire',286,109,286,180),('wire',252,109,286,109),
    ('wire',30,196,286,196),('gnd',100,196),('vo',302,116,180,'Vo')]
CIRCUITS['p10_73']=_sallen('10V',('res_h','10k'),('res_h','20k'),('cap_h','10nF'),('cap_v','20nF'))
CIRCUITS['p10_75']=_sallen('10V',('cap_h','1nF'),('cap_h','1nF'),('res_h','100k'),('res_v','100k'),('res_h','40k'),('res_v','20k'))
CIRCUITS['p10_76']=_sallen('2/_30V',('imp_h','-j4000'),('res_h','10k'),('res_h','20k'),('imp_v','-j2000'))
CIRCUITS['p10_78']=_sallen('2/_-90V',('res_h','10k'),('cap_h','0.5uF'),('res_h','20k'),('res_v','10k'),('res_h','40k'),('res_v','20k'))
# The first capacitor in 10.78 is a shunt at the junction, not an input part.
CIRCUITS['p10_78'] += [('cap_v',76,138,196,'0.25uF'),('wire',102,112,102,138),('wire',76,138,102,138)]
CIRCUITS['p10_77']=[('vsrc_v',30,78,196,'10V'),('res_h',30,78,150,'10k'),
    ('cap_v',150,78,196,'10nF'),('res_v',170,158,196,'10k'),
    ('res_h',190,158,286,'20k'),('cap_h',190,180,286,'10nF'),
    ('opamp',190,80,True),('wire',150,78,190,93),('wire',170,158,190,158),
    ('wire',190,117,190,180),('wire',286,109,286,180),('wire',252,109,286,109),
    ('wire',30,196,286,196),('gnd',60,196),('vo',302,116,180,'Vo')]
# Separate parallel feedback labels vertically (capacitor label is y-28).
for _id in ('p10_71','p10_77'):
    CIRCUITS[_id]=[(op[0],op[1],135,op[3],op[4]) if op[0]=='res_h' and op[2]==158
        else ('res_v',170,135,196,op[4]) if op[0]=='res_v' and op[1]==170
        else ('wire',170,135,190,135) if op==('wire',170,158,190,158) else op
        for op in CIRCUITS[_id]]
    if _id=='p10_77':
        CIRCUITS[_id]=[('res_h',30,78,110,'10k') if op==('res_h',30,78,150,'10k')
            else ('cap_v',110,78,196,'10nF') if op==('cap_v',150,78,196,'10nF')
            else ('wire',110,78,190,93) if op==('wire',150,78,190,93) else op for op in CIRCUITS[_id]]
for _id in ('p10_73',):
    # Feedback capacitor must be below the header, including its own label.
    CIRCUITS[_id]=[(op[0],op[1],86,op[3],op[4]) if op[0]=='cap_h' and op[2]==58
        else ('wire',102,112,102,86) if op==('wire',102,112,102,58)
        else ('wire',270,86,270,109) if op==('wire',270,58,270,109) else op for op in CIRCUITS[_id]]

def _two_inverters(source,input1,feedback1,input2,feedback2,parallel1=None,cross=None):
    fy2=105 if feedback2[0]=='cap_h' else 110
    ops=[('vsrc_v',18,155,206,source),(input1[0],18,155,112,input1[1]),
        (feedback1[0],112,110,174,feedback1[1]),(input2[0],174,155,230,input2[1]),
        (feedback2[0],230,fy2,292,feedback2[1]),
        ('opamp',112,142,False),('opamp',230,142,False),
        ('wire',112,80,112,155),('wire',174,80,174,171),
        ('wire',230,fy2,230,155),('wire',292,fy2,292,171),
        ('wire',112,179,112,206),('wire',230,179,230,206),
        ('wire',18,206,292,206),('gnd',174,206),('vo',308,180,204,'Vo')]
    if parallel1:ops += [(parallel1[0],112,80,174,parallel1[1])]
    if cross:ops += [(cross[0],112,64,292,cross[1]),('wire',112,64,112,80),('wire',292,64,292,fy2)]
    return ops
CIRCUITS['p10_79']=_two_inverters('5V',('res_h','10k'),('res_h','20k'),('cap_h','0.2uF'),('res_h','40k'),('cap_h','0.1uF'))
CIRCUITS['p10_80']=_two_inverters('4/_-60V',('cap_h','0.1uF'),('res_h','20k'),('res_h','10k'),('cap_h','0.2uF'),cross=('res_h','50k'))

def _oscillator(kind):
    # c0 is an explicitly labelled test excitation, not an invented supply.
    # Preserve L,C,Rp,Rf,Ri order; the final register is the trial R/Ro.
    ops=[('vsrc_v',24,158,206,'10V'),
        ('ind_h',170,146,216,'0.4mH') if kind==91 else ('ind_v',100,146,206,'10uH'),
        ('cap_h',216,146,260,'2nF') if kind==91 else ('cap_v',170,146,206,'2nF'),
        ('res_v',170,146,206,'10k') if kind==91 else ('res_h',190,58,286,'1M'),
        ('res_h',190,58,286,'80k') if kind==91 else ('res_v',240,146,206,'10k'),
        ('res_v',130,85,206,'20k' if kind==91 else '100k'),
        ('res_h',260 if kind==91 else 190,146,286,'40k' if kind==91 else '100k'),
        ('opamp',190,72,False),('wire',130,85,190,85),('wire',190,58,190,85),
        ('wire',252,101,286,101),('wire',286,58,286,146),
        ('wire',190,109,190,126),('wire',190,126,170,126),('wire',170,126,170,146),
        ('wire',24,206,286,206),('gnd',130,206),('lbl','Teste',6,142),('vo',304,110,184,'Vo')]
    ops += [('term',24,158,'t')]
    if kind==92:ops += [('wire',100,146,240,146)]
    return ops
CIRCUITS['p10_91']=_oscillator(91)
CIRCUITS['p10_92']=_oscillator(92)
for _id in ('p10_91',):
    CIRCUITS[_id]=[(op[0],op[1],168,op[3],op[4]) if op[0] in ('ind_h','cap_h','res_h') and op[2]==146
        else ('res_v',170,168,206,'10k') if op==('res_v',170,146,206,'10k')
        else ('wire',170,126,170,168) if op==('wire',170,126,170,146)
        else ('wire',286,58,286,168) if op==('wire',286,58,286,146) else op for op in CIRCUITS[_id]]
CIRCUITS['p10_92']=[('ind_v',160,146,206,'10uH') if op==('ind_v',100,146,206,'10uH')
    else ('cap_v',210,146,206,'2nF') if op==('cap_v',170,146,206,'2nF')
    else ('res_v',278,146,206,'10k') if op==('res_v',240,146,206,'10k')
    else ('res_h',174,128,286,'100k') if op==('res_h',190,146,286,'100k')
    else ('wire',160,146,278,146) if op==('wire',100,146,240,146)
    else ('wire',174,128,174,146) if op==('wire',170,126,170,146)
    else ('wire',190,126,174,128) if op==('wire',190,126,170,126) else op for op in CIRCUITS['p10_92']]
CIRCUITS['p10_89']=[('vsrc_v',292,90,206,'10V'),('res_h',16,90,70,'10k'),
    ('res_h',70,90,124,'20k'),('res_h',124,90,180,'30k'),('cap_h',180,90,236,'10nF'),
    ('res_h',236,90,292,'40k'),('opamp',60,120,False),('opamp',186,120,False),
    ('wire',16,90,16,206),('wire',70,90,70,110),('wire',70,110,60,133),
    ('wire',124,90,124,149),('wire',122,149,124,149),
    ('wire',180,90,180,110),('wire',180,110,186,133),
    ('wire',248,149,248,110),('wire',248,110,236,110),('wire',236,90,236,192),
    ('wire',60,157,60,192),('wire',60,192,236,192),
    ('wire',186,157,186,206),('wire',16,206,292,206),('gnd',130,206)]


STATEMENTS = {
    2: ["Use a Figura 10.51 e formule um exemplo", "de analise nodal; determine Vo."],
    3: ["Determine vo(t) usando analise nodal."],
    4: ["Determine vo(t) no circuito com fonte", "dependente da Figura 10.53."],
    5: ["Determine vo(t) no circuito da Figura 10.54."],
    6: ["Use analise nodal para obter Vx."],
    8: ["Use analise nodal para determinar io."],
    9: ["Determine vo(t) pelo metodo dos nos."],
    10: ["Para w=2000 rad/s, determine vo(t)."],
    11: ["Use analise nodal e determine io."],
    12: ["Problema de projeto sobre analise nodal", "em uma rede RLC com fonte dependente."],
    13: ["Calcule Vx no circuito da Figura 10.62."],
    14: ["Determine as tensoes nodais da Figura 10.63."],
    15: ["Determine a corrente I usando analise nodal."],
    16: ["Determine Vx usando analise nodal."],
    17: ["Determine a corrente do ramo de 2 ohm."],
    18: ["Determine Vo no circuito da Figura 10.67."],
    19: ["Determine Vo no circuito da Figura 10.68."],
    20: ["Deduza A e fase de vo=A sen(wt+fase)", "para a rede R-(L paralelo C)."],
    21: ["Obtenha Vo/Vi para w=0, w=infinito", "e w^2=1/(LC), nos dois circuitos."],
    22: ["Determine a funcao de transferencia Vo/Vs."],
    23: ["Usando analise nodal, obtenha V/Vs."],
    24: ["Formule um exemplo que explique o metodo", "das correntes de malha em CA."],
    25: ["Determine io usando analise de malhas."],
    27: ["Determine I1 e I2 por analise de malhas."],
    28: ["Determine as correntes de malha i1 e i2."],
    29: ["Problema de projeto: formule e resolva", "uma rede CA de duas malhas."],
    30: ["Use malhas para determinar vo."],
    31: ["Determine Io por analise de malhas."],
    32: ["Determine Vo e Io por analise de malhas."],
    33: ["Refaca o Problema 10.15 usando malhas."],
    34: ["Refaca o Exemplo 10.10 usando malhas."],
    35: ["Refaca o Problema pratico 10.10", "usando analise de malhas."],
    36: ["Calcule Vo usando analise de malhas."],
    37: ["Determine I1, I2 e I3 por malhas."],
    38: ["Use malhas e obtenha Io."],
    39: ["Determine I1, I2, I3 e Ix."],
    40: ["Determine io usando superposicao."],
    41: ["Com vs=6cos2t+4sen4t V, obtenha vo."],
    42: ["Formule um exemplo para explicar", "superposicao em regime senoidal."],
    43: ["Determine ix pelo principio da superposicao."],
    44: ["Com fontes em 2 e 6 rad/s, obtenha vx."],
    45: ["Determine i(t) usando superposicao."],
    46: ["Determine vo(t) usando superposicao."],
    47: ["Determine io usando superposicao."],
    48: ["Determine io usando superposicao."],
    49: ["Use transformacao de fontes para achar i."],
    50: ["Formule um exemplo de transformacao", "de fontes na rede RLC mostrada."],
    51: ["Resolva o Problema 10.42 por", "transformacao de fontes."],
    52: ["Use transformacao de fontes para obter Ix."],
    53: ["Determine Vo por transformacao de fontes."],
    54: ["Refaca o Problema 10.7 usando", "transformacao de fontes."],
    55: ["Obtenha Thevenin e Norton em a-b", "para os dois circuitos da figura."],
    56: ["Obtenha Thevenin e Norton em a-b", "para os dois circuitos da figura."],
    57: ["Formule um exemplo sobre equivalentes", "de Thevenin e Norton em CA."],
    58: ["Determine Thevenin nos terminais a-b."],
    59: ["Calcule a impedancia de saida."],
    60: ["Determine Thevenin visto de a-b e c-d."],
    61: ["Determine Thevenin nos terminais a-b."],
    62: ["Use Thevenin para determinar vo."],
    63: ["Obtenha Norton nos terminais a-b."],
    64: ["Obtenha Norton nos terminais a-b."],
    65: ["Formule um exemplo para explicar Norton."],
    66: ["Com w=10 rad/s, obtenha Thevenin e", "Norton nos terminais a-b."],
    67: ["Determine Thevenin e Norton entre a-b."],
    68: ["Determine Thevenin nos terminais a-b."],
    69: ["Para o diferenciador ideal, obtenha Vo/Vs", "e vo(t) quando w=1/(RC)."],
    70: ["Formule um exemplo de AOP em circuito CA."],
    71: ["Determine vo no circuito com AOP."],
    72: ["Se vs=4cos(10^4 t), calcule io(t)."],
    73: ["Calcule a impedancia de entrada Zent."],
    74: ["Obtenha Av=Vo/Vs e seus limites."],
    75: ["Determine ganho de malha fechada e fase."],
    76: ["Determine Vo e Io no circuito com AOP."],
    77: ["Calcule o ganho Vo/Vs com realimentacao."],
    78: ["Determine vo(t) no circuito com AOP."],
    79: ["Determine vo(t) para os dois AOPs."],
    80: ["Para vs=4cos(1000t-60deg), obtenha vo."],
    81: ["Use analise CA para determinar Vo", "com w=1 rad/s."],
    82: ["Resolva novamente o Problema 10.19."],
    83: ["Para is=2cos(1000t) A, determine vo(t)."],
    84: ["Determine Vo no circuito da Figura 10.126."],
    85: ["Formule e resolva um exemplo de analise", "CA para a Figura 10.127."],
    86: ["Determine V1, V2 e V3."],
    87: ["Determine V1, V2 e V3."],
    88: ["Determine vo e io no circuito acoplado."],
    89: ["Demonstre a impedancia do simulador", "de indutancia com AOPs."],
    90: ["Demonstre a frequencia e o ganho", "necessario da ponte de Wien."],
    91: ["No oscilador, determine a frequencia", "e o menor R que permite oscilacao."],
    92: ["Calcule Ro minimo e a frequencia", "de oscilacao do AOP ideal."],
    93: ["Demonstre a frequencia do oscilador", "Colpitts da Figura 10.135."],
    94: ["Projete um oscilador Colpitts de 50 kHz."],
    95: ["Demonstre a frequencia do oscilador", "Hartley da Figura 10.136."],
    96: ["Demonstre V2/Vo, ache fo e a relacao", "entre R1 e R2 para oscilacao."],
}


SOLUTIONS = {
    2: ["Exemplo: converta cada ramo em Y.", "KCL: (V-4)/2+V/(-j5)+V/(j4)=0.",
        "Isole V pela soma das admitancias.", "= O procedimento vale para novos valores."],
    12: ["Escolha a referencia e nomeie os nos.", "Troque L e C por jwL e 1/(jwC).",
         "Inclua a fonte dependente na KCL.", "= Resolva o sistema complexo obtido."],
    20: ["Zp=(jwL)/(1-w^2LC).", "H=Vo/Vs=Zp/(R+Zp).",
         "A=Vm|H|; fase=arg(H).", "= vo=A sen(wt+fase)."],
    21: ["(a) H=ZC/(R+jwL+ZC).", "(b) H=ZL/(R+ZC+ZL).",
         "Substitua w=0, infinito e 1/sqrt(LC).", "= Os limites saem diretamente de H."],
    22: ["Zp=(R2+jwL)||1/(jwC).", "Vo/Vs=Zp/(R1+Zp).",
         "Expanda em potencias de jw.", "= H(s)=Zp/(R1+Zp), s=jw."],
    23: ["Y1=1/(jwL+1/(jwC)); Y2=jwC.", "KCL: (V-Vs)/R+V(Y1+Y2)=0.",
         "V/Vs=1/[1+R(Y1+Y2)].", "= Simplifique para a forma pedida."],
    24: ["Defina I1 e I2 no sentido horario.", "Escreva queda propria e termo mutuo.",
         "[Z11 -Z12;-Z12 Z22][I]=[V].", "= Resolva o sistema complexo 2x2."],
    29: ["Escolha valores para R1,R2,R3 e X.", "Escreva as duas equacoes de malha.",
         "O ramo comum entra com -Zcomum.", "= Problema de projeto: ha varias respostas."],
    41: ["Separe as frequencias 2 e 4 rad/s.", "Em cada w, Zc=1/(jwC) e H=R/(R+Zc).",
         "Calcule uma parcela por fonte.", "= Some as duas senoides no tempo."],
    42: ["Anule fontes independentes uma por vez.", "Fonte V anulada vira curto; I vira aberto.",
         "Calcule a contribuicao de cada fonte.", "= Some fasores apenas de mesma frequencia."],
    44: ["As fontes possuem frequencias diferentes.", "Resolva w=2 com apenas vs ativa.",
         "Resolva w=6 com apenas is ativa.", "= Converta cada parcela ao tempo e some."],
    45: ["Resolva separadamente w=10 e w=4.", "Para cada fonte, ZL=jw(0.3).",
         "Use I=(V1-V2)/(20+jwL).", "= Some as correntes no dominio do tempo."],
    46: ["Ha parcelas em w=3, w=2 e DC.", "Em cada CA use Zc=1/(jwC), Zl=jwL.",
         "Em DC: C aberto e L em curto.", "= vo(t) e a soma das tres parcelas."],
    47: ["Separe w=1, w=3 e a fonte de 24 V.", "Anule as demais fontes em cada etapa.",
         "Calcule io no resistor de 4 ohm.", "= Some as tres respostas no tempo."],
    48: ["Separe w=2000 e as fontes DC.", "Em CA: fonte 24 V vira curto.",
         "Em DC: C abre e L entra em curto.", "= io e a soma das duas parcelas."],
    50: ["Transforme Vs-R1 em Norton: Vs/R1.", "Combine fontes/cargas paralelas.",
         "Retorne a Thevenin antes de L e R2.", "= Vo sai por divisor de impedancias."],
    55: ["Abra a carga: Vth=Vab.", "Anule fontes e aplique fonte-teste.",
         "Zth=Vteste/Iteste; In=Vth/Zth.", "= Repita o processo para (a) e (b)."],
    56: ["Calcule Vab com o porto aberto.", "Anule a fonte independente.",
         "Reduza a rede para obter Zth.", "= Norton: In=Vth/Zth, Zn=Zth."],
    57: ["Exemplo: ache Vab com o porto aberto.", "Depois anule Vs e aplique 1 A em a-b.",
         "Zth=Vab/1A; In=Vth/Zth.", "= Thevenin e Norton sao equivalentes."],
    59: ["Aplique uma fonte-teste no porto.", "Mantenha a fonte dependente ativa.",
         "Escreva Vo e a KCL do no interno.", "= Zout=Vteste/Iteste=6+j38 ohm."],
    60: ["Para cada par, abra o porto e ache Vth.", "Anule 20V e 4A para calcular Zth.",
         "Use uma fonte-teste se houver acoplamento.", "= Repita para a-b e para c-d."],
    61: ["Mantenha a fonte 1.5Ix ativa.", "Ache Vab em circuito aberto.",
         "Aplique 1 A de teste em a-b.", "= Zth=Vteste/1A; In=Vth/Zth."],
    65: ["Defina o porto e calcule Vab aberto.", "Anule apenas fontes independentes.",
         "Use 1 A de teste para obter Zth.", "= In=Vth/Zth e Zn=Zth."],
    68: ["Ache Vab com a carga removida.", "Fontes dependentes permanecem ativas.",
         "Use uma fonte-teste no porto a-b.", "= Vth=Vab e Zth=Vteste/Iteste."],
    69: ["No AOP ideal, V-=V+=0 e entrada nula.", "Ic=jwC Vs; Vo=-R Ic.",
         "Vo/Vs=-jwRC.", "= Para w=1/RC: vo=Vm cos(wt)."],
    70: ["Use V-=V+ e correntes de entrada nulas.", "Escreva KCL no no inversor.",
         "Substitua Zc=1/(jwC).", "= Isole H(jw)=Vo/Vs."],
    71: ["O AOP e nao inversor.", "Zf=10k||1/(jw0.5uF).",
         "H=1+Zf/2k, com w=2 rad/s.", "= Vo=H Vs; converta ao tempo."],
    72: ["O AOP e seguidor: Vo e a tensao no C.", "H=Zc/(50k+Zc), w=10^4.",
         "Io=Vo/100k.", "= Calcule modulo/fase e volte ao tempo."],
    73: ["Seguidor ideal: Vo e a tensao em C2.", "Escreva KCL nos dois nos RC.",
         "Is=(Vs-V1)/R1+jwC1(Vs-Vo).", "= Zent=Vs/Is apos resolver Vo."],
    74: ["AOP inversor: Av=-Zf/Zin.", "Zin=R1+1/(jwC1).",
         "Zf=R2+1/(jwC2).", "= Avalie w=0, infinito e os dois cortes."],
    75: ["A entrada + recebe o divisor C1-C2-R2.", "A malha - define ganho 1+R1/R4.",
         "Combine as duas funcoes em H(jw).", "= Avalie com w=2000 rad/s."],
    76: ["O AOP e seguidor; V+=Vo.", "Resolva a rede RC de entrada por KCL.",
         "Io=(Ventrada-Vo)/20k.", "= Use fasores e informe Vo e Io."],
    77: ["A entrada + e um passa-baixas R1-C1.", "A realimentacao usa R3 e R2||C2.",
         "Use V-=V+ e KCL no no inversor.", "= Simplifique H(jw)=Vo/Vs."],
    78: ["Resolva a rede RC que alimenta V+.", "O AOP e nao inversor: 1+40k/20k=3.",
         "Inclua a realimentacao de 20k na KCL.", "= Obtenha o fasor Vo e volte ao tempo."],
    79: ["Primeiro AOP: H1=-Zf/Zin.", "Segundo AOP: H2=-40k/Zc.",
         "Htotal=H1 H2, com w=1000.", "= Vo=Htotal(5/_0) e volte ao tempo."],
    80: ["Use V-=V+=0 em cada AOP.", "Escreva as duas KCLs acopladas.",
         "Substitua Zc=1/(jwC), w=1000.", "= Resolva Vo e converta ao tempo."],
    85: ["Nomeie os tres nos essenciais.", "Troque XL e XC por jX e -jX.",
         "Inclua 0.25Vx na KCL superior.", "= Resolva o sistema complexo nodal."],
    89: ["Aplique Vin e use V-=V+ nos AOPs.", "Elimine os nos internos pelas KCLs.",
         "Zent=Vin/Iin=jwLeq.", "= Leq=(R1 R3 R4/R2) C."],
    90: ["A ponte equilibra quando wRC=1.", "Logo fo=1/(2piRC).",
         "Na frequencia, a rede atenua por 3.", "= O amplificador deve ter Av=3."],
    91: ["fo=1/[2pi sqrt(LC)].", "L=0.4mH e C=2nF.",
         "fo=177.94 kHz, aprox. 180 kHz.", "= A condicao de ganho fornece R minimo."],
    92: ["O tanque paralelo fixa fo=1/(2pi sqrt(LC)).", "Com L=10uH e C=2nF: fo=1.125MHz.",
         "Aplique Barkhausen para achar o ganho.", "= Isole Ro minimo na realimentacao."],
    93: ["No tanque, CT=C1C2/(C1+C2).", "Imponha parte imaginaria igual a zero.",
         "w0=1/sqrt(L CT).", "= fo=1/[2pi sqrt(L CT)]."],
    94: ["Escolha C1=C2=C; entao CT=C/2.", "Para fo=50kHz, L=1/[(2pi fo)^2 CT].",
         "Exemplo: C=20nF -> CT=10nF.", "= L=1.013mH; ajuste o ganho de partida."],
    95: ["O tanque usa L1+L2 em paralelo com C.", "Imponha a fase de malha igual a zero.",
         "w0=1/sqrt[C(L1+L2)].", "= fo=1/{2pi sqrt[C(L1+L2)]}."],
    96: ["A rede fornece V2/Vo=1/[3+j(wL/R-R/wL)].", "Fase zero exige wL=R.",
         "Logo fo=R/(2piL).", "= Barkhausen: 1+R2/R1=3; R2=2R1."],
}


_DYNAMIC = {1, 7, 26}
_VISUAL_ONLY = {2, 12, 20, 21, 22, 23, 24, 29, 41, 42, 44, 45, 46, 47, 48,
                50, 55, 56, 57, 59, 60, 61, 65, 67, 68, 69, 70, 71, 72, 73, 74,
                75, 76, 77, 78, 79, 80, 85, 89, 90, 91, 92, 93, 94, 95, 96}
_THEVENIN = set(range(55, 69))
_SUPER = set(range(40, 55))
_MESH = set(range(24, 40))
_VOLTAGE_TARGET = {2, 3, 4, 5, 6, 9, 10, 13, 16, 18, 19, 20, 21, 22, 23,
                   30, 32, 36, 41, 44, 46, 51, 53, 54, 62, 71, 76, 78, 79,
                   80, 81, 82, 83, 84, 85, 86, 87, 88}

_OMEGA = {
    3: 4.0, 4: 4.0, 5: 4000.0, 8: 200.0, 9: 1000.0, 10: 2000.0,
    11: 2.0, 20: 1.0, 21: 1.0, 22: 1.0, 23: 1.0, 25: 2.0,
    28: 4.0, 30: 100.0, 40: 4.0, 41: 2.0, 43: 2.0, 44: 2.0,
    45: 10.0, 46: 3.0, 47: 1.0, 48: 2000.0, 49: 200.0,
    63: 200.0, 66: 10.0, 68: 10.0, 71: 2.0, 72: 10000.0,
    73: 5000.0, 75: 2000.0, 78: 400.0, 79: 1000.0, 80: 1000.0,
    83: 1000.0, 88: 4.0,
}

# 10.24 e o unico item sem uma figura numerica fixa.  O exemplo de duas
# malhas continua aberto, mas seus dados-base tambem precisam passar pelo
# mesmo editor escalar dos demais capitulos.
PARAMS = {
    24: [("Vs_V", 120.0), ("Vs_deg", 0.0),
         ("Z1_R", 10.0), ("Z1_X", 5.0),
         ("Z2_R", 20.0), ("Z2_X", -4.0),
         ("Zm_R", 5.0), ("Zm_X", 2.0)],
}


def _subject(number):
    if number in _THEVENIN:
        return "Thevenin AC"
    if number in _SUPER:
        return "Superposicao AC"
    if number in _MESH:
        return "Analise Malhas AC"
    return "Analise Nodal AC"


def _last_component_index(ops):
    kinds = {"res_h", "res_v", "cap_h", "cap_v", "ind_h", "ind_v",
             "imp_h", "imp_v", "vsrc_h", "vsrc_v", "isrc_h", "isrc_v",
             "dvs_h", "dvs_v", "dis_v"}
    candidates = [i for i, op in enumerate(ops) if op[0] in kinds]
    return candidates[-1] if candidates else None


EXERCISES = []
for number in range(1, 97):
    if number in _DYNAMIC:
        continue
    ex_id = "p10_%d" % number
    statement = STATEMENTS[number]
    static = number in _VISUAL_ONLY or ex_id not in CIRCUITS
    exercise = {
        "id": ex_id,
        "title": "Problema 10.%d" % number,
        "subject": _subject(number),
        "priority": 100 + number,
        "source": "Livro, Cap.10, Problema 10.%d" % number,
        "statement": statement,
        "static": static,
    }
    if number in PARAMS:
        exercise["params"] = PARAMS[number]
    if static:
        solution = list(SOLUTIONS.get(number, [
            "1) Converta todas as fontes em fasores.",
            "2) Use ZL=jwL e ZC=1/(jwC).",
            "3) Monte e resolva as equacoes complexas.",
            "= A figura permanece editavel para novos dados.",
        ]))
        if number in _VISUAL_ONLY:
            solution.append("# Ao editar, substitua os novos dados nas formulas.")
        exercise["solution"] = solution
    if ex_id in CIRCUITS:
        engine = {"omega": _OMEGA.get(number, 1.0)}
        if number in _VISUAL_ONLY:
            engine["visual_only"] = True
        elif number in _THEVENIN:
            # Figuras com a-b possuem terminais; problemas de carga (62)
            # usam a rota nodal para entregar vo diretamente.
            if number != 62 and any(op[0] == "term" for op in CIRCUITS[ex_id]):
                engine["port_labels"] = ["a", "b"]
            else:
                engine["force_nodal"] = True
        elif number in _MESH:
            # A resposta continua no menu de malhas, mas a rota nodal e mais
            # geral para supermalhas e fontes de corrente.
            engine["force_nodal"] = True
        elif number in _SUPER:
            engine["force_nodal"] = True
        target = _last_component_index(CIRCUITS[ex_id])
        if target is not None and number not in _THEVENIN:
            engine["target_op_index"] = target
            if number in _VOLTAGE_TARGET:
                engine["flags2"] = 2
        exercise["engine"] = engine
    elif number in PARAMS:
        exercise["engine"] = {"visual_only": True}
    EXERCISES.append(exercise)
