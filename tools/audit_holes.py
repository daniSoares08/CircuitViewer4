#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Precise geometric detector for genuinely dangling component legs (visible
'holes'): a component terminal pixel that no wire passes through, that no
other component/wire/node/gnd terminal coincides with, and that is not an
intentional labeled open (vo/pm marker). Distinct from topology.py's
electrical degree check, which legitimately leaves Thevenin ports / open
measurement terminals at degree 1."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import content
from topology import _terminals

COMP = {'res_h', 'res_v', 'cap_h', 'cap_v', 'ind_h', 'ind_v', 'imp_h', 'imp_v',
        'vsrc_v', 'vsrc_h', 'isrc_v', 'isrc_h', 'dvs_v', 'dvs_h', 'dis_v'}


TOL = 6  # px: a leg within this distance of any wire/terminal/marker is
         # visually connected (covers terminal-circle edges and small
         # authoring offsets). 3.32's genuine gap is 28px - well past this.


def _near_segment(p, a, b, tol):
    px, py = p
    ax, ay = a
    bx, by = b
    if ay == by:
        return abs(py - ay) <= tol and min(ax, bx) - tol <= px <= max(ax, bx) + tol
    if ax == bx:
        return abs(px - ax) <= tol and min(ay, by) - tol <= py <= max(ay, by) + tol
    return False


def _dist(p, q):
    return abs(p[0] - q[0]) + abs(p[1] - q[1])


def find_holes(ops):
    conn = {}
    wires = []
    markers = []   # term/node/gnd/vo/pm connection points (bridge small gaps)
    for op in ops:
        if op[0] in ('wire', 'line'):
            wires.append((op[1], op[2], op[3], op[4]))
            for t in ((op[1], op[2]), (op[3], op[4])):
                conn[t] = conn.get(t, 0) + 1
        elif op[0] == 'arr_h':
            # a current-direction arrow draws a full connecting wire x1..x2
            wires.append((op[1], op[2], op[3], op[2]))
        elif op[0] == 'arr_v':
            wires.append((op[1], op[2], op[1], op[3]))
        elif op[0] == 'opamp':
            # opamp inputs sit on its left edge (x, y..y+58) - resistor legs
            # landing there are connected, not dangling.
            markers.append((op[1], op[2] + 13))
            markers.append((op[1], op[2] + 37))
        elif op[0] in COMP:
            for t in _terminals(op):
                conn[t] = conn.get(t, 0) + 1
        elif op[0] in ('term', 'node', 'gnd'):
            for t in _terminals(op):
                conn[t] = conn.get(t, 0) + 1
                markers.append(t)
        elif op[0] in ('vo', 'pm'):
            markers.append((op[1], op[2]))
            markers.append((op[1], op[3]))
    holes = []
    for op in ops:
        if op[0] not in COMP:
            continue
        for t in _terminals(op):
            if conn.get(t, 0) >= 2:
                continue
            if any(c != t and _dist(c, t) <= TOL for c in conn):
                continue
            if any(_dist(m, t) <= TOL for m in markers):
                continue
            if any(_near_segment(t, (w[0], w[1]), (w[2], w[3]), TOL) for w in wires):
                continue
            holes.append((op[0], t))
    return holes


def main():
    _subjects, all_c, _exercises = content.load()
    real = []
    for cid, ops in sorted(all_c.items()):
        h = find_holes(ops)
        if h:
            real.append((cid, h))
    print("GENUINE holes (dangling component legs): %d circuits" % len(real))
    for cid, h in real:
        print("  %s: %r" % (cid, h))
    return 1 if real else 0


if __name__ == "__main__":
    sys.exit(main())
