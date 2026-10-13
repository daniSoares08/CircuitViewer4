"""Capitulo 10 - Analise em regime estacionario senoidal."""

SUBJECTS = ["Analise Nodal AC", "Analise Malhas AC", "Thevenin AC"]

CIRCUITS = {
    "p10_1": [
        ("vsrc_v", 40, 78, 194, "2V"),
        ("res_h", 40, 78, 115, "1"),
        ("wire", 115, 78, 282, 78),
        ("cap_v", 135, 78, 194, "1F"),
        ("ind_v", 205, 78, 194, "1H"),
        ("res_v", 275, 78, 194, "1"),
        ("wire", 40, 194, 282, 194),
        ("arr_h", 55, 60, 105, "i", True),
        ("gnd", 160, 194),
    ],
    "p10_7": [
        ("vsrc_v", 42, 78, 194, "120/_-15V"),
        ("res_h", 42, 78, 112, "40"),
        ("imp_h", 112, 78, 185, "j20"),
        ("wire", 185, 78, 282, 78),
        ("isrc_v", 200, 78, 194, "6/_30A", False),
        ("imp_v", 240, 78, 194, "-j30"),
        ("res_v", 280, 78, 194, "50"),
        ("wire", 42, 194, 282, 194),
        ("lbl", "V", 188, 60),
        ("gnd", 200, 194),
    ],
    "p10_26": [
        ("vsrc_v", 40, 78, 192, "10V"),
        ("res_h", 40, 78, 125, "2k"),
        ("wire", 125, 78, 155, 78),
        ("ind_v", 155, 78, 192, "0.4H"),
        ("cap_h", 155, 78, 250, "1uF"),
        ("vsrc_v", 250, 78, 192, "20/_-90V"),
        ("wire", 40, 192, 250, 192),
        ("arr_v", 137, 100, 155, "io", False),
        ("gnd", 150, 192),
    ],
}

EXERCISES = [
    {
        "id": "p10_1", "title": "Problema 10.1",
        "subject": "Analise Nodal AC", "priority": 10,
        "source": "Livro, Cap.10, Problema 10.1",
        "statement": [
            "Determine i(t) no circuito mostrado.",
            "A fonte e 2 cos(10t) V.",
        ],
        "engine": {"omega": 10.0, "target_op_index": 1},
        "expected": {"i_mag": 1.9704, "i_deg": 5.65},
    },
    {
        "id": "p10_7", "title": "Problema 10.7",
        "subject": "Analise Nodal AC", "priority": 11,
        "source": "Livro, Cap.10, Problema 10.7",
        "statement": ["Use analise nodal para determinar V."],
        "engine": {"omega": 1.0, "target_op_index": 6, "flags2": 2},
        "expected": {"v_mag": 124.08, "v_deg": -154.0},
    },
    {
        "id": "p10_26", "title": "Problema 10.26",
        "subject": "Analise Malhas AC", "priority": 12,
        "source": "Livro, Cap.10, Problema 10.26",
        "statement": [
            "Use analise de malhas para determinar",
            "io no circuito. omega = 1000 rad/s.",
        ],
        "engine": {"omega": 1000.0, "target_op_index": 3,
                   "force_nodal": True},
        "expected": {"i_mag": 0.039528, "i_deg": -18.435},
    },
]
