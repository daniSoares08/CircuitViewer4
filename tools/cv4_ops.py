#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Converts a v3 op-list + its derived topology into v2 template
ops+comps: each electrical element becomes one EditComp (register), each
direction-editable arrow becomes a CK_ARROW register, everything else stays
a literal-label op exactly like v3. See .ai-tasks/spec_v4_engine.md
section 2 and .ai-tasks/spec_appvar_v2.md."""

NAME_TO_OPCODE = {
    "wire": 0, "line": 0, "node": 1, "term": 2,
    "res_h": 3, "res_v": 4, "cap_h": 5, "cap_v": 6, "ind_h": 7, "ind_v": 8,
    "vsrc_v": 9, "vsrc_h": 10, "isrc_v": 11, "isrc_h": 12, "gnd": 13,
    "sw_h": 14, "opamp": 15, "dvs_v": 16, "dvs_h": 17, "dis_v": 18,
    "lbl": 19, "arr_h": 20, "arr_v": 21, "vo": 22, "pm": 23,
    "imp_h": 24, "imp_v": 25,
}
_ARROW_OPS = {"arr_h", "arr_v"}
_COMPONENT_OPS = {
    "res_h", "res_v", "cap_h", "cap_v", "ind_h", "ind_v", "imp_h", "imp_v",
    "vsrc_v", "vsrc_h", "isrc_v", "isrc_h", "dvs_v", "dvs_h", "dis_v",
}

CK = {"R": 0, "VSRC": 1, "ISRC": 2, "C": 3, "L": 4, "DVS": 5, "DIS": 6,
      "Z": 8}
CK_ARROW = 7

NONE8 = 0xFF


class OpsError(Exception):
    pass


def solve_nodes(op_name, flag, na, nb):
    """Map a source op's topology terminals (na=first terminal, nb=second) to
    the MNA convention (na = "+" for a V source; positive current injected
    INTO nb for an I source), per how src/ui.c actually DRAWS each symbol:

      vsrc_v / dvs_v : "+" on top by default; flag swaps it
      vsrc_h / dvs_h : "+" on the RIGHT by default; flag swaps it
      isrc_v / dis_v : arrow up (flag) injects the TOP node   -> swap iff up
      isrc_h         : arrow right (flag) injects the RIGHT node -> swap iff left

    Getting this wrong silently flips a source's sign in the solve (a real
    bug found via e_3_32: v1 came out 22 V instead of 2 V). Resistors/caps/
    inductors are symmetric - callers only pass source ops here."""
    if op_name in ("vsrc_v", "dvs_v"):
        return (nb, na) if flag else (na, nb)
    if op_name in ("vsrc_h", "dvs_h"):
        return (na, nb) if flag else (nb, na)
    if op_name in ("isrc_v", "dis_v"):
        return (nb, na) if flag else (na, nb)      # flag = upward
    if op_name == "isrc_h":
        return (na, nb) if flag else (nb, na)      # flag = right
    return na, nb  # symmetric components


def _normalize_op(op):
    """Normalize one authored drawing op; returns
    (a,b,c,d, flag, label_or_None)."""
    name = op[0]
    args = op[1:]
    if name == "lbl":
        return op[2], op[3], 0, 0, 0, op[1]
    nums, flag, label = [], 0, None
    for arg in args:
        if isinstance(arg, bool):
            flag = 1 if arg else 0
        elif isinstance(arg, str):
            label = arg
        elif isinstance(arg, int):
            nums.append(arg)
        else:
            raise OpsError("unsupported op arg %r in %r" % (arg, op))
    nums = (nums + [0, 0, 0, 0])[:4]
    return nums[0], nums[1], nums[2], nums[3], flag, label


def build_comps_and_ops(ops, topo, dep_resolve=None):
    """Returns (comps, v2ops). comps[i] = {kind,na,nb,ctrl,ctrl_a,ctrl_b,
    deflt,flags}. v2ops[i] = {opcode,a,b,c,d,flag,reg,label}. Raises
    OpsError if an element references an unresolved dependent-source
    control variable and no matching entry exists in `dep_resolve` (see
    tools/cv4_annotations.py's DEP_SOURCE_CTRL - caller should fall back to
    static for that exercise - see spec section 7 / circviewer4-rebuild
    memory). `dep_resolve` = {dvs_or_dis_op_index: {"kind": "voltage",
    "node_op_index": int} | {"kind": "current", "branch_op_index": int}}."""
    dep_resolve = dep_resolve or {}

    # pass 1: assign every element a comp index (needed before resolving
    # any current-controlled ctrl, which may reference an element that
    # appears LATER in the op list than the dependent source itself).
    op_index_to_comp = {}
    for i, el in enumerate(topo["elements"]):
        if el["kind"] not in CK:
            raise OpsError("unknown element kind %r" % el["kind"])
        op_index_to_comp[el["op_index"]] = i

    comps = []
    for el in topo["elements"]:
        ctrl, ctrl_a, ctrl_b = NONE8, 0, 0
        na, nb = el["na"], el["nb"]
        if el["kind"] in ("VSRC", "ISRC", "DVS", "DIS"):
            src_op = ops[el["op_index"]]
            _a, _b, _c, _d, flag, _lbl = _normalize_op(src_op)
            na, nb = solve_nodes(src_op[0], bool(flag), na, nb)
        if el["ctrl"] is not None or (el['kind'] in ('DVS','DIS') and el['op_index'] in dep_resolve):
            resolve = dep_resolve.get(el["op_index"])
            if resolve is None:
                raise OpsError("dependent source control %r not resolved "
                               "(op_index=%d)" % (el["ctrl"], el["op_index"]))
            if resolve["kind"] == "voltage":
                node_op = resolve["node_op_index"]
                node_el = next((e for e in topo["elements"] if e["op_index"] == node_op), None)
                if node_el is None:
                    raise OpsError("node_op_index %d not a real element" % node_op)
                non_gnd = node_el["na"] if node_el["na"] != 0 else node_el["nb"]
                ctrl_a, ctrl_b = non_gnd, 0
            elif resolve["kind"] == "current":
                branch_comp = op_index_to_comp.get(resolve["branch_op_index"])
                if branch_comp is None:
                    raise OpsError("branch_op_index %d not a real element" %
                                   resolve["branch_op_index"])
                ctrl = branch_comp
            else:
                raise OpsError("unknown dep_resolve kind %r" % resolve["kind"])
        comps.append({
            "kind": CK[el["kind"]], "na": na, "nb": nb,
            "ctrl": ctrl, "ctrl_a": ctrl_a, "ctrl_b": ctrl_b,
            "deflt": el["value"], "deflt_im": el.get("value_im", 0.0), "flags": 0,
        })

    v2ops = []
    for idx, op in enumerate(ops):
        name = op[0]
        if name not in NAME_TO_OPCODE:
            raise OpsError("unknown op %r" % (op,))
        a, b, c, d, flag, label = _normalize_op(op)
        reg = NONE8
        out_label = label or ""
        if name in _COMPONENT_OPS:
            if idx not in op_index_to_comp:
                raise OpsError("component op %d (%s) has no topology element "
                               "(likely a symbolic/unparseable value)" % (idx, name))
            reg = op_index_to_comp[idx]
            # keep the ORIGINAL authored label (e.g. "4", "12V", "5io") - the
            # C loader shows it verbatim while the value is unedited (so an
            # untouched circuit is pixel-identical to v3, no unit overflow),
            # and only reformats compactly via fmt_label once the user edits
            # the value. See src/appvar.c av_draw_circuit.
            out_label = label or ""
        elif name in _ARROW_OPS:
            reg = len(comps)
            comps.append({
                "kind": CK_ARROW, "na": 0, "nb": 0,
                "ctrl": NONE8, "ctrl_a": 0, "ctrl_b": 0,
                "deflt": 0.0, "flags": 0,
            })
            out_label = label or ""
        v2ops.append({
            "opcode": NAME_TO_OPCODE[name], "a": a, "b": b, "c": c, "d": d,
            "flag": flag, "reg": reg, "label": out_label,
        })

    if len(comps) > 16:
        raise OpsError("too many registers (%d > 16 COMP_MAXN)" % len(comps))
    return comps, v2ops
