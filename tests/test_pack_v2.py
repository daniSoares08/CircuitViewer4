#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Round-trip + byte-alignment test for tools/pack_v2.py, mirroring
CircuitViewer3's proven "simulate the C parser in Python" technique."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import pack_v2 as pk  # noqa: E402


def test_single_template_single_exercise():
    template = {
        "n_nodes": 4,
        "comps": [
            {"kind": 0, "na": 1, "nb": 2, "deflt": 10.0},
            {"kind": 0, "na": 1, "nb": 2, "deflt": 10.0},
            {"kind": 0, "na": 2, "nb": 0, "deflt": 10.0},
            {"kind": 0, "na": 2, "nb": 3, "deflt": 4.0},
            {"kind": 1, "na": 1, "nb": 0, "deflt": 12.0},
            {"kind": 1, "na": 3, "nb": 0, "deflt": 20.0},
        ],
        "ops": [
            {"opcode": 9, "a": 48, "b": 94, "c": 170, "d": 0, "reg": 4, "label": ""},
            {"opcode": 3, "a": 48, "b": 94, "c": 118, "d": 0, "reg": 0, "label": ""},
            {"opcode": 19, "a": 108, "b": 72, "c": 0, "d": 0, "reg": 0xFF, "label": "V1"},
        ],
        "meshes": [[(0, 1), (3, -1)], [(1, 1), (2, -1), (4, 1)]],
        "port_a": 1, "port_b": 3,
    }
    exercise = {
        "template_id": 0,
        "content_id": 1,  # CID_NODAL_AC
        "chapter": 10, "section": 1,
        "val_overrides": [(4, 12.0, -3.0)],
        "flag_overrides": [(5, 1)],
        "params": [165.0, 120.0],
        "title": "Prova01 Q3",
        "statement": [
            {"title": "Enunciado", "subtitle": "", "result": "", "result_y": 0,
             "lines": [(2, 62, 1, "Use analise nodal..."),
                       (2, 82, 1, "para achar V1.")]},
        ],
        "tail": [],
    }

    t_bytes = pk.encode_template(template)
    e_bytes = pk.encode_exercise(exercise)
    payload = pk.build_chunk_payload([t_bytes], [e_bytes])

    n_t, n_e = pk.sim_parse_chunk(payload)
    assert n_t == 1 and n_e == 1, (n_t, n_e)
    print("ok   single template+exercise: parse-sim landed exactly, "
          "payload=%d bytes" % len(payload))


def test_many_blocks_alignment():
    """Several templates/exercises of varying shapes - the real regression
    risk (a fixed-size miscalculation only shows up past the first block,
    exactly like the v3 lesson - see pack_v2.py's docstring)."""
    templates = []
    for n_ops in (0, 1, 3, 5):
        t = {
            "n_nodes": 3, "comps": [{"kind": 0, "na": 1, "nb": 0, "deflt": 5.0}],
            "ops": [{"opcode": 3, "a": i, "b": i, "c": i, "d": 0, "reg": 0, "label": ""}
                    for i in range(n_ops)],
            "meshes": [[(0, 1)]] if n_ops == 5 else [],
            "port_a": 1, "port_b": 0,
        }
        templates.append(pk.encode_template(t))

    exercises = []
    for i, n_lines in enumerate((0, 1, 4, 8)):
        e = {
            "template_id": i % len(templates),
            "content_id": 0xFF if i % 2 else 2,
            "chapter": i, "section": i,
            "val_overrides": [(0, 1.0 * i)] if i else [],
            "flag_overrides": [],
            "title": "Ex %d" % i,
            "statement": [
                {"title": "Enunciado", "subtitle": "", "result": "", "result_y": 0,
                 "lines": [(2, 62 + 20 * j, 1, "linha %d" % j) for j in range(n_lines)]},
            ],
            "tail": [
                {"title": "Resultado", "subtitle": "Final", "result": "x = 1",
                 "result_y": 150, "lines": [(2, 62, 5, "resposta")]},
            ] if i % 2 == 0 else [],
        }
        exercises.append(pk.encode_exercise(e))

    payload = pk.build_chunk_payload(templates, exercises)
    n_t, n_e = pk.sim_parse_chunk(payload)
    assert n_t == len(templates) and n_e == len(exercises)
    print("ok   %d templates + %d exercises, all blocks byte-aligned "
          "(payload=%d bytes)" % (n_t, n_e, len(payload)))


if __name__ == "__main__":
    test_single_template_single_exercise()
    test_many_blocks_alignment()
    print("\nALL OK")
