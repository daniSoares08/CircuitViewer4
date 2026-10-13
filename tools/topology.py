#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Auto-derive electrical topology (nodes + elements) from a v3-style op
list, purely from the pixel coordinates already present in every op - see
.ai-tasks/spec_v4_engine.md section 3 and 7.

Algorithm: union-find over every terminal coordinate; a `wire` op unions
adjacent same-line points EXCEPT across a gap that exactly matches another
component's own two terminals (a resistor/source drawn "bridging" part of
a long rail - the wire is really two separate segments with the component
between them, a common pattern in these ladder diagrams; see
_collinear_points_on/union_wires). Component ops are NOT unioned with each
other directly - they connect two (generally different) nodes.

Some circuits label a component with a variable ("R", "Vo", "vi") instead
of a number - the pedagogical point of those problems is either an inverse
("find R"/"find V") or a symbolic ratio (op-amp vo/vi), not "solve this
numeric network". parse_value() flags those (mag=None, symbolic=label)
instead of raising, so the caller can mark the whole exercise "static"
(keep its existing pre-written text, still draw the figure, don't attempt
live re-solving) rather than losing it.
"""

import re

_TWO_TERM_H = {"res_h", "cap_h", "ind_h", "imp_h", "vsrc_h", "isrc_h", "dvs_h", "sw_h"}
_TWO_TERM_V = {"res_v", "cap_v", "ind_v", "imp_v", "vsrc_v", "isrc_v", "dvs_v", "dis_v"}
_WIRE = {"wire", "line"}
_ONE_TERM = {"term", "node", "gnd"}
_COMPONENT_KIND = {
    "res_h": "R", "res_v": "R",
    "cap_h": "C", "cap_v": "C",
    "ind_h": "L", "ind_v": "L",
    "imp_h": "Z", "imp_v": "Z",
    "vsrc_h": "VSRC", "vsrc_v": "VSRC",
    "isrc_h": "ISRC", "isrc_v": "ISRC",
    "dvs_h": "DVS", "dvs_v": "DVS",
    "dis_v": "DIS",
}

_VAL_RE = re.compile(r'^(-?\d+\.?\d*)([GMkmunp])?(ohm|V|A|F|H)?(\w*)$')
_EXPR_RE = re.compile(r'^(-?\d+\.?\d*)\s*([+-])\s*(\d+\.?\d*)$')
_SCALE = {"G":1e9,"M":1e6,"k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9,"p":1e-12, None: 1.0}
_RECT_COMPLEX_RE = re.compile(
    r'^\(?\s*([+-]?\d+(?:\.\d+)?)?\s*([+-])?\s*j\s*(\d+(?:\.\d+)?)\s*\)?(?:ohm)?$',
    re.IGNORECASE)
_PURE_J_RE = re.compile(r'^([+-]?)j(\d+(?:\.\d+)?)(?:ohm)?$', re.IGNORECASE)
_POLAR_RE = re.compile(r'^([+-]?\d+(?:\.\d+)?)\s*(?:/_|<|angle)\s*([+-]?\d+(?:\.\d+)?)(?:deg)?(?:V|A)?$', re.IGNORECASE)


class TopologyError(Exception):
    pass


def parse_complex_value(label):
    """Return (real, imag, symbolic). Accepts rectangular and polar labels."""
    s = label.strip().replace(" ", "")
    # Compact independent engineering prefixes on the two rectangular parts.
    m = re.match(r'^([+-]?\d+(?:\.\d+)?)([kmun])?([+-])j(\d+(?:\.\d+)?)([kmun])$', s)
    if m:
        return (float(m[1])*_SCALE[m[2]],
                float(m[4])*_SCALE[m[5]]*(-1 if m[3]=='-' else 1), None)
    m = _PURE_J_RE.match(s)
    if m:
        return 0.0, (-1.0 if m.group(1) == "-" else 1.0) * float(m.group(2)), None
    m = _RECT_COMPLEX_RE.match(s)
    if m:
        real = float(m.group(1)) if m.group(1) else 0.0
        imag = float(m.group(3)) * (-1.0 if m.group(2) == "-" else 1.0)
        return real, imag, None
    m = _POLAR_RE.match(s)
    if m:
        import math
        mag, deg = float(m.group(1)), float(m.group(2))
        rad = math.radians(deg)
        return mag * math.cos(rad), mag * math.sin(rad), None
    mag, symbolic = parse_value(label)
    return mag, 0.0, symbolic


def parse_value(label):
    """"12V"->(12.0,None); "10"->(10.0,None); "5io"->(5.0,"io");
    "5+3"->(8.0,None) (arithmetic display labels); "R"/"vi"/"Vo"->(None,label)
    for symbolic/unknown quantities (caller should mark the exercise static)."""
    s = label.strip()
    m = _VAL_RE.match(s)
    if m:
        num, prefix, _unit, rest = m.groups()
        mag = float(num) * _SCALE[prefix]
        return mag, (rest or None)
    e = _EXPR_RE.match(s)
    if e:
        a, op, b = e.groups()
        mag = float(a) + float(b) if op == "+" else float(a) - float(b)
        return mag, None
    return None, s


def _terminals(op):
    name = op[0]
    a = op[1:]
    if name in _TWO_TERM_H:
        x1, y, x2 = a[0], a[1], a[2]
        return [(x1, y), (x2, y)]
    if name in _TWO_TERM_V:
        x, y1, y2 = a[0], a[1], a[2]
        return [(x, y1), (x, y2)]
    if name in _WIRE:
        x1, y1, x2, y2 = a[0], a[1], a[2], a[3]
        return [(x1, y1), (x2, y2)]
    if name in _ONE_TERM:
        return [(a[0], a[1])]
    if name == 'opamp':
        return [(a[0],a[1]+13),(a[0],a[1]+37),(a[0]+62,a[1]+29)]
    return []


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def _collinear_points_on(wire, all_points):
    ax, ay, bx, by = wire[1], wire[2], wire[3], wire[4]
    pts = []
    for p in all_points:
        px, py = p
        if ((px-ax)*(by-ay)==(py-ay)*(bx-ax) and
                min(ax,bx)<=px<=max(ax,bx) and min(ay,by)<=py<=max(ay,by)):
            pts.append(((px-ax)*(bx-ax)+(py-ay)*(by-ay),p))
    pts.sort(key=lambda t: t[0])
    return [p for _, p in pts]


def _union_wires(ops, uf, all_points):
    bridge_pairs = set()
    for op in ops:
        if op[0] in _COMPONENT_KIND:
            terms = _terminals(op)
            if len(terms) == 2:
                bridge_pairs.add(frozenset(terms))
    for w in [op for op in ops if op[0] in _WIRE]:
        pts = _collinear_points_on(w, all_points)
        for i in range(len(pts) - 1):
            gap = frozenset((pts[i], pts[i + 1]))
            if gap in bridge_pairs:
                continue  # a component bridges exactly this gap - not a plain wire
            uf.union(pts[i], pts[i + 1])


_TERM_SNAP_PX = 20  # 'term'/'node' markers are drawn a few px off their
                    # real connection point for visual clarity (label/dot
                    # clearance), not pixel-exact - snap to the nearest
                    # other point within this radius if otherwise isolated.


def _snap_isolated_markers(ops, uf, all_points):
    for op in ops:
        if op[0] not in ("term", "node"):
            continue
        p = (op[1], op[2])
        root = uf.find(p)
        if any(uf.find(q) == root for q in all_points if q != p):
            continue  # already connected to something real
        best, best_d = None, None
        for q in all_points:
            if q == p:
                continue
            d = abs(q[0] - p[0]) + abs(q[1] - p[1])
            if d <= _TERM_SNAP_PX and (best_d is None or d < best_d):
                best, best_d = q, d
        if best is not None:
            uf.union(p, best)


def derive_topology(ops, circuit_id="?"):
    """Returns dict: n_nodes, ground, elements[], symbolic[], node_coord,
    warnings[]. `elements` only has numeric-valued components; anything
    whose label didn't parse as a number is appended to `symbolic` instead
    (caller: if symbolic is non-empty, treat the whole exercise as static)."""
    all_points = set()
    for op in ops:
        for p in _terminals(op):
            all_points.add(p)

    uf = UnionFind()
    for p in all_points:
        uf.find(p)
    _union_wires(ops, uf, all_points)
    _snap_isolated_markers(ops, uf, all_points)

    degree = {}
    gnd_root = None
    for op in ops:
        if op[0] == "gnd":
            gnd_root = uf.find((op[1], op[2]))
        if op[0] in _COMPONENT_KIND or op[0] in _WIRE:
            for p in _terminals(op):
                r = uf.find(p)
                degree[r] = degree.get(r, 0) + 1

    if gnd_root is None:
        if not degree:
            raise TopologyError("%s: no electrical elements" % circuit_id)
        # Prefer the textbook's usual reference: the bottom rail. Pick the
        # electrically-connected node whose points sit lowest on screen
        # (largest y), tie-broken by how wide it spans (a rail) then degree.
        # (Falls back to plain max-degree behaviour when there's no clear
        # rail.) Matching the book's reference keeps the narrated node
        # voltages numerically equal to the book's, not merely offset.
        y_of = {}
        span_of = {}
        for p in all_points:
            r = uf.find(p)
            if r not in degree:
                continue
            y_of[r] = max(y_of.get(r, -1), p[1])
            span_of.setdefault(r, [p[0], p[0]])
            span_of[r][0] = min(span_of[r][0], p[0])
            span_of[r][1] = max(span_of[r][1], p[0])
        gnd_root = max(degree, key=lambda r: (
            y_of.get(r, 0), span_of.get(r, [0, 0])[1] - span_of.get(r, [0, 0])[0],
            degree[r]))

    roots = sorted(set(uf.find(p) for p in all_points),
                    key=lambda r: (r != gnd_root, r))
    node_id = {r: i for i, r in enumerate(roots)}
    node_coord = {}
    for p in all_points:
        node_coord.setdefault(node_id[uf.find(p)], []).append(p)

    elements = []
    symbolic = []
    warnings = []
    for idx, op in enumerate(ops):
        name = op[0]
        if name not in _COMPONENT_KIND:
            continue
        kind = _COMPONENT_KIND[name]
        terms = _terminals(op)
        na = node_id[uf.find(terms[0])]
        nb = node_id[uf.find(terms[1])]
        label = op[-1] if isinstance(op[-1], str) else op[-2]
        mag, imag, ctrl_or_sym = parse_complex_value(label)
        if mag is None:
            symbolic.append({"op_index": idx, "kind": kind, "label": label})
            continue
        if na == nb:
            raise TopologyError(
                "%s op#%d (%s) has both terminals on the same node (%r)"
                % (circuit_id, idx, name, terms))
        elements.append({
            "op_index": idx, "kind": kind, "na": na, "nb": nb,
            "value": mag, "value_im": imag, "ctrl": ctrl_or_sym, "label": label,
        })

    if len(node_id) < 2:
        warnings.append("%s: only %d node(s)" % (circuit_id, len(node_id)))

    return {
        "n_nodes": len(node_id),
        "ground": 0,
        "elements": elements,
        "symbolic": symbolic,
        "node_coord": node_coord,
        "warnings": warnings,
    }


def _selftest():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    import content

    _subjects, all_circuits, exercises = content.load()
    diagram_only = {e["id"] for e in exercises
                    if e.get("engine", {}).get("diagram_only")}

    ok, failed, static = 0, [], []
    total_elems = 0
    for cid, ops in sorted(all_circuits.items()):
        if cid in diagram_only:
            continue
        try:
            topo = derive_topology(ops, cid)
            ok += 1
            total_elems += len(topo["elements"])
            if topo["symbolic"]:
                static.append((cid, [s["label"] for s in topo["symbolic"]]))
            for w in topo["warnings"]:
                print("WARN", w)
        except TopologyError as e:
            failed.append((cid, str(e)))

    electrical_total = len(all_circuits) - len(diagram_only)
    print("\n%d/%d electrical circuits derived cleanly (%d total elements), "
          "%d have a symbolic/unknown value" %
          (ok, electrical_total, total_elems, len(static)))
    if diagram_only:
        print("%d diagram-only figure(s) skipped by topology" % len(diagram_only))
    if static:
        print("\nSYMBOLIC (not accepted in the live catalog):")
        for cid, labels in static:
            print("  %s: %r" % (cid, labels))
    if failed:
        print("\n%d FAILURES:" % len(failed))
        for cid, msg in failed:
            print("  %s: %s" % (cid, msg))
    return 0 if not failed else 1


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
