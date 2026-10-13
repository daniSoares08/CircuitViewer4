#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Vector intake from LIVRO_ORIGINAL.pdf: turns a book problem number into a
structured JSON draft (statement text + figure geometry + book answer) with
ZERO vision-model tokens.

Why this exists: the book's circuit figures are *vector* art, not raster
images (`page.images` is empty; the drawings are `lines`/`rects`/`curves`
plus positioned text). So component values, labels and wire segments can be
read straight out of the PDF at exact coordinates, instead of paying a
vision model to OCR a 300 dpi PNG and hoping it reads "8 ohm" and not "B ohm".
That makes intake deterministic, free, and more accurate than the eye.

What it does NOT do: decide the electrical topology or lay out the 320x240
calculator drawing. Those are judgment calls left to the authoring step (see
.codex/skills/cv4-exercicios/SKILL.md). This tool's job is to hand that step
a small, exact, pre-digested fact sheet instead of a megabyte of pixels.

Usage
-----
    # one-time (or after changing the PDF): build the problem -> page index
    python tools/book_extract.py --build-index

    # list what a chapter offers (problem number, page, has-figure, has-answer)
    python tools/book_extract.py --chapter 9 --list

    # emit JSON drafts for specific problems
    python tools/book_extract.py --problems 9.13,9.15,10.7 --out .ai-tasks/intake

    # same, plus a TIGHT png crop of each figure (fallback for the rare
    # figure whose geometry is too tangled to read as text; a tight crop is
    # ~40 KB, versus ~2 MB for a full 300 dpi page)
    python tools/book_extract.py --problems 9.13 --out .ai-tasks/intake --crop

Notes on the source PDF
-----------------------
- Two-column layout; columns are split at the page midpoint.
- Appendix D ("Respostas para os problemas impares") carries THREE overlapping
  text layers at slightly different offsets, so every line appears ~3x. We
  parse all copies and take a majority vote per problem number, which reliably
  picks the clean one. Only ODD-numbered problems have answers.
- Degree signs, integrals and other math glyphs come out mangled by the text
  layer. That is expected: the statement is a *draft* for a human/agent to
  tidy, while the values and the geometry - the parts that matter for the
  circuit - come out exact.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "LIVRO_ORIGINAL.pdf"
INDEX = ROOT / ".ai-tasks" / "book_index.json"

# Appendix D: only odd-numbered problems are answered there.
ANSWERS_FIRST_PAGE = 855   # 1-based pdf page, scan starts here
ANSWERS_LAST_PAGE = 894
# Appendix D stacks 3 text layers ~1 pt apart; read at this granularity so
# they stay separate instead of interleaving into garbage. (Measured: this
# recovers 40 answers/chapter where the body-text bucket recovers 11, and it
# beats pdfplumber's own dedupe_chars, which recovers 26 and is far slower.)
ANSWER_YDIV = 1.5

# A chapter's end-of-chapter problem section is dense with markers; the
# chapter body only mentions a number here and there (worked examples,
# cross-references). A page carrying at least this many distinct markers of
# its own chapter is part of the problem section.
PROBLEM_PAGE_MIN_MARKERS = 4

# A figure never extends further above its caption than this (points).
FIG_MAX_HEIGHT = 280
# Geometry thinner than this is page furniture (rules, column separators).
MIN_FIG_ELEMENTS = 4

# The PDF's symbol font has no ToUnicode map, so pdfplumber emits raw CIDs
# and private-use codepoints for the very symbols an AC problem is made of.
# Normalising them here means the JSON hands the authoring step values that
# are already in the calculator's own ASCII convention ("ohm", not U+03A9) -
# see the ASCII rule in .codex/skills/cv4-exercicios/SKILL.md.
GLYPHS = {
    "(cid:58)": "ohm",   # capital omega
    "": "ohm",
    "Ω": "ohm",
    "(cid:113)": "deg",  # degree sign, as in 40 /30deg V
    "°": "deg",
    "(cid:16)": "-",     # minus / negative terminal
    "−": "-",
    "(cid:12)": "",
    "(cid:112)": "pi",
    "∠": "/_",      # phasor angle
    "": "",        # decorative bullet in running heads
}


