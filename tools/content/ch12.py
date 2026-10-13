"""Capitulo 12 - Circuitos trifasicos."""

SUBJECTS = ["Trifasico"]


def _box(x1, y, x2):
    return [
        ("line", x1, y - 8, x2, y - 8), ("line", x2, y - 8, x2, y + 8),
        ("line", x2, y + 8, x1, y + 8), ("line", x1, y + 8, x1, y - 8),
    ]


_P12_14 = [
    ("lbl", "Fonte Y", 30, 57), ("lbl", "Carga delta", 215, 57),
    ("lbl", "a", 30, 78), ("lbl", "b", 30, 128), ("lbl", "c", 30, 178),
    ("line", 42, 82, 170, 82), ("line", 42, 132, 170, 132),
    ("line", 42, 182, 170, 182),
] + _box(88, 82, 125) + _box(88, 132, 125) + _box(88, 182, 125) + [
    ("lbl", "1+j2", 88, 64), ("lbl", "1+j2", 88, 114),
    ("lbl", "1+j2", 88, 164),
    ("line", 170, 82, 255, 132), ("line", 255, 132, 170, 182),
    ("line", 170, 182, 170, 82),
    ("lbl", "12+j12", 205, 91), ("lbl", "12+j12", 205, 165),
    ("lbl", "12+j12", 112, 145),
]

_P12_7 = [
    ("lbl", "Fonte Y", 30, 57), ("lbl", "Carga Y", 230, 57),
    ("lbl", "a", 30, 78), ("lbl", "b", 30, 128), ("lbl", "c", 30, 178),
    ("line", 42, 82, 210, 82), ("line", 42, 132, 210, 132),
    ("line", 42, 182, 210, 182),
    ("line", 210, 82, 270, 132), ("line", 210, 132, 270, 132),
    ("line", 210, 182, 270, 132),
    ("lbl", "6-j8", 224, 88), ("lbl", "6-j8", 215, 120),
    ("lbl", "6-j8", 224, 171), ("lbl", "N", 277, 128),
]

_P12_25 = [
    ("lbl", "Fonte delta", 28, 57), ("lbl", "Carga Y", 225, 57),
    ("lbl", "a", 28, 78), ("lbl", "b", 28, 128), ("lbl", "c", 28, 178),
    ("line", 42, 82, 205, 82), ("line", 42, 132, 205, 132),
    ("line", 42, 182, 205, 182),
] + _box(90, 82, 127) + _box(90, 132, 127) + _box(90, 182, 127) + [
    ("lbl", "3+j2", 91, 64), ("lbl", "3+j2", 91, 114),
    ("lbl", "3+j2", 91, 164),
    ("line", 205, 82, 260, 132), ("line", 205, 132, 260, 132),
    ("line", 205, 182, 260, 132),
    ("lbl", "10-j8", 220, 88), ("lbl", "10-j8", 210, 120),
    ("lbl", "10-j8", 220, 171), ("lbl", "N", 267, 128),
]

CIRCUITS = {"p12_7": _P12_7, "p12_14": _P12_14, "p12_25": _P12_25}

EXERCISES = [
    {
        "id": "p12_7", "title": "Problema 12.7",
        "subject": "Trifasico", "priority": 10,
        "source": "Livro, Cap.12, Problema 12.7",
        "statement": ["Fonte Y equilibrada de 440 V/fase", "alimenta carga Y de 6-j8 ohm/fase.", "Determine Ia, Ib e Ic."],
        "engine": {"profile": 4, "diagram_only": True},
        "params": [
            ("Van_V", 440.0), ("Van_deg", 0.0),
            ("Zlin_R", 0.0), ("Zlin_X", 0.0),
            ("ZY_R", 6.0), ("ZY_X", -8.0),
        ],
        "expected": {"ia_mag": 44.0, "ia_deg": 53.13},
    },
    {
        "id": "p12_14", "title": "Problema 12.14",
        "subject": "Trifasico", "priority": 11,
        "source": "Livro, Cap.12, Problema 12.14",
        "statement": ["Obtenha Ia, Ib e Ic para a fonte Y,", "linhas 1+j2 e carga delta 12+j12."],
        "engine": {"profile": 2, "diagram_only": True},
        "params": [
            ("Van_V", 100.0), ("Van_deg", 0.0),
            ("Zlin_R", 1.0), ("Zlin_X", 2.0),
            ("Zdel_R", 12.0), ("Zdel_X", 12.0),
        ],
    },
    {
        "id": "p12_25", "title": "Problema 12.25",
        "subject": "Trifasico", "priority": 12,
        "source": "Livro, Cap.12, Problema 12.25",
        "statement": ["Fonte delta: Vab=440/_10 V.", "Linhas 3+j2; carga Y 10-j8 ohm.", "Determine as correntes de linha."],
        "engine": {"profile": 3, "diagram_only": True},
        "params": [
            ("Vab_V", 440.0), ("Vab_deg", 10.0),
            ("Zlin_R", 3.0), ("Zlin_X", 2.0),
            ("ZY_R", 10.0), ("ZY_X", -8.0),
        ],
    },
]
