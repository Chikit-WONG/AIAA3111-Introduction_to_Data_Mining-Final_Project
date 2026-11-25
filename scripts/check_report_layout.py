"""Check Word PDF pagination and measure text baselines above the A4 body margin."""
import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
POINTS_PER_MM = 72 / 25.4
BODY_MARGIN_PT = 72.0


def inspect_page(page, number):
    baselines = []

    def visit(text, canvas, matrix, font, size):
        y = matrix[4] * canvas[1] + matrix[5] * canvas[3] + canvas[5]
        text = " ".join(text.split())
        # Word also puts a page number below the body. The six-point
        # allowance retains body descenders and the caption baselines.
        if text and font and "TimesNewRoman" in str(font.get("/BaseFont", "")) and y >= BODY_MARGIN_PT - 6:
            baselines.append((round(y, 2), text))

    page.extract_text(visitor_text=visit)
    if not baselines:
        raise ValueError(f"No Times New Roman body text on page {number}.")
    width, height = (float(d) / POINTS_PER_MM for d in (page.mediabox.width, page.mediabox.height))
    if abs(width - 210) > 0.3 or abs(height - 297) > 0.3:
        raise ValueError(f"Page {number} is {width:.2f} × {height:.2f} mm. Expected A4.")
    first_y = max(y for y, _ in baselines)
    first = " ".join(t for y, t in baselines if abs(y - first_y) < 0.7)
    last_y = min(y for y, _ in baselines)
    last = " ".join(t for y, t in baselines if abs(y - last_y) < 0.7)
    return {
        "page": number,
        "first_line": first,
        "last_line": last,
        "last_baseline_above_bottom_margin_mm": round((last_y - BODY_MARGIN_PT) / POINTS_PER_MM, 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=ROOT.parent / (ROOT.name + "-Report"))
    parser.add_argument("--max-gap-mm", type=float, default=8.0,
                        help="Maximum extra baseline gap on the last main-text page.")
    args = parser.parse_args()
    report = args.report_dir.resolve()
    pages = [inspect_page(page, n) for n, page in enumerate(PdfReader(report / "Report.pdf").pages, 1)]
    starts = [p["page"] for p in pages if re.fullmatch(r"(?:\d+\.?\s*)?Disclosures", p["first_line"], re.I)]
    if starts != [11]:
        raise ValueError(f"Disclosures should begin page 11. Observed page(s) {starts}.")
    gap = pages[9]["last_baseline_above_bottom_margin_mm"]
    if not -0.5 <= gap <= args.max_gap_mm:
        raise ValueError(f"Page 10 ends {gap:.2f} mm above the body margin, measured at the last baseline.")
    result = {
        "main_text_pages": 10, "total_pdf_pages": len(pages), "bottom_margin_mm": 25.4,
        "scope": "Times New Roman text including captions and table cells. Inspect the rendered PDF for graphics and ink edges.",
        "pages": pages,
    }
    output = report / "build" / "layout_check.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"10 main pages, {len(pages)} total. Last main-text baseline: {gap:.2f} mm above the 25.4 mm margin.")
    for p in pages:
        print(f"Page {p['page']:>2}: {p['last_baseline_above_bottom_margin_mm']:>5.1f} mm  {p['last_line'][:76]}")


if __name__ == "__main__":
    main()
