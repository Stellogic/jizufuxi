from __future__ import annotations

from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tmp" / "pdfs" / "presentation_pages"
OUT.mkdir(parents=True, exist_ok=True)

pdf = ROOT / "演示文稿48(3).pdf"
doc = fitz.open(pdf)
for index, page in enumerate(doc, start=1):
    pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
    path = OUT / f"page_{index:02d}.png"
    pix.save(path)
    print(path)
