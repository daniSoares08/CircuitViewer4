#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Generate the official, new-only CircuitViewer4 catalog and AppVars."""

import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import content  # noqa: E402
import topology  # noqa: E402
import mesh_trace  # noqa: E402
import cv4_ops  # noqa: E402
import cv4_content as cc  # noqa: E402
import pack_v2 as pk  # noqa: E402
from live_recipe import compile_recipe
from content.live_solutions import SCALAR, PARAM_FIX
from content.live_networks import network_recipe
from content.live_specials import special_recipe, EXTRA_PARAMS

ROOT = Path(__file__).resolve().parents[1]
# Keep enough headroom below the 16-bit AppVar payload ceiling while avoiding
# a nearly-empty fourth chunk after the scalar-edit catalog expansion.
CHUNK_LIMIT = 60000


# ---------------------------------------------------------------------------
# Text pages
# ---------------------------------------------------------------------------

TEXT_X = 14
TEXT_YS = [62, 82, 102, 122, 142, 162, 182]
COLOR_VALUES = {"COL_BLACK": 1, "COL_BLUE": 4, "COL_RED": 5}


def c_string(value):
    value.encode("ascii", "strict")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def wrap_text(line, width=37):
    words, out, cur = str(line).split(), [], ""
    for word in words:
        candidate = word if not cur else cur + " " + word
        if len(candidate) <= width:
            cur = candidate
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur or not out:
        out.append(cur)
    return out

def build_text_blocks(lines_source, title):
    items = []
    for raw in lines_source:
        color = "COL_BLACK"
        text = raw
        if raw.startswith("# "):
            text, color = raw[2:], "COL_BLUE"
        elif raw.startswith("= "):
            text, color = raw[2:], "COL_RED"
        items.extend((part, color) for part in wrap_text(text))
    pages = []
    chunks = [items[i:i + 7] for i in range(0, len(items), 7)] or [[]]
    for page_no, chunk in enumerate(chunks):
        subtitle = "" if len(chunks) == 1 else "parte %d/%d" % (page_no + 1, len(chunks))
        lines = [(TEXT_X, TEXT_YS[i], COLOR_VALUES[color], text)
                 for i, (text, color) in enumerate(chunk)]
        pages.append({"title": title, "subtitle": subtitle,
                      "result": "", "result_y": 0, "lines": lines})
    return pages, []


def build_page_blocks(ex):
    return build_text_blocks(
        ex.get("statement", ["Exercicio sem enunciado cadastrado."]),
        "Enunciado")


def comp_counts(topo):
    counts = [0, 0, 0, 0, 0]
    if not topo:
        return counts
    for el in topo["elements"]:
        slot = {"R": 0, "Z": 0, "VSRC": 1, "ISRC": 2, "C": 3, "L": 4}.get(el["kind"])
        if slot is not None:
            counts[slot] += 1
    return counts


# ---------------------------------------------------------------------------
# Template dedup
# ---------------------------------------------------------------------------

def ops_signature(ops):
    sig = []
    for op in ops:
        name = op[0]
        if name in cv4_ops._COMPONENT_OPS:
            a, b, c, d, flag, _label = cv4_ops._normalize_op(op)
            sig.append((name, a, b, c, d, flag))
        else:
            sig.append(tuple(op))
    return tuple(sig)


class TemplateBank:
    def __init__(self):
        self.by_sig = {}
        self.templates = []  # list of dicts (pre-encode form)

    def get_or_add(self, ops, topo, extra, dep_resolve=None):
        # Solver metadata is part of the identity. Equal drawings with a
        # different frequency, port pair or mesh basis are not interchangeable.
        mesh_sig = tuple(tuple(tuple(edge) for edge in mesh)
                         for mesh in extra.get("meshes", []))
        # Different numerical defaults must not reuse the first circuit's
        # registers/labels. Geometry alone silently substituted another problem.
        sig = (tuple(tuple(op) for op in ops), repr(dep_resolve), extra.get("omega", 0.0), mesh_sig,
               extra.get("port_a", 0xFF), extra.get("port_b", 0xFF),
               extra.get("flags2", 0))
        if sig in self.by_sig:
            return self.by_sig[sig]
        comps, v2ops = cv4_ops.build_comps_and_ops(ops, topo, dep_resolve)
        idx = len(self.templates)
        t = {
            "n_nodes": topo["n_nodes"], "comps": comps, "ops": v2ops,
            "omega": extra.get("omega", 0.0),
            "meshes": extra.get("meshes", []),
            "port_a": extra.get("port_a", 0xFF), "port_b": extra.get("port_b", 0xFF),
            "flags2": extra.get("flags2", 0),
        }
        self.templates.append(t)
        self.by_sig[sig] = idx
        return idx


