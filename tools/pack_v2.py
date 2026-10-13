#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""CV4DATA AppVar v2 binary packing - see .ai-tasks/spec_appvar_v2.md.
Uses magic+offset tables+blocks for templates and exercises.

CRITICAL (see memory: a v3 bug had the C loader advance 9 bytes instead of
10 per op - only surfaced after multiple pages, and only a byte-exact
simulator caught it before hardware). `sim_parse_chunk()` below replays the
C side's exact pointer arithmetic in Python and asserts every block's parse
ends exactly on the next stored offset - run it on every chunk before ever
trusting the bytes.
"""

import struct

MAGIC = b"CV4A"
# v2: templates carry `omega` (rad/s), every component carries an imaginary
# default and exercises carry editable scalar parameters.
VERSION = 2
LAYOUT_REVISION = 3


def _cstr(s):
    if s is None:
        s = ""
    if "\x00" in s:
        raise ValueError("NUL in string %r" % s)
    return s.encode("ascii", "strict") + b"\x00"


def _u8(v):
    if not 0 <= v <= 255:
        raise ValueError("u8 out of range: %r" % v)
    return struct.pack("<B", v)


def _i8(v):
    if not -128 <= v <= 127:
        raise ValueError("i8 out of range: %r" % v)
    return struct.pack("<b", v)


def _u16(v):
    if not 0 <= v <= 65535:
        raise ValueError("u16 out of range: %r" % v)
    return struct.pack("<H", v)


def _i16(v):
    if not -32768 <= v <= 32767:
        raise ValueError("i16 out of range: %r" % v)
    return struct.pack("<h", v)


def _f32(v):
    return struct.pack("<f", float(v))


NONE8 = 0xFF
NONE16 = 0xFFFF


def encode_template(t):
    """t: dict with n_nodes, comps=[{kind,na,nb,ctrl,ctrl_a,ctrl_b,deflt,flags}],
    ops=[{opcode,a,b,c,d,flag,reg,label}],
    meshes=[[(elem,sign),...],...], port_a, port_b, flags2."""
    out = bytearray()
    out += _u8(t["n_nodes"])
    # Angular frequency of this circuit, rad/s. ZERO means DC and selects the
    # original real solver path; nonzero selects phasor analysis. Stored per
    # template because frequency is a property of the circuit, not of any one
    # component - and because that is what makes it separately editable.
    out += _f32(t.get("omega", 0.0))
    comps = t["comps"]
    out += _u8(len(comps))
    for c in comps:
        out += _u8(c["kind"])
        out += _u8(c["na"])
        out += _u8(c["nb"])
        out += _u8(c.get("ctrl", NONE8))
        out += _u8(c.get("ctrl_a", 0))
        out += _u8(c.get("ctrl_b", 0))
        out += _f32(c["deflt"])
        out += _f32(c.get("deflt_im", 0.0))   # phasor "j" part; 0 for all DC
        out += _u8(c.get("flags", 0))
    ops = t["ops"]
    out += _u8(len(ops))
    for op in ops:
        out += _u8(op["opcode"])
        out += _i16(op["a"])
        out += _i16(op["b"])
        out += _i16(op["c"])
        out += _i16(op["d"])
        out += _u8(op.get("flag", 0))
        out += _u8(op.get("reg", NONE8))
        out += _cstr(op.get("label", ""))
    meshes = t.get("meshes", [])
    out += _u8(len(meshes))
    for mesh in meshes:
        out += _u8(len(mesh))
        for elem, sign in mesh:
            out += _u8(elem)
            out += _i8(sign)
    out += _u8(t.get("port_a", NONE8))
    out += _u8(t.get("port_b", NONE8))
    out += _u8(t.get("flags2", 0))
    return bytes(out)


def _page_block(page):
    out = bytearray()
    out += _cstr(page.get("title", ""))
    out += _cstr(page.get("subtitle", ""))
    out += _cstr(page.get("result", ""))
    out += _u8(page.get("result_y", 0))
    lines = page.get("lines", [])
    out += _u8(len(lines))
    for (x, y, color, text) in lines:
        out += _i16(x)
        out += _i16(y)
        out += _u8(color)
        out += _cstr(text)
    return bytes(out)


def encode_exercise(e):
    """e: dict with template_id(int|None), content_id(int|0xFF),
    chapter,section, val_overrides=[(idx,re,im)], flag_overrides=[(idx,flags)],
    target(0xFF default), params=[float|{name,value}...], title,
    statement=[page...],
    tail=[page...] (optional authored initial resolution; after an edit the
    live narrator selected by content_id replaces it)."""
    out = bytearray()
    out += _u16(NONE16 if e.get("template_id") is None else e["template_id"])
    out += _u8(e.get("content_id", 0xFF))
    out += _u8(e.get("chapter", 0))
    out += _u8(e.get("section", 0))
    vo = e.get("val_overrides", [])
    out += _u8(len(vo))
    for override in vo:
        idx, val = override[0], override[1]
        imag = override[2] if len(override) > 2 else 0.0
        out += _u8(idx)
        out += _f32(val)
        out += _f32(imag)
    fo = e.get("flag_overrides", [])
    out += _u8(len(fo))
    for idx, fl in fo:
        out += _u8(idx)
        out += _u8(fl)
    out += _u8(e.get("target", 0xFF))
    params = e.get("params", [])
    if len(params) > 64:
        raise ValueError("at most 64 exercise params")
    out += _u8(len(params))
    for index, param in enumerate(params):
        if isinstance(param, dict):
            value = param["value"]
            name = param.get("name", "P%d" % (index + 1))
        elif isinstance(param, (tuple, list)) and len(param) == 2:
            name, value = param
        else:
            value = param
            name = "P%d" % (index + 1)
        if len(str(name)) > 12:
            raise ValueError("parameter name too long: %r" % name)
        out += _f32(value)
        out += _cstr(str(name))
    out += _cstr(e["title"])
    statement = e.get("statement", [])
    out += _u8(len(statement))
    for page in statement:
        out += _page_block(page)
    tail = e.get("tail", [])
    out += _u8(len(tail))
    for page in tail:
        out += _page_block(page)
    live = e.get("live", b"")
    out += _u16(len(live))
    out += live
    return bytes(out)


def build_chunk_payload(templates, exercises):
    """templates/exercises: list of already-ENCODED byte blocks (in the
    order they'll be indexed by template_id/local exercise id)."""
    header_len = 4 + 1 + 1 + 2 + 2 * len(templates) + 2 + 2 * len(exercises)
    pos = header_len
    t_offsets = []
    for t in templates:
        t_offsets.append(pos)
        pos += len(t)
    e_offsets = []
    for e in exercises:
        e_offsets.append(pos)
        pos += len(e)
    if pos >= 65536:
        raise AssertionError("CV4DAT chunk payload too large: %d bytes" % pos)

    payload = bytearray(MAGIC)
    payload += _u8(VERSION)
    payload += _u8(LAYOUT_REVISION)
    payload += _u16(len(templates))
    for off in t_offsets:
        payload += _u16(off)
    payload += _u16(len(exercises))
    for off in e_offsets:
        payload += _u16(off)
    for t in templates:
        payload += t
    for e in exercises:
        payload += e
    return bytes(payload)


# ---------------------------------------------------------------------------
# Byte-exact C-parser simulator (the safety net - see module docstring)
# ---------------------------------------------------------------------------

class ParseSimError(Exception):
    pass


def _sim_cstr(data, pos):
    end = data.index(b"\x00", pos)
    return data[pos:end].decode("ascii"), end + 1


def _sim_template(data, pos, expect_end):
    start = pos
    n_nodes = data[pos]; pos += 1
    pos += 4             # omega f32
    n_comps = data[pos]; pos += 1
    # kind,na,nb,ctrl,ctrl_a,ctrl_b(6) + deflt f32(4) + deflt_im f32(4) + flags(1)
    pos += n_comps * 15
    n_ops = data[pos]; pos += 1
    for _ in range(n_ops):
        pos += 10  # opcode+a,b,c,d+flag
        pos += 1   # reg
        _, pos = _sim_cstr(data, pos)
    n_meshes = data[pos]; pos += 1
    for _ in range(n_meshes):
        ec = data[pos]; pos += 1
        pos += ec * 2
    pos += 3  # port_a, port_b, flags2
    if pos != expect_end:
        raise ParseSimError("template at %d: parsed to %d, expected %d (delta %d)"
                            % (start, pos, expect_end, expect_end - pos))
    return pos


def _sim_page_block(data, pos):
    _, pos = _sim_cstr(data, pos)  # title
    _, pos = _sim_cstr(data, pos)  # subtitle
    _, pos = _sim_cstr(data, pos)  # result
    pos += 1  # result_y
    lc = data[pos]; pos += 1
    for _ in range(lc):
        pos += 5  # x,y,color
        _, pos = _sim_cstr(data, pos)
    return pos


def _sim_exercise(data, pos, expect_end):
    start = pos
    pos += 2  # template_id
    pos += 1  # content_id
    pos += 2  # chapter, section
    n_vo = data[pos]; pos += 1
    pos += n_vo * 9
    n_fo = data[pos]; pos += 1
    pos += n_fo * 2
    pos += 1  # target
    n_params = data[pos]; pos += 1
    for _ in range(n_params):
        pos += 4
        _, pos = _sim_cstr(data, pos)
    _, pos = _sim_cstr(data, pos)  # title
    n_enun = data[pos]; pos += 1
    for _ in range(n_enun):
        pos = _sim_page_block(data, pos)
    n_tail = data[pos]; pos += 1
    for _ in range(n_tail):
        pos = _sim_page_block(data, pos)
    live_size = struct.unpack_from("<H", data, pos)[0]
    pos += 2 + live_size
    if pos != expect_end:
        raise ParseSimError("exercise at %d: parsed to %d, expected %d (delta %d)"
                            % (start, pos, expect_end, expect_end - pos))
    return pos


def sim_parse_chunk(payload):
    """Replays the C loader's pointer walk. Raises ParseSimError on any
    misalignment. Returns (n_templates, n_exercises) on success."""
    if (payload[0:4] != MAGIC or payload[4] != VERSION or
            payload[5] != LAYOUT_REVISION):
        raise ParseSimError("bad magic/version")
    n_templates = struct.unpack_from("<H", payload, 6)[0]
    t_off_table = 8
    t_offsets = [struct.unpack_from("<H", payload, t_off_table + 2 * i)[0]
                 for i in range(n_templates)]
    n_ex_pos = t_off_table + 2 * n_templates
    n_exercises = struct.unpack_from("<H", payload, n_ex_pos)[0]
    e_off_table = n_ex_pos + 2
    e_offsets = [struct.unpack_from("<H", payload, e_off_table + 2 * i)[0]
                 for i in range(n_exercises)]

    all_offsets = sorted(t_offsets + e_offsets) + [len(payload)]
    for i, off in enumerate(t_offsets):
        next_off = all_offsets[all_offsets.index(off) + 1]
        _sim_template(payload, off, next_off)
    for i, off in enumerate(e_offsets):
        next_off = all_offsets[all_offsets.index(off) + 1]
        _sim_exercise(payload, off, next_off)
    return n_templates, n_exercises
