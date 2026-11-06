"""Check the 10-page main text and back-matter layout after a local PDF build.

Uses Latin Modern text baselines to measure unused space above the 21 mm
bottom margin. This does not replace visual inspection of figures and pages.
"""
from pathlib import Path
import argparse
import json

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=ROOT.parent / (ROOT.name + "-Report"))
    parser.add_argument("--max-gap-mm", type=float, default=8.0)
    args = parser.parse_args()
    report = args.report_dir.resolve()
    reader = PdfReader(report / "Report.pdf")
    records = []
    back_matter = []
    found_disclosure = False
    for number, page in enumerate(reader.pages, 1):
        positions = []

        def visitor(text, cm, tm, font, size):
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            # Exclude page-number footers and figure-internal fonts.
            if text.strip() and y > 45 and font and "LM" in str(font.get("/BaseFont", "")):
                positions.append((text.strip(), y))

        text = page.extract_text(visitor_text=visitor)
        if text.lstrip().startswith("6 Disclosures"):
            found_disclosure = True
        if not positions:
            raise AssertionError(f"No manuscript text found on page {number}")
        last, y = min(positions, key=lambda item: item[1])
        target = back_matter if found_disclosure else records
        target.append({
            "page": number,
            "last_text": last,
            "last_baseline_from_bottom_mm": round(y * 25.4 / 72, 3),
            "unused_height_above_bottom_margin_mm": round(y * 25.4 / 72 - 21, 3),
        })

    assert found_disclosure, "Cannot identify the separate Disclosures section"
    assert len(records) == 10, f"Expected 10 main-text pages, found {len(records)}"
    for record in records:
        gap = record["unused_height_above_bottom_margin_mm"]
        assert -.5 <= gap <= args.max_gap_mm, f"Check page {record['page']}: {gap} mm baseline gap"
    assert abs(records[-1]["unused_height_above_bottom_margin_mm"]) <= 1.0, "Page 10 does not reach the body bottom"
    for record in back_matter:
        gap = record["unused_height_above_bottom_margin_mm"]
        assert -.5 <= gap <= args.max_gap_mm, f"Check back-matter page {record['page']}: {gap} mm baseline gap"
    result = {
        "status": "passed",
        "total_pdf_pages": len(reader.pages),
        "main_text_pages": len(records),
        "bottom_margin_mm": 21,
        "scope": "Latin Modern manuscript baselines; inspect rendered pages separately",
        "pages": records,
        "back_matter_pages": back_matter,
    }
    output = report / "build/layout_check.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Passed: 10 main-text pages; largest extra baseline gap {max(x['unused_height_above_bottom_margin_mm'] for x in records):.1f} mm; page 10 gap {records[-1]['unused_height_above_bottom_margin_mm']:.1f} mm.")
    print(f"Back matter: {len(back_matter)} pages; largest extra baseline gap {max(x['unused_height_above_bottom_margin_mm'] for x in back_matter):.1f} mm.")
    print(output)


if __name__ == "__main__":
    main()