# ---------------------------------------------------------------------------
# Main pass
# ---------------------------------------------------------------------------

def process_all():
    bank = TemplateBank()
    out_exercises = []  # list of (sort_key, encoded_exercise_dict_pre_encode)
    stats = {"dynamic": 0, "with_figure": 0, "without_figure": 0}
    _subjects, circuits, catalog = content.load()

    for catalog_index, ex in enumerate(catalog):
        cid, chapter, section, _title = cc.resolve_content(ex)
        runtime_cid = cid
        is_static = bool(ex.get("static", False))
        has_circuit = ex["id"] in circuits
        template_id = None
        topo = None
        engine = dict(ex.get("engine", {}))
        book_number = re.fullmatch(r'p(\d+)_(\d+)[ab]?', ex['id'])
        if book_number and chapter==11 and int(book_number.group(2))<22:
            engine['peak']=True  # Book footnote: RMS convention starts at 11.22.

        # Algebraic/design figures require a live recipe (possibly with ideal
        # AOP constraints), never a frozen symbolic/numeric answer.
        if engine.get("visual_only"):
            runtime_cid = cc.CID_STATIC
        elif engine.get("force_nodal"):
            # Preserve the chapter/section menu placement while using the
            # robust generic nodal recalculation route after the first edit.
            runtime_cid = cc.CID_NODAL_AC

        if has_circuit:
            ops = circuits[ex["id"]]
            if (is_static and not engine.get("diagram_only") and
                    not engine.get("visual_only")):
                # Every electrical figure needs a deterministic live route:
                # passive two-terminal networks become Zin/Zeq problems;
                # networks with a source use the generic AC nodal narrator.
                engine.setdefault("omega", 1.0)
                has_independent_source = any(
                    op[0] in ("vsrc_h", "vsrc_v", "isrc_h", "isrc_v")
                    for op in ops)
                terminals = [op[-1] for op in ops if op[0] == "term"]
                if not has_independent_source and len(terminals) >= 2:
                    runtime_cid = cc.CID_IMPEDANCIA_AC
                    engine.setdefault("port_labels", terminals[:2])
            if engine.get("diagram_only"):
                if engine.get('flags2',0)&8 and [p[0] for p in ex.get('params',[])]!=['Acos','Asin']:
                    raise ValueError('live phasor requires Acos, Asin in that order: '+ex['id'])
                topo = {"n_nodes": 0, "elements": [], "symbolic": [],
                        "node_coord": {}, "warnings": []}
            else:
                topo = topology.derive_topology(ops, ex["id"])
                if topo["symbolic"]:
                    raise ValueError("%s has unsupported symbolic components: %r" %
                                     (ex["id"], topo["symbolic"]))
            extra = dict(engine)
            if cid == cc.CID_MALHAS_AC and "meshes" not in extra:
                extra["meshes"] = mesh_trace.fundamental_meshes(topo)
            if "target_op_index" in engine:
                target_el = next(el for el in topo["elements"]
                                 if el["op_index"] == engine["target_op_index"])
                engine["target"] = topo["elements"].index(target_el)
            if engine.get("peak"):
                extra["flags2"] = extra.get("flags2", 0) | 1
            if "port_labels" in engine:
                labels = engine["port_labels"]
                ports = []
                for label in labels:
                    found = None
                    for op in ops:
                        if op[0] == "term" and str(op[-1]).lower() == label.lower():
                            for node, points in topo["node_coord"].items():
                                if (op[1], op[2]) in points:
                                    found = node
                                    break
                    if found is None:
                        raise ValueError("%s: terminal %s not found" % (ex["id"], label))
                    ports.append(found)
                extra["port_a"], extra["port_b"] = ports
            template_id = bank.get_or_add(
                ops, topo, extra, dep_resolve=engine.get("dep_resolve"))
            stats["with_figure"] += 1
        else:
            stats["without_figure"] += 1

        statement, _tail = build_page_blocks(ex)
        tail = []
        if is_static:
            tail, _unused = build_text_blocks(
                ex.get("solution", ["Resolucao nao cadastrada."]), "Resolucao")

        e = {
            "template_id": template_id,
            # content_id preserves subject routing; a recipe overrides the
            # numeric narrator on both first opening and subsequent edits.
            "content_id": runtime_cid,
            "chapter": chapter, "section": section,
            "val_overrides": ex.get("val_overrides", []),
            "flag_overrides": ex.get("flag_overrides", []),
            "target": engine.get("target", engine.get("profile", 0xFF)),
            "params": ex.get("params", []),
            "title": ex["title"], "statement": statement, "tail": tail,
        }
        e['params']=PARAM_FIX.get(ex['id'],e['params'])
        e['params']=e['params']+EXTRA_PARAMS.get(ex['id'],[])
        live_spec=ex.get('live_recipe') or SCALAR.get(ex['id'])
        if has_circuit and not engine.get('diagram_only'):
            live_spec=special_recipe(ex['id'],bank.templates[template_id],topo,ops) or live_spec
        if live_spec is None and has_circuit and not engine.get('diagram_only'):
            # Every worked electrical figure gets the same live calculation
            # on first opening and after edits. Never retain a frozen answer.
            if is_static or engine.get('visual_only'):
                use_cid=cid
                if chapter==9 and not any(c['kind'] in (1,2) for c in bank.templates[template_id]['comps']):use_cid=0
                if book_number and chapter==10 and 55<=int(book_number.group(2))<=68:use_cid=4
                if use_cid==6 and ex['id'] in ('p11_14','p11_16','p11_18','p11_19','p11_20'):
                    load=next(c for c in reversed(bank.templates[template_id]['comps']) if c['kind'] in (0,3,4,8))
                    bank.templates[template_id]['port_a']=load['na']
                    bank.templates[template_id]['port_b']=load['nb']
                if use_cid in (0,4,6) and bank.templates[template_id]['port_a']==255:
                    labels=[op for op in ops if op[0]=='term']
                    if len(labels)>=2:
                        for attr,op in zip(('port_a','port_b'),labels[:2]):
                            bank.templates[template_id][attr]=next(k for k,ps in topo['node_coord'].items() if (op[1],op[2]) in ps)
                    else:use_cid=1
                ex_for_recipe=dict(ex,engine=engine)
                live_spec=network_recipe(ex_for_recipe,bank.templates[template_id],topo,ops,use_cid)
        if live_spec:
            template=bank.templates[template_id] if template_id is not None else {'comps':[],'n_nodes':0}
            e['live']=compile_recipe(live_spec,[p[0] for p in e['params']],len(template['comps']),template['n_nodes'])
            e['live_spec']=live_spec
            e['tail']=[]
        if runtime_cid==cc.CID_STATIC and not e.get('live'):
            raise ValueError(ex['id']+': editable exercise without recalculation')
        stats['dynamic'] += int(bool(e.get('live')) or not is_static)
        sort_key = (chapter, section, ex.get("priority", 1000), catalog_index)
        out_exercises.append({
            "sort_key": sort_key, "data": e, "id": ex["id"],
            "title": ex["title"], "source": ex.get("source", ""),
            "content_title": cc.resolve_content(ex)[3],
            "comp_counts": comp_counts(topo), "has_fig": has_circuit,
            "is_dynamic": bool(e.get('live')) or not is_static,
        })

    out_exercises.sort(key=lambda r: r["sort_key"])
    return bank, out_exercises, stats