def normalize(text):
    """Map the PDF's unmapped symbol glyphs onto the project's ASCII names."""
    if not text:
        return text
    for src, dst in GLYPHS.items():
        text = text.replace(src, dst)
    return re.sub(r"[ \t]{2,}", " ", text).strip()


PROBLEM_RE = re.compile(r"^(\d{1,2})\.(\d{1,3})\b")
CAPTION_RE = re.compile(r"Figura\s+(\d{1,2})\.(\d{1,3})")
CAPTION_FOR_RE = re.compile(r"[Pp]roblema\s+(\d{1,2})\.(\d{1,3})")


def _open():
    import pdfplumber
    if not PDF.exists():
        raise SystemExit("PDF nao encontrado: %s" % PDF)
    return pdfplumber.open(str(PDF))


# ---------------------------------------------------------------------------
# Column handling
# ---------------------------------------------------------------------------

def column_boxes(page):
    """Left and right column bounding boxes (the book is two-column)."""
    mid = page.width / 2.0
    return [(0, 0, mid, page.height), (mid, 0, page.width, page.height)]


def column_lines(page, box, ydiv=3.0):
    """Text lines inside a column, as (text, top) sorted top-down.

    `ydiv` is the vertical bucket size used to group words into lines. The
    default (3.0) is right for body text. Appendix D needs a much finer
    bucket (see ANSWER_YDIV): its three overlapping text layers sit ~1 pt
    apart, so a coarse bucket interleaves them into garbage while a fine one
    separates each layer into its own readable line."""
    crop = page.crop(box)
    words = crop.extract_words(x_tolerance=1, y_tolerance=1 if ydiv < 2 else 3)
    rows = defaultdict(list)
    for w in words:
        rows[round(w["top"] / ydiv)].append(w)
    out = []
    for key in sorted(rows):
        ws = sorted(rows[key], key=lambda w: w["x0"])
        out.append((" ".join(w["text"] for w in ws), ws[0]["top"]))
    return out


# ---------------------------------------------------------------------------
# Problem -> page index
# ---------------------------------------------------------------------------

def build_index(chapters=None):
    """Scan the PDF for '<chapter>.<n>' problem markers at column starts.

    A marker only counts when it sits at the very start of a text line inside
    a column AND its chapter matches the chapter the page belongs to - this
    filters out cross-references like 'ver Figura 9.40' mid-paragraph."""
    # Some pages in this PDF nest clipping paths deeply enough to blow the
    # default recursion limit inside pdfplumber; raise it and isolate each
    # page so one pathological page cannot abort the whole scan.
    sys.setrecursionlimit(20000)
    pdf = _open()
    hits = []          # (num, chapter, page)
    per_page = defaultdict(set)
    skipped = []
    cur_chapter = None
    for i, page in enumerate(pdf.pages, 1):
        try:
            text = page.extract_text() or ""
            m = re.search(r"Cap[ií]tulo\s+(\d{1,2})\b", text[:200])
            if m:
                cur_chapter = int(m.group(1))
            ch = cur_chapter
            if ch is None or i >= ANSWERS_FIRST_PAGE:
                continue
            if chapters and ch not in chapters:
                continue
            for box in column_boxes(page):
                for line_text, _top in column_lines(page, box):
                    pm = PROBLEM_RE.match(line_text)
                    if not pm or int(pm.group(1)) != ch:
                        continue
                    num = "%s.%s" % (pm.group(1), pm.group(2))
                    hits.append((num, ch, i))
                    per_page[(ch, i)].add(num)
        except (RecursionError, Exception) as exc:  # noqa: B014 - page is skippable
            skipped.append((i, type(exc).__name__))
        finally:
            page.flush_cache()
        if i % 100 == 0:
            print("  ... pagina %d (%d marcadores)" % (i, len(hits)), file=sys.stderr)
    if skipped:
        print("paginas puladas: %r" % (skipped[:20],), file=sys.stderr)

    # Keep only markers that live on a problem-section page. Without this,
    # "9.3" resolves to the worked example "eXeMpLo 9.3" in the chapter body
    # rather than to end-of-chapter problem 9.3.
    problem_pages = {key for key, nums in per_page.items()
                     if len(nums) >= PROBLEM_PAGE_MIN_MARKERS}
    index = {}
    for num, ch, page_no in hits:
        if (ch, page_no) not in problem_pages:
            continue
        # Review questions reuse 1..10 immediately before the end-of-chapter
        # problem set.  The actual problem occurrence is later in the chapter,
        # so deliberately keep the LAST dense-page hit instead of the first.
        index[num] = {"pdf_page": page_no, "chapter": ch}
    # anything only ever seen outside a problem section still gets recorded,
    # flagged so the caller knows the page is a guess
    for num, ch, page_no in hits:
        if num not in index:
            index[num] = {"pdf_page": page_no, "chapter": ch, "uncertain": True}

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(index, indent=1, sort_keys=True), encoding="utf-8")
    unsure = sum(1 for v in index.values() if v.get("uncertain"))
    print("indice: %d problemas (%d incertos) -> %s" % (len(index), unsure, INDEX))
    return index


