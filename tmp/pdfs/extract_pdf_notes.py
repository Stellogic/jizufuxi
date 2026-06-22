from __future__ import annotations

import json
import math
from pathlib import Path

import fitz  # PyMuPDF


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tmp" / "pdfs"
PDFS = [
    ROOT / "计算机组成原理习题解答1(2).pdf",
    ROOT / "计算机组成原理习题解答2(2).pdf",
    ROOT / "演示文稿48(3).pdf",
]


def is_yellow(color: tuple[float, ...] | None) -> bool:
    if not color or len(color) < 3:
        return False
    r, g, b = color[:3]
    # Accept bright yellow and marker-like yellow-green fills.
    return r >= 0.75 and g >= 0.65 and b <= 0.35 and (r + g - b) >= 1.2


def overlap_ratio(a: fitz.Rect, b: fitz.Rect) -> float:
    inter = a & b
    if inter.is_empty:
        return 0.0
    area = max(1.0, a.get_area())
    return inter.get_area() / area


def merge_text_from_words(words: list[tuple]) -> str:
    if not words:
        return ""
    words = sorted(words, key=lambda w: (round(w[1] / 3) * 3, w[0]))
    lines: list[list[tuple]] = []
    for word in words:
        y_mid = (word[1] + word[3]) / 2
        placed = False
        for line in lines:
            existing_mid = sum((w[1] + w[3]) / 2 for w in line) / len(line)
            if abs(y_mid - existing_mid) <= 4:
                line.append(word)
                placed = True
                break
        if not placed:
            lines.append([word])
    chunks = []
    for line in lines:
        line = sorted(line, key=lambda w: w[0])
        chunks.append(" ".join(str(w[4]) for w in line))
    return "\n".join(chunks)


def nearby_words(page: fitz.Page, rect: fitz.Rect) -> str:
    words = page.get_text("words", sort=True)
    hits = []
    padded = fitz.Rect(rect)
    padded.x0 -= 2
    padded.y0 -= 2
    padded.x1 += 2
    padded.y1 += 2
    for word in words:
        wr = fitz.Rect(word[:4])
        if overlap_ratio(wr, padded) >= 0.2 or wr.intersects(padded):
            hits.append(word)
    return merge_text_from_words(hits)


def drawing_rects(drawings: list[dict]) -> list[fitz.Rect]:
    rects: list[fitz.Rect] = []
    for drawing in drawings:
        fill = drawing.get("fill")
        color = drawing.get("color")
        if not (is_yellow(fill) or is_yellow(color)):
            continue
        rect = drawing.get("rect")
        if rect:
            r = fitz.Rect(rect)
            if r.width > 3 and r.height > 3:
                rects.append(r)
        for item in drawing.get("items", []):
            if not item:
                continue
            op = item[0]
            if op == "re" and len(item) >= 2:
                r = fitz.Rect(item[1])
                if r.width > 3 and r.height > 3:
                    rects.append(r)
    return rects


def unique_rects(rects: list[fitz.Rect]) -> list[fitz.Rect]:
    result: list[fitz.Rect] = []
    for rect in sorted(rects, key=lambda r: (r.y0, r.x0, r.y1, r.x1)):
        if any(abs(rect.x0 - old.x0) < 1 and abs(rect.y0 - old.y0) < 1 and abs(rect.x1 - old.x1) < 1 and abs(rect.y1 - old.y1) < 1 for old in result):
            continue
        result.append(rect)
    return result


def extract_annots(page: fitz.Page) -> list[dict]:
    items = []
    annot = page.first_annot
    while annot:
        rect = annot.rect
        subtype = annot.type[1] if annot.type else ""
        text = nearby_words(page, rect)
        items.append(
            {
                "type": subtype,
                "rect": [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
                "content": annot.info.get("content", ""),
                "text": text,
            }
        )
        annot = annot.next
    return items


def page_yellow_pixel_ratio(page: fitz.Page) -> float:
    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), alpha=False)
    data = pix.samples
    count = pix.width * pix.height
    yellow = 0
    for i in range(0, len(data), pix.n):
        r, g, b = data[i], data[i + 1], data[i + 2]
        if r >= 185 and g >= 165 and b <= 110 and r + g - b >= 260:
            yellow += 1
    return yellow / max(1, count)


def extract_pdf(pdf: Path) -> dict:
    doc = fitz.open(pdf)
    pages = []
    highlights = []
    for index, page in enumerate(doc, start=1):
        text = page.get_text("text", sort=True).strip()
        annots = extract_annots(page)
        drawings = drawing_rects(page.get_drawings())
        yellow_rects = unique_rects(drawings)
        yellow_items = []
        for rect in yellow_rects:
            text_in_rect = nearby_words(page, rect)
            if text_in_rect.strip():
                yellow_items.append(
                    {
                        "rect": [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
                        "text": text_in_rect.strip(),
                    }
                )
        yellow_ratio = page_yellow_pixel_ratio(page) if pdf.name.startswith("演示文稿48") else 0.0
        page_info = {
            "page": index,
            "text": text,
            "annotation_highlights": annots,
            "yellow_fill_text": yellow_items,
            "yellow_pixel_ratio": yellow_ratio,
        }
        pages.append(page_info)
        for item in annots:
            if item["type"].lower() == "highlight" or item["text"].strip():
                highlights.append({"page": index, "source": "annotation", **item})
        for item in yellow_items:
            highlights.append({"page": index, "source": "yellow_fill", **item})
    return {
        "file": pdf.name,
        "page_count": len(doc),
        "pages": pages,
        "highlights": highlights,
    }


def compact_md(data: dict) -> str:
    lines = [f"# {data['file']}", "", f"页数: {data['page_count']}", ""]
    lines.append("## 标黄/注释提取")
    if not data["highlights"]:
        lines.append("未检测到可直接提取的高亮注释或黄色填充文字。")
    else:
        for item in data["highlights"]:
            text = item.get("text", "").strip()
            if text:
                lines.append(f"- P{item['page']} [{item['source']}]: {text}")
    lines.append("")
    lines.append("## 分页正文")
    for page in data["pages"]:
        lines.append(f"### P{page['page']}")
        if page.get("yellow_pixel_ratio", 0) > 0:
            lines.append(f"yellow_pixel_ratio={page['yellow_pixel_ratio']:.5f}")
        lines.append(page["text"] or "[无可提取文本]")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    all_data = []
    for pdf in PDFS:
        data = extract_pdf(pdf)
        all_data.append(data)
        stem = pdf.stem
        (OUT / f"{stem}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        (OUT / f"{stem}.md").write_text(compact_md(data), encoding="utf-8")
    summary = []
    for data in all_data:
        summary.append(
            {
                "file": data["file"],
                "page_count": data["page_count"],
                "highlight_count": len(data["highlights"]),
                "text_chars": sum(len(p["text"]) for p in data["pages"]),
                "yellow_pages": [
                    p["page"]
                    for p in data["pages"]
                    if p.get("yellow_pixel_ratio", 0.0) > 0.002 or p["yellow_fill_text"] or p["annotation_highlights"]
                ],
            }
        )
    (OUT / "extraction_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