# ---------------------------------------------------------------------------
# content_flags.h (hand-edited compilation directives - parsed, not written,
# except the first time when it doesn't exist yet)
# ---------------------------------------------------------------------------

CONTENT_FLAG_NAMES = {
    cid: "CV4_CONTENT_%s" % subject.upper().replace(" ", "_")
    for cid, subject, _title, _chapter, _section in cc.CONTENT_META
}


def ensure_content_flags_h():
    path = ROOT / "src" / "content_flags.h"
    if path.exists():
        return
    lines = [
        "/* CircuitViewer4 - github.com/daniSoares08",
        " * Open source (MIT License): free to use, copy, modify and redistribute. */",
        "",
        "/* Hand-edited compilation directives - see .ai-tasks/spec_appvar_v2.md.",
        " * Flip any flag to 0 and rebuild (make clean && make; then rerun",
        " * tools/generate_cv4.py to also shrink the AppVar payload) to drop",
        " * that content from both the compiled menu and the packed data. */",
        "#ifndef CV4_CONTENT_FLAGS_H",
        "#define CV4_CONTENT_FLAGS_H",
        "",
    ]
    for cid, _subj, title, _ch, _sec in cc.CONTENT_META:
        lines.append("#define %s 1  /* %s */" % (CONTENT_FLAG_NAMES[cid], title))
    lines += ["", "#endif", ""]
    path.write_text("\n".join(lines), encoding="ascii")
    print("wrote %s (all content enabled by default)" % path)