def load_index():
    if not INDEX.exists():
        raise SystemExit("indice ausente; rode: python tools/book_extract.py --build-index")
    return json.loads(INDEX.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Answers (Appendix D)
# ---------------------------------------------------------------------------

def _garble(s):
    """0.0 = clean text, higher = more interleaving damage.

    When Appendix D's three text layers get merged, characters end up doubled
    and parentheses unbalanced ("((add)))", "544044 ,,V4488"). Adjacent
    identical characters are rare in clean Portuguese/numeric text, so their
    density is a good cheap discriminator between a clean copy and a merged
    one."""
    if not s:
        return 1.0
    dup = sum(1 for a, b in zip(s, s[1:]) if a == b and not a.isspace())
    unbalanced = abs(s.count("(") - s.count(")"))
    return (dup + 2 * unbalanced) / float(len(s))


def build_answers():
    """Parse Appendix D into {problem_number: {text, votes, seen, garble}}.

    Only ODD-numbered problems are answered in the book, so an even problem
    legitimately has no entry here - that is not a parse failure.

    Each line is rendered ~3x at ~1 pt offsets, so we read at ANSWER_YDIV
    granularity to keep the layers apart, then pick the cleanest candidate
    per problem number (majority vote, tie-broken by _garble())."""
    pdf = _open()
    cands = defaultdict(list)
    for i in range(ANSWERS_FIRST_PAGE, min(ANSWERS_LAST_PAGE, len(pdf.pages)) + 1):
        page = pdf.pages[i - 1]
        try:
            for box in column_boxes(page):
                for text, _top in column_lines(page, box, ydiv=ANSWER_YDIV):
                    m = re.match(r"^(\d{1,2}\.\d{1,3})\s+(.+)$", text)
                    if not m:
                        continue
                    body = m.group(2).strip()
                    if len(body) < 2:
                        continue
                    cands[m.group(1)].append(body)
        finally:
            page.flush_cache()

    answers = {}
    for num, options in cands.items():
        counts = Counter(options)
        best = max(counts.items(), key=lambda kv: (kv[1], -_garble(kv[0])))
        answers[num] = {"text": best[0], "votes": best[1],
                        "seen": len(options), "garble": round(_garble(best[0]), 3)}
    return answers


_ANSWER_CACHE = ROOT / ".ai-tasks" / "book_answers.json"


def load_answers(rebuild=False):
    """build_answers() re-reads 40 PDF pages, so cache it on disk."""
    if not rebuild and _ANSWER_CACHE.exists():
        return json.loads(_ANSWER_CACHE.read_text(encoding="utf-8"))
    answers = build_answers()
    _ANSWER_CACHE.parent.mkdir(parents=True, exist_ok=True)
    _ANSWER_CACHE.write_text(json.dumps(answers, indent=1, ensure_ascii=False,
                                        sort_keys=True), encoding="utf-8")
    return answers


# ---------------------------------------------------------------------------
# Figure geometry
# ---------------------------------------------------------------------------

def _seg(obj):
    return {
        "x0": round(obj["x0"], 1), "x1": round(obj["x1"], 1),
        "y0": round(obj["top"], 1), "y1": round(obj["bottom"], 1),
    }


def figures_on_page(page, want_problem=None):
    """Every figure on the page, as caption + bbox + labels + geometry.

    A figure is located from its 'Figura N.M' caption, then grown upward
    within the caption's own column until the geometry runs out."""
    figs = []
    for box in column_boxes(page):
        crop = page.crop(box)
        words = crop.extract_words(x_tolerance=1, y_tolerance=3)
        # caption anchors. "Figura" must be the FIRST word on its row - a
        # statement that merely mentions "...na Figura 9.56..." is not a
        # caption, and treating it as one pulls in a dozen phantom figures
        # per page.
        for w in words:
            if w["text"] != "Figura":
                continue
            cap_top = w["top"]
            same_row = sorted((x for x in words if abs(x["top"] - cap_top) < 4),
                              key=lambda x: x["x0"])
            if not same_row or same_row[0]["text"] != "Figura":
                continue
            caption = " ".join(x["text"] for x in same_row)
            cm = CAPTION_RE.search(caption)
            if not cm:
                continue
            fig_num = "%s.%s" % (cm.group(1), cm.group(2))
            fm = CAPTION_FOR_RE.search(caption)
            for_problem = "%s.%s" % (fm.group(1), fm.group(2)) if fm else None
            if want_problem and for_problem != want_problem:
                continue

            # Grow upward, but stop at the nearest problem marker above the
            # caption - that is where the previous problem's text begins and
            # this figure certainly ends.
            ceiling = max(0, cap_top - FIG_MAX_HEIGHT)
            for text, top in column_lines(page, box):
                if top < cap_top - 6 and PROBLEM_RE.match(text) and top > ceiling:
                    ceiling = top
            band = (box[0], ceiling, box[2], cap_top - 2)
            sub = page.crop(band)
            geo = list(sub.lines) + list(sub.rects) + list(sub.curves)
            if len(geo) < MIN_FIG_ELEMENTS:
                continue
            x0 = min(g["x0"] for g in geo)
            x1 = max(g["x1"] for g in geo)
            y0 = min(g["top"] for g in geo)
            y1 = max(g["bottom"] for g in geo)

            # Trim any statement prose that sits between the previous problem
            # marker and the top of the drawing. Circuit labels are short and
            # scattered; prose is many words spanning most of the column.
            col_w = box[2] - box[0]
            geo_top = y0
            for text, top in column_lines(page, box):
                # only prose ABOVE the drawing may raise the ceiling; a wide
                # label row inside the figure must never clip its own top
                if not (ceiling <= top < geo_top):
                    continue
                words_in_row = [x for x in words if abs(x["top"] - top) < 4]
                if len(words_in_row) < 6:
                    continue
                span = max(x["x1"] for x in words_in_row) - min(x["x0"] for x in words_in_row)
                if span > 0.55 * col_w:
                    y0 = max(y0, max(x["bottom"] for x in words_in_row) + 2)

            # Generous horizontal padding: source/meter labels (v_s, +/-) sit
            # just outside the stroked geometry and get clipped otherwise.
            bbox = (max(box[0], x0 - 12), max(0, y0 - 6),
                    min(box[2], x1 + 12), min(page.height, y1 + 6))
            if bbox[3] - bbox[1] < 20 or bbox[2] - bbox[0] < 20:
                continue
            tight = page.crop(bbox)

            labels = []
            for lw in tight.extract_words(x_tolerance=1, y_tolerance=3):
                txt = normalize(lw["text"])
                if not txt:
                    continue
                labels.append({"text": txt,
                               "x": round(lw["x0"], 1), "y": round(lw["top"], 1)})
            figs.append({
                "figure": fig_num,
                "for_problem": for_problem,
                "caption": caption,
                "bbox": [round(v, 1) for v in bbox],
                "labels": labels,
                "lines": [_seg(o) for o in tight.lines],
                "rects": [_seg(o) for o in tight.rects],
                "curves": [_seg(o) for o in tight.curves],
            })
    return figs


# ---------------------------------------------------------------------------
# Statement text
# ---------------------------------------------------------------------------

def statement_for(page, num):
    """Text of one problem: from its own '<num>' marker down to whatever
    marker comes next in the same column."""
    for box in column_boxes(page):
        lines = column_lines(page, box)
        starts = []
        for idx, (text, _top) in enumerate(lines):
            if PROBLEM_RE.match(text) and text.split()[0].rstrip(".") == num:
                starts.append(idx)
                continue
            m = PROBLEM_RE.match(text)
            if m and "%s.%s" % (m.group(1), m.group(2)) == num:
                starts.append(idx)
        if not starts:
            continue
        start = starts[-1]
        body = []
        for text, _top in lines[start:]:
            if body and PROBLEM_RE.match(text):
                break
            if text.startswith("Figura "):
                continue
            body.append(text)
        if body:
            body[0] = body[0][len(num):].strip()
        return " ".join(body).strip()
    return None


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def extract(nums, out_dir, crop=False, answers=None):
    pdf = _open()
    index = load_index()
    answers = answers if answers is not None else load_answers()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for num in nums:
        entry = index.get(num)
        if not entry:
            print("!! %s nao encontrado no indice" % num)
            continue
        page = pdf.pages[entry["pdf_page"] - 1]
        figs = figures_on_page(page, want_problem=num)
        if not figs:
            # a figure can sit on the facing page
            for delta in (1, -1):
                nb = entry["pdf_page"] + delta
                if 1 <= nb <= len(pdf.pages):
                    figs = figures_on_page(pdf.pages[nb - 1], want_problem=num)
                    if figs:
                        break
        ans = answers.get(num)
        data = {
            "num": num,
            "chapter": entry["chapter"],
            "pdf_page": entry["pdf_page"],
            "statement_raw": normalize(statement_for(page, num)),
            "figures": figs,
            "answer": normalize(ans["text"]) if ans else None,
            "answer_confidence": (ans["votes"] / ans["seen"]) if ans else 0.0,
            "answer_available": bool(ans),
        }
        target = out_dir / ("p%s.json" % num.replace(".", "_"))
        target.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        written.append(target)
        print("%-7s pag %-4d figuras=%d resposta=%s -> %s"
              % (num, entry["pdf_page"], len(figs),
                 "sim" if ans else "NAO(par?)", target.name))

        if crop and figs:
            for k, f in enumerate(figs):
                img = page.crop(f["bbox"]).to_image(resolution=200)
                png = out_dir / ("p%s_fig%d.png" % (num.replace(".", "_"), k))
                img.save(str(png))
                print("        crop -> %s (%d KB)" % (png.name, png.stat().st_size // 1024))
    return written


def list_chapter(ch, answers=None):
    index = load_index()
    answers = answers if answers is not None else load_answers()
    nums = sorted((n for n, e in index.items() if e["chapter"] == ch),
                  key=lambda n: int(n.split(".")[1]))
    print("cap %d: %d problemas" % (ch, len(nums)))
    print("%-8s %-6s %-8s" % ("prob", "pag", "gabarito"))
    for n in nums:
        print("%-8s %-6d %-8s" % (n, index[n]["pdf_page"],
                                  "sim" if n in answers else "-"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--build-index", action="store_true")
    ap.add_argument("--build-answers", action="store_true")
    ap.add_argument("--chapter", type=int)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--problems")
    ap.add_argument("--out", default=".ai-tasks/intake")
    ap.add_argument("--crop", action="store_true")
    args = ap.parse_args()

    if args.build_index:
        build_index()
        load_answers(rebuild=True)
        return
    if args.build_answers:
        a = load_answers(rebuild=True)
        print("gabarito: %d respostas -> %s" % (len(a), _ANSWER_CACHE))
        return
    if args.list:
        if not args.chapter:
            raise SystemExit("--list exige --chapter N")
        list_chapter(args.chapter)
        return
    if args.problems:
        nums = [s.strip() for s in args.problems.split(",") if s.strip()]
        extract(nums, args.out, crop=args.crop)
        return
    if args.chapter:
        index = load_index()
        nums = sorted((n for n, e in index.items() if e["chapter"] == args.chapter),
                      key=lambda n: int(n.split(".")[1]))
        extract(nums, args.out, crop=args.crop)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
