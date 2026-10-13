#!/usr/bin/env python3
"""Official CircuitViewer4 content routing (new catalog only)."""

CID_IMPEDANCIA_AC = 0
CID_NODAL_AC = 1
CID_MALHAS_AC = 2
CID_SUPERPOSICAO_AC = 3
CID_THEVENIN_AC = 4
CID_POTENCIA_AC = 5
CID_MAX_POTENCIA_AC = 6
CID_TRIFASICO = 7
CID_CIRCUITOS_CH9 = 8
CID_STATIC = 0xFF

# cid, subject key, calculator menu title, chapter, section
CONTENT_META = [
    (CID_IMPEDANCIA_AC, "Impedancia AC", "Impedancia e Fasores (Cap.9)", 9, 1),
    (CID_NODAL_AC, "Analise Nodal AC", "Analise Nodal AC (Cap.10)", 10, 1),
    (CID_MALHAS_AC, "Analise Malhas AC", "Analise de Malhas AC (Cap.10)", 10, 2),
    (CID_SUPERPOSICAO_AC, "Superposicao AC", "Superposicao AC (Cap.10)", 10, 3),
    (CID_THEVENIN_AC, "Thevenin AC", "Thevenin AC (Cap.10)", 10, 4),
    (CID_POTENCIA_AC, "Potencia AC", "Potencia em CA (Cap.11)", 11, 1),
    (CID_MAX_POTENCIA_AC, "Max Potencia AC", "Max. Potencia CA (Cap.11)", 11, 2),
    (CID_TRIFASICO, "Trifasico", "Circuitos Trifasicos (Cap.12)", 12, 1),
    (CID_CIRCUITOS_CH9, "Circuitos AC Cap9", "Circuitos em Fasores (Cap.9)", 9, 2),
]
SUBJECT_TO_META = {subject: (cid, title, chapter, section)
                   for cid, subject, title, chapter, section in CONTENT_META}


def resolve_content(ex):
    try:
        cid, title, chapter, section = SUBJECT_TO_META[ex["subject"]]
    except KeyError:
        raise KeyError("no CV4 content mapping for subject %r (id=%s)" %
                       (ex.get("subject"), ex.get("id")))
    return cid, ex.get("chapter", chapter), ex.get("section", section), title


def menu_sort_key(cid, chapter, section):
    return chapter, section, cid