def read_content_flags():
    path = ROOT / "src" / "content_flags.h"
    text = path.read_text(encoding="ascii")
    flags = {}
    for cid, name in CONTENT_FLAG_NAMES.items():
        m = re.search(r"#define\s+%s\s+(\d+)" % re.escape(name), text)
        flags[cid] = bool(m and int(m.group(1)))
    return flags


# ---------------------------------------------------------------------------
# Chunking + packing (mirrors v3's greedy bin-packing, extended for
# chunk-local template ids - see .ai-tasks/spec_appvar_v2.md)
# ---------------------------------------------------------------------------

def pack_chunks(bank, exercises):
    chunks = []  # each: {"templates": [encoded], "tpl_global_to_local": {}, "exercises": [encoded]}
    cur = {"templates": [], "tpl_global_to_local": {}, "exercises": []}
    placement = []  # placement[i] = (chunk_idx, local_ex_idx) for exercises[i]

    def projected_size(templates, exs):
        try:
            return len(pk.build_chunk_payload(templates, exs))
        except AssertionError:
            return 10 ** 9

    for i, rec in enumerate(exercises):
        e = rec["data"]
        need_new_template = False
        tpl_bytes = None
        if e["template_id"] is not None and e["template_id"] not in cur["tpl_global_to_local"]:
            tpl_bytes = pk.encode_template(bank.templates[e["template_id"]])
            need_new_template = True

        e_for_encode = dict(e)
        if e["template_id"] is not None:
            local_tpl = cur["tpl_global_to_local"].get(e["template_id"],
                                                        len(cur["templates"]))
            e_for_encode["template_id"] = local_tpl
        ex_bytes = pk.encode_exercise(e_for_encode)

        trial_templates = cur["templates"] + ([tpl_bytes] if need_new_template else [])
        trial_exs = cur["exercises"] + [ex_bytes]
        if cur["exercises"] and projected_size(trial_templates, trial_exs) > CHUNK_LIMIT:
            chunks.append(cur)
            cur = {"templates": [], "tpl_global_to_local": {}, "exercises": []}
            need_new_template = e["template_id"] is not None
            tpl_bytes = pk.encode_template(bank.templates[e["template_id"]]) if need_new_template else None
            e_for_encode = dict(e)
            if e["template_id"] is not None:
                e_for_encode["template_id"] = 0
            ex_bytes = pk.encode_exercise(e_for_encode)

        if need_new_template:
            cur["tpl_global_to_local"][e["template_id"]] = len(cur["templates"])
            cur["templates"].append(tpl_bytes)
        cur["exercises"].append(ex_bytes)
        placement.append((len(chunks), len(cur["exercises"]) - 1))

    if cur["exercises"]:
        chunks.append(cur)

    payloads = [pk.build_chunk_payload(c["templates"], c["exercises"]) for c in chunks]
    for idx, payload in enumerate(payloads):
        n_t, n_e = pk.sim_parse_chunk(payload)
        assert n_t == len(chunks[idx]["templates"])
        assert n_e == len(chunks[idx]["exercises"])
    return payloads, placement


# ---------------------------------------------------------------------------
# Compiled metadata emission (src/exercises.c, EXERCISE_MANIFEST.md)
# ---------------------------------------------------------------------------

def estimate_page_count(rec):
    if not rec["is_dynamic"]:
        return max(1, len(rec["data"]["statement"]) + len(rec["data"]["tail"]) +
                  (1 if rec["has_fig"] else 0))
    # rough estimate only - the runtime recomputes the real count live.
    return (1 if rec["has_fig"] else 0) + len(rec["data"]["statement"]) + 3


