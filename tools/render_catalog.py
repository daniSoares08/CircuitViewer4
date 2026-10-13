#!/usr/bin/env python3
"""Render every CV4 figure and text page for visual QA.

Outputs calculator-sized PNGs plus contact sheets under tmp/catalog-render.
This is deliberately independent from the AppVar reader: it exercises the
same authored ops and generated page blocks before the calculator build.
"""

import shutil
import json
import sys
import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import content  # noqa: E402
import cv_render  # noqa: E402
import generate_cv4  # noqa: E402

OUT = ROOT / "tmp" / "catalog-render"
COLOR_NAME = {1: "COL_BLACK", 4: "COL_BLUE", 5: "COL_RED"}


def _contact(paths, target, cols=4, rows=4):
    pages = []
    for start in range(0, len(paths), cols * rows):
        group = paths[start:start + cols * rows]
        sheet = Image.new("RGB", (320 * cols, 240 * rows), "white")
        for idx, path in enumerate(group):
            with Image.open(path) as image:
                sheet.paste(image, ((idx % cols) * 320, (idx // cols) * 240))
        out = target.with_name("%s-%02d.png" % (target.stem, len(pages) + 1))
        sheet.save(out)
        pages.append(out)
    return pages


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', help='Comma-separated IDs; leave previous previews intact')
    args=parser.parse_args()
    selected=set(args.ids.split(',')) if args.ids else None
    OUT.resolve().relative_to((ROOT / 'tmp').resolve())
    if OUT.exists() and selected is None:
        shutil.rmtree(str(OUT))
    figures_dir = OUT / "figures"
    text_dir = OUT / "text"
    figures_dir.mkdir(parents=True,exist_ok=True)
    text_dir.mkdir(parents=True,exist_ok=True)

    _subjects, circuits, _catalog = content.load()
    authored={e['id']:e for e in _catalog}
    bank, generated, _stats = generate_cv4.process_all()
    figure_paths = []
    text_paths = []
    errors = []
    runtime_path = ROOT / 'tmp/live-qa/runtime-pages.json'
    if not runtime_path.exists():
        raise SystemExit('Run tests/test_appvar_live.py before rendering runtime pages')
    runtime = {r['id']: r['pages'] for r in json.loads(runtime_path.read_text(encoding='utf8'))}

    for rec in generated:
        title = rec["title"]
        ex_id = rec["id"]
        if selected is not None and ex_id not in selected:continue
        if ex_id in circuits:
            for op in circuits[ex_id]:
                nums = [v for v in op[1:] if isinstance(v, int) and not isinstance(v, bool)]
                if any(v < 0 or v > 319 for v in nums[::2]):
                    errors.append("%s: coordenada horizontal fora da tela: %r" % (ex_id, op))
            page = {"title": "Circuito", "body": circuits[ex_id]}
            if authored[ex_id].get('engine',{}).get('flags2',0)&8:
                page['title']='Diagrama fasorial'
                page['phasor']=[v for _,v in rec['data']['params'][:2]]
            image = cv_render.render_page(page, rec["content_title"], ex_id, title)
            path = figures_dir / (ex_id + ".png")
            image.save(path)
            figure_paths.append(path)

        blocks = list(rec["data"]["statement"])
        params = rec["data"]["params"]
        for start in range(0, len(params), 7):
            blocks.append({
                "title": "Dados atuais",
                "subtitle": "MODE para editar",
                "result": "",
                "result_y": 0,
                "lines": [
                    (14, 62 + 20 * line_index, 1,
                     "%s = %.7g" % (name, value))
                    for line_index, (name, value)
                    in enumerate(params[start:start + 7])
                ],
            })
        blocks += list(rec["data"]["tail"])
        # Draw actual C-loader steps/results, never frozen author solution text.
        for p in runtime[ex_id]:
            if p['title'] not in ('Resolucao','Resultados atuais'):
                continue
            blocks.append(dict(title=p['title'],subtitle=p['subtitle'],result='',result_y=0,
                lines=[(14,62+20*i,color,text) for i,(text,color) in enumerate(p['lines'])]))
        for idx, block in enumerate(blocks):
            lines = []
            for x, y, color, text in block["lines"]:
                if len(text) > 37:
                    errors.append("%s: texto >37 colunas: %r" % (ex_id, text))
                lines.append((text, x, y, COLOR_NAME[color]))
            page = dict(block)
            page["lines"] = lines
            image = cv_render.render_page(page, rec["content_title"], ex_id, title)
            path = text_dir / ("%s-%02d.png" % (ex_id, idx + 1))
            image.save(path)
            text_paths.append(path)

    contacts = []
    suffix='-selected' if selected is not None else ''
    contacts += _contact(figure_paths, OUT / ("figures-contact%s.png"%suffix))
    contacts += _contact(text_paths, OUT / ("text-contact%s.png"%suffix))
    print("rendered %d figures and %d text pages" % (len(figure_paths), len(text_paths)))
    print("contact sheets: %d -> %s" % (len(contacts), OUT))
    if errors:
        print("LAYOUT INPUT ERRORS:")
        for error in errors:
            print("  " + error)
        return 1
    print("LAYOUT INPUT OK: coordinates and wrapped text fit the calculator page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
