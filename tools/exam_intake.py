"""Render the explicitly authorized exam PDFs, with source fingerprints."""
import hashlib
import json
from pathlib import Path
import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'PROVAS/NOVAS_PROVAS'
OUT = ROOT / 'tmp/exam-intake'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for doc_index, path in enumerate(sorted(SOURCE.glob('*.pdf')), 1):
        doc = fitz.open(str(path))
        stem = '%02d' % doc_index
        pages = []
        for i, page in enumerate(doc):
            target = OUT / ('%s-p%02d.png' % (stem, i+1))
            page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False).save(str(target))
            pages.append(target)
        for first in range(0, len(pages), 4):
            sheet = Image.new('RGB', (1200, 1720), 'white')
            draw = ImageDraw.Draw(sheet)
            for j, page_path in enumerate(pages[first:first+4]):
                im = Image.open(page_path); im.thumbnail((590, 820))
                x, y = (j % 2)*600, (j//2)*860
                draw.text((x+6, y+4), '%s / PDF page %d' % (stem, first+j+1), fill='black')
                sheet.paste(im, (x, y+25))
            sheet.save(OUT / ('%s-contact-%02d.png' % (stem, first//4+1)))
        manifest.append(dict(index=doc_index, document=path.name, pages=len(doc),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        print(stem, path.name, len(doc), 'pages')
    (OUT/'sources.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')

if __name__ == '__main__':main()