def generate_c(exercises, flags):
    out = [
        "/* CircuitViewer4 - github.com/daniSoares08",
        " * Open source (MIT License): free to use, copy, modify and redistribute. */",
        "",
        '#include "cv3.h"',
        "",
        "/* Generated by tools/generate_cv4.py. Do not edit by hand. */",
        "",
    ]

    kept = [r for r in exercises if flags.get(r["data"]["content_id"], True)
            or r["data"]["content_id"] == 0xFF]
    out.append("const ExMeta ex_meta[] = {")
    for rec in kept:
        chunk, local = rec["placement"]
        cc5 = rec["comp_counts"]
        out.append('    { %s, %s, %d, %d, %d, { %d, %d, %d, %d, %d } },'
                  % (c_string(rec["title"]), c_string(rec["content_title"]),
                     chunk, local, estimate_page_count(rec),
                     cc5[0], cc5[1], cc5[2], cc5[3], cc5[4]))
    out.append("};")
    out.append("")
    out.append("const uint16_t ex_count = %d;" % len(kept))
    out.append("const uint8_t chunk_count = %d;" % rec_chunk_count[0])
    out.append("")

    out.append("const SubRange subjects[] = {")
    groups = []
    seen_keys = []
    for rec in kept:
        key = (rec["data"]["chapter"], rec["data"]["section"])
        if key not in seen_keys:
            seen_keys.append(key)
            groups.append({"key": key, "title": rec["content_title"], "start": None, "count": 0})
    idx_map = {g["key"]: g for g in groups}
    for i, rec in enumerate(kept):
        g = idx_map[(rec["data"]["chapter"], rec["data"]["section"])]
        if g["start"] is None:
            g["start"] = i
        g["count"] += 1
    for g in groups:
        out.append('    { %s, %d, %d },' % (c_string(g["title"]), g["start"], g["count"]))
    out.append("};")
    out.append("")
    out.append("const uint8_t subject_count = %d;" % len(groups))
    out.append("")

    out.append("const MenuItem menu_items[] = {")
    out.append('    { "Buscar", MENU_SEARCH, 0 },')
    for i, g in enumerate(groups):
        out.append('    { %s, MENU_SUBJECT, %d },' % (c_string(g["title"]), i))
    out.append("};")
    out.append("")
    out.append("const uint8_t menu_count = %d;" % (len(groups) + 1))
    out.append("")

    def has_fig(rec):
        return rec["has_fig"]

    def is_exam(rec):
        title = rec["title"]
        return title.startswith(("Prova", "Rec", "PV1")) or "PROVAS" in rec.get("source", "")

    browse = [(i, has_fig(r)) for i, r in enumerate(kept)]

    def emit_browse(name, rows):
        out.append("const uint16_t %s[] = {" % name)
        for idx, _fig in rows:
            out.append("    %d," % idx)
        if not rows:
            out.append("    0,")
        out.append("};")
        out.append("")

    nofig = [b for b in browse if not b[1]]
    withfig = [b for b in browse if b[1]]
    emit_browse("nofig_items", nofig)
    out.append("const uint16_t nofig_count = %d;" % len(nofig))
    out.append("")
    emit_browse("withfig_items", withfig)
    out.append("const uint16_t withfig_count = %d;" % len(withfig))
    out.append("")

    return "\n".join(out)


rec_chunk_count = [0]  # set by main() before generate_c() runs


def main():
    ensure_content_flags_h()
    flags = read_content_flags()

    bank, exercises, stats = process_all()
    print("classification:", stats)

    kept = [r for r in exercises if flags.get(r["data"]["content_id"], True)
            or r["data"]["content_id"] == 0xFF]
    dropped = len(exercises) - len(kept)
    if dropped:
        print("content_flags.h disabled %d exercises" % dropped)

    payloads, placement = pack_chunks(bank, kept)
    rec_chunk_count[0] = len(payloads)
    for i, r in enumerate(kept):
        r["placement"] = placement[i]

    bin_dir = ROOT / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    for stale in list(bin_dir.glob("CV4DAT*.bin")) + list(bin_dir.glob("CV4DAT*.8xv")):
        stale.unlink()

    convbin = find_convbin()
    for idx, payload in enumerate(payloads):
        name = "CV4DAT%d" % idx
        bin_path = bin_dir / ("%s.bin" % name)
        appvar_path = bin_dir / ("%s.8xv" % name)
        bin_path.write_bytes(payload)
        subprocess.run([convbin, "--iformat", "bin", "--oformat", "8xv",
                        "--name", name, "--archive",
                        "--input", str(bin_path), "--output", str(appvar_path)],
                       check=True)
        print("wrote %s (%d bytes payload)" % (appvar_path, len(payload)))

    (ROOT / "src" / "exercises.c").write_text(generate_c(kept, flags), encoding="ascii")
    print("wrote src/exercises.c (%d exercises, %d chunks, %d templates)"
         % (len(kept), len(payloads), len(bank.templates)))


def find_convbin():
    found = shutil.which("convbin.exe") or shutil.which("convbin")
    if found:
        return found
    for candidate in ("C:/CEdev/bin/convbin.exe", "/c/CEdev/bin/convbin.exe"):
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError("convbin.exe not found")


if __name__ == "__main__":
    main()
