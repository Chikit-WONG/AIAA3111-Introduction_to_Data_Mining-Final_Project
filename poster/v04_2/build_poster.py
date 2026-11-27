"""Publish the V04.2 poster with the original layout and the model-family credits."""
import csv
import hashlib
import json
import runpy
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from reportlab import rl_config

HERE = Path(__file__).resolve().parent
POSTER = HERE.parent
ROOT = POSTER.parent
VERSION = "V04.2"
STEM = "Poster_" + VERSION
DEST = ROOT / "artifacts" / VERSION
SENSITIVITY = "results/tables/basket_size_sensitivity.csv"
SOURCES = [
    "poster/v04_2/build_poster.py", "poster/v04_2/copy.json", "poster/v04_2/README.md",
    "poster/build_poster.py", "poster/scene_engine.py", "poster/poster_data.json",
    "poster/assets/hkustgz_logo.png", "poster/requirements-render.txt",
    "poster/Presentation_Script_EN_ZH.md", SENSITIVITY,
]

sys.path.insert(0, str(POSTER))
from scene_engine import Scene, render_and_check


def monthly_rates(layout):
    with (ROOT / SENSITIVITY).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    months = [r["month"] for r in layout["DATA"]["test_months"]]
    if [r["month"] for r in rows] != months or any(
        int(r["discovered_rules"]) != layout["rule_count"] or r["scope"] != "UK at most 100 products"
        for r in rows
    ):
        raise ValueError("The basket-size sensitivity rows must cover the same four months and frozen cohort.")
    total = layout["test_checks"]
    return {
        "main_retention": f"{layout['test_passes'] / total:.1%}",
        "restricted_retention": f"{sum(int(r['retained_rules']) for r in rows) / total:.1%}",
    }


def revised_scene(layout):
    copy = json.loads((HERE / "copy.json").read_text(encoding="utf-8"))
    caption_one, caption_two = copy["legend"]
    rates = monthly_rates(layout)
    title, first_line, second_line = [line.format(**rates) for line in copy["takeaway"]]
    width = layout["CWD"]
    body = {"size": 37, "style": "regular", "fill": layout["INK"]}
    # Anchor the six text replacements to their existing baselines. All artwork, anchors,
    # font families and other text come directly from the original native scene.
    replacements = {
        ("test_grid", 3016, "start"): (caption_one, width, {}),
        ("test_grid", 3062, "start"): (caption_two, width, {}),
        ("test_grid", 3150, "start"): (title, width - 70, {}),
        ("test_grid", 3202, "start"): (first_line, width - 70, body),
        ("test_grid", 3250, "start"): (second_line, width - 70, body),
        ("footer", 3950, "start"): (copy["credit"], 1860, {}),
    }
    changed_lines = [text for text, _, _ in replacements.values()]
    original = layout["S"]
    scene = Scene(original.width, original.height)
    scene.warnings.extend(original.warnings)
    for item in original.elements:
        key = (item["tag"], item.get("y"), item.get("anchor"))
        revision = replacements.pop(key, None) if item["kind"] == "text" else None
        if revision is None:
            scene.elements.append(item)
            continue
        text, available, overrides = revision
        style = {name: item[name] for name in ("size", "style", "fill", "anchor")}
        style.update(overrides)
        scene.tag = item["tag"]
        scene.text(item["x"], item["y"], text, max_width=available, **style)
    if replacements:
        raise ValueError(f"V04.0 layout anchors missing: {list(replacements)}")
    return scene, changed_lines


def archive(outputs, target):
    assets = {name: (ROOT / name).read_bytes() for name in SOURCES}
    assets.update({dest.relative_to(ROOT).as_posix(): src.read_bytes() for dest, src in outputs.items()})
    assets["README.md"] = assets["poster/v04_2/README.md"]
    assets["poster/README.md"] = b"Shared renderer files. See [the V04.2 guide](v04_2/README.md) for fonts and build instructions.\n"
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in assets.items()}
    assets["source_manifest.json"] = json.dumps(
        {"version": VERSION, "sha256": manifest}, indent=2, sort_keys=True
    ).encode("utf-8")
    with ZipFile(target, "w") as bundle:
        for name, data in sorted(assets.items()):
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, data, compress_type=ZIP_DEFLATED)
    with ZipFile(target) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("The poster source archive did not pass its CRC check.")
    return target


def main():
    rl_config.invariant = True
    # Load the original scene without invoking its PDF/SVG publication entry point.
    layout = runpy.run_path(str(POSTER / "build_poster.py"), run_name="poster_v040_template")
    scene, changed_lines = revised_scene(layout)
    checks = scene.validate()
    if any(checks[k] for k in ("width_warnings", "text_outside_page", "text_overlaps")):
        raise ValueError(json.dumps(checks, indent=2))
    required = [s for s in layout["REQUIRED"] if s != "79.2% test retention"]
    required += ["MEAN MONTHLY TEST RETENTION", "79.2%", "100.0%", "Ineligible (<20)", *changed_lines]
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="poster-v042-", dir=DEST.parent) as temp:
        work = Path(temp)
        (work / "qa").mkdir()
        pdf = work / (STEM + ".pdf")
        svg = work / (STEM + ".svg")
        scene.export_svg(svg)
        scene.export_pdf(pdf)
        physical = render_and_check(pdf, work, required, logo_images=1)
        outputs = {DEST / pdf.name: pdf, DEST / svg.name: svg,
                   DEST / (STEM + "_preview.png"): work / "poster_preview.png"}
        bundle = archive(outputs, work / (STEM + "_source.zip"))
        outputs[DEST / bundle.name] = bundle
        DEST.mkdir(exist_ok=True)
        for target, source in outputs.items():
            source.replace(target)
    print(json.dumps({"version": VERSION, "folder": str(DEST), **checks, **physical}, indent=2))


if __name__ == "__main__":
    main()
