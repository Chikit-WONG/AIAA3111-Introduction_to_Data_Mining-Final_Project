"""Vector-first poster canvas: one scene -> SVG + true-size PDF + PDF previews."""
from pathlib import Path
from html import escape
import base64
import math
import os
from PIL import Image
from reportlab.pdfgen.canvas import Canvas as PdfCanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import toColor
from reportlab.lib.utils import ImageReader
import pymupdf

ROOT = Path(__file__).resolve().parent
UNIT_PT = 72 / 25.4 / 4  # four design units per physical millimetre
FONTS = {
    'regular': ('PosterArial', 'arial.ttf', 'Arial, sans-serif', 400),
    'bold': ('PosterArialBold', 'arialbd.ttf', 'Arial, sans-serif', 700),
    'mono': ('PosterConsolas', 'consola.ttf', 'Consolas, monospace', 400),
    'cjk': ('PosterYaHei', 'msyh.ttc', 'Microsoft YaHei, sans-serif', 400),
    'cjkbold': ('PosterYaHeiBold', 'msyhbd.ttc', 'Microsoft YaHei, sans-serif', 700),
}
FONT_DIR = Path(os.environ.get('POSTER_FONT_DIR', r'C:\Windows\Fonts'))
for name, filename, _, _ in FONTS.values():
    font_path = FONT_DIR / filename
    if not font_path.is_file():
        raise FileNotFoundError(f'Missing font: {font_path}. See poster/README.md and POSTER_FONT_DIR.')
    pdfmetrics.registerFont(TTFont(name, str(font_path), subfontIndex=0))
CAPS = {'butt': 0, 'round': 1, 'square': 2}


def measure(value, size, style='regular'):
    return pdfmetrics.stringWidth(value, FONTS[style][0], size)


def missing_glyphs(value, style='regular'):
    """Characters the chosen font cannot draw (they would print as empty boxes)."""
    glyphs = pdfmetrics.getFont(FONTS[style][0]).face.charToGlyph
    return sorted({ch for ch in value if ord(ch) not in glyphs})


class Scene:
    def __init__(self, width=3200, height=4000):
        self.width, self.height = width, height
        self.elements = []
        self.warnings = []
        self.tag = 'page'

    def add(self, **item):
        item['tag'] = self.tag
        self.elements.append(item)

    def rect(self, x, y, w, h, fill='none', stroke='#202020', sw=2, r=0, dash=None):
        """Rectangle; r rounds all four corners, dash is an optional (on, off) pattern."""
        self.add(kind='rect', x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, sw=sw,
                 r=max(0, min(r, w / 2, h / 2)), dash=dash)

    def line(self, points, stroke='#202020', sw=2, cap='butt', dash=None):
        self.add(kind='line', points=points, stroke=stroke, sw=sw, cap=cap, dash=dash)

    def polygon(self, points, fill='#2463B5'):
        self.add(kind='polygon', points=points, fill=fill)

    def circle(self, x, y, r, fill='#2463B5', stroke='none', sw=0):
        self.add(kind='circle', x=x, y=y, r=r, fill=fill, stroke=stroke, sw=sw)

    def text(self, x, y, value, size=34, style='regular', fill='#202020', anchor='start', max_width=None, vertical=False):
        width = measure(value, size, style)
        if max_width is not None and width > max_width + 0.5:
            self.warnings.append(dict(type='text_too_wide', tag=self.tag, value=value, width=round(width, 1), available=max_width))
        missing = missing_glyphs(value, style)
        if missing:
            self.warnings.append(dict(type='missing_glyph', tag=self.tag, value=value, characters=missing, style=style))
        xx = x - (width if anchor == 'end' else width / 2 if anchor == 'middle' else 0)
        bbox = [xx, y - size * 0.83, xx + width, y + size * 0.2]
        if vertical:
            # Rotate the horizontal bounds a quarter turn around the text anchor, bottom to top.
            left, top, right, bottom = bbox
            bbox = [x + top - y, y - (right - x), x + bottom - y, y - (left - x)]
        self.add(kind='text', x=x, y=y, value=value, size=size, style=style, fill=fill, anchor=anchor,
                 bbox=bbox, vertical=vertical)

    def paragraph(self, x, y, value, width, size=34, leading=None, style='regular', fill='#202020'):
        leading = leading or size * 1.33
        lines, current = [], ''
        for word in value.split():
            candidate = word if not current else current + ' ' + word
            if current and measure(candidate, size, style) > width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        for n, line in enumerate(lines):
            self.text(x, y + n * leading, line, size, style, fill, max_width=width)
        return y + len(lines) * leading

    def image(self, x, y, w, h, path):
        self.add(kind='image', x=x, y=y, w=w, h=h, path=str(path))

    def arrow(self, x1, y1, x2, y2, fill='#2463B5', sw=5, head=16):
        a = math.atan2(y2 - y1, x2 - x1)
        # Stop the shaft inside the head so the tip stays sharp at any stroke width.
        self.line([(x1, y1), (x2 - head * .6 * math.cos(a), y2 - head * .6 * math.sin(a))], fill, sw)
        pts = [(x2, y2)] + [(x2 - head * math.cos(a) + side * head * .48 * math.sin(a),
                            y2 - head * math.sin(a) - side * head * .48 * math.cos(a)) for side in [-1, 1]]
        self.polygon(pts, fill)

    def export_svg(self, path):
        parts = [f'<rect width="{self.width}" height="{self.height}" fill="white"/>']
        for e in self.elements:
            k = e['kind']
            dash = f' stroke-dasharray="{e["dash"][0]} {e["dash"][1]}"' if e.get('dash') else ''
            if k == 'rect':
                radius = f' rx="{e["r"]}" ry="{e["r"]}"' if e['r'] else ''
                parts.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}"{radius} fill="{e["fill"]}" stroke="{e["stroke"]}" stroke-width="{e["sw"]}"{dash}/>')
            elif k == 'circle':
                parts.append(f'<circle cx="{e["x"]}" cy="{e["y"]}" r="{e["r"]}" fill="{e["fill"]}" stroke="{e["stroke"]}" stroke-width="{e["sw"]}"/>')
            elif k in ('line', 'polygon'):
                pts = ' '.join(f'{round(x, 2)},{round(y, 2)}' for x, y in e['points'])
                if k == 'line':
                    parts.append(f'<polyline points="{pts}" fill="none" stroke="{e["stroke"]}" stroke-width="{e["sw"]}" stroke-linecap="{e["cap"]}" stroke-linejoin="round"{dash}/>')
                else:
                    parts.append(f'<polygon points="{pts}" fill="{e["fill"]}"/>')
            elif k == 'text':
                _, _, family, weight = FONTS[e['style']]
                rotation = f' transform="rotate(-90 {e["x"]} {e["y"]})"' if e['vertical'] else ''
                parts.append(f'<text x="{e["x"]}" y="{e["y"]}"{rotation} xml:space="preserve" font-family="{family}" font-size="{e["size"]}" font-weight="{weight}" fill="{e["fill"]}" text-anchor="{e["anchor"]}">{escape(e["value"])}</text>')
            else:
                raw = base64.b64encode(Path(e['path']).read_bytes()).decode('ascii')
                parts.append(f'<image x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{raw}"/>')
        prefix = f'<svg xmlns="http://www.w3.org/2000/svg" width="800mm" height="1000mm" viewBox="0 0 {self.width} {self.height}"><title>Beyond Frequent Co-Purchases - AIAA 3111 Group 11</title>'
        path.write_text(prefix + ''.join(parts) + '</svg>', encoding='utf-8')

    def export_pdf(self, path):
        pdf = PdfCanvas(str(path), pagesize=(self.width * UNIT_PT, self.height * UNIT_PT),
                        pageCompression=1, initialFontName=FONTS['regular'][0])
        pdf.setTitle('Beyond Frequent Co-Purchases | AIAA 3111 Group 11')
        pdf.setAuthor('Chi Kit WONG; Yuxuan OUYANG; Zhicheng SUN')
        pdf.setSubject('800 x 1000 mm portrait research poster with editable vector figures')
        pdf.setLineJoin(1)
        for e in self.elements:
            k = e['kind']
            if e.get('dash'):
                pdf.setDash([v * UNIT_PT for v in e['dash']])
            if k in ('rect', 'circle'):
                fill = e['fill'] != 'none'
                stroke = e['stroke'] != 'none'
                if fill:
                    pdf.setFillColor(toColor(e['fill']))
                if stroke:
                    pdf.setStrokeColor(toColor(e['stroke']))
                    pdf.setLineWidth(e['sw'] * UNIT_PT)
                if k == 'rect' and e['r']:
                    pdf.roundRect(e['x'] * UNIT_PT, (self.height - e['y'] - e['h']) * UNIT_PT, e['w'] * UNIT_PT,
                                  e['h'] * UNIT_PT, e['r'] * UNIT_PT, fill=int(fill), stroke=int(stroke))
                elif k == 'rect':
                    pdf.rect(e['x'] * UNIT_PT, (self.height - e['y'] - e['h']) * UNIT_PT, e['w'] * UNIT_PT, e['h'] * UNIT_PT, fill=int(fill), stroke=int(stroke))
                else:
                    pdf.circle(e['x'] * UNIT_PT, (self.height - e['y']) * UNIT_PT, e['r'] * UNIT_PT, fill=int(fill), stroke=int(stroke))
            elif k in ('line', 'polygon'):
                p = pdf.beginPath()
                pts = e['points']
                p.moveTo(pts[0][0] * UNIT_PT, (self.height - pts[0][1]) * UNIT_PT)
                for x, y in pts[1:]:
                    p.lineTo(x * UNIT_PT, (self.height - y) * UNIT_PT)
                if k == 'line':
                    pdf.setStrokeColor(toColor(e['stroke']))
                    pdf.setLineWidth(e['sw'] * UNIT_PT)
                    pdf.setLineCap(CAPS[e['cap']])
                    pdf.drawPath(p, stroke=1, fill=0)
                    pdf.setLineCap(0)
                else:
                    p.close()
                    pdf.setFillColor(toColor(e['fill']))
                    pdf.drawPath(p, stroke=0, fill=1)
            elif k == 'text':
                pdf.setFillColor(toColor(e['fill']))
                pdf.setFont(FONTS[e['style']][0], e['size'] * UNIT_PT)
                x, y = e['x'] * UNIT_PT, (self.height - e['y']) * UNIT_PT
                if e['vertical']:
                    pdf.saveState()
                    pdf.translate(x, y)
                    pdf.rotate(90)
                    x, y = 0, 0
                if e['anchor'] == 'middle':
                    pdf.drawCentredString(x, y, e['value'])
                elif e['anchor'] == 'end':
                    pdf.drawRightString(x, y, e['value'])
                else:
                    pdf.drawString(x, y, e['value'])
                if e['vertical']:
                    pdf.restoreState()
            else:
                with Image.open(e['path']) as im:
                    scale = min(e['w'] / im.width, e['h'] / im.height)
                    iw, ih = im.width * scale, im.height * scale
                xx, yy = e['x'] + (e['w'] - iw) / 2, e['y'] + (e['h'] - ih) / 2
                pdf.drawImage(ImageReader(e['path']), xx * UNIT_PT, (self.height - yy - ih) * UNIT_PT, iw * UNIT_PT, ih * UNIT_PT, mask='auto')
            if e.get('dash'):
                pdf.setDash()
        pdf.showPage()
        pdf.save()

    def validate(self):
        text_items = [e for e in self.elements if e['kind'] == 'text']
        outside = []
        for e in text_items:
            x0, y0, x1, y1 = e['bbox']
            if x0 < 35 or y0 < 20 or x1 > self.width - 35 or y1 > self.height - 25:
                outside.append(dict(tag=e['tag'], value=e['value'], bbox=e['bbox']))
        overlaps = []
        for i, a in enumerate(text_items):
            a0, b0, a1, b1 = a['bbox']
            for b in text_items[i + 1:]:
                c0, d0, c1, d1 = b['bbox']
                if min(a1, c1) - max(a0, c0) > 3 and min(b1, d1) - max(b0, d0) > 5:
                    overlaps.append(dict(a=a['value'], b=b['value'], a_tag=a['tag'], b_tag=b['tag']))
        return dict(text_nodes=len(text_items), image_nodes=sum(e['kind'] == 'image' for e in self.elements),
                    width_warnings=self.warnings, text_outside_page=outside, text_overlaps=overlaps)


def render_and_check(pdf_path, out_dir, required, forbidden=(), logo_images=0, crops=None):
    """Check the print PDF (size, text, fonts, raster policy) and write previews and detail crops."""
    doc = pymupdf.open(pdf_path)
    assert len(doc) == 1
    page = doc[0]
    width_mm, height_mm = page.rect.width / 72 * 25.4, page.rect.height / 72 * 25.4
    assert abs(width_mm - 800) < .05 and abs(height_mm - 1000) < .05
    extracted = page.get_text()
    for value in required:
        assert value in extracted, value
    for value in forbidden:
        assert value not in extracted, value
    # Every figure is vector. The university logo is the only raster allowed, and it must print sharply.
    images = page.get_image_info()
    assert len(images) == logo_images, f'Expected {logo_images} raster image(s), found {len(images)}'
    logo_dpi = [round(image['width'] / ((image['bbox'][2] - image['bbox'][0]) / 72)) for image in images]
    assert all(dpi >= 300 for dpi in logo_dpi), f'Logo resolution too low for print: {logo_dpi} dpi'
    fonts = page.get_fonts()
    assert fonts and all(doc.extract_font(font[0])[3] for font in fonts), 'Print fonts must be embedded'
    for width, name in [(1600, 'poster_preview.png'), (3200, 'poster_detail.png')]:
        zoom = width / page.rect.width
        page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False).save(out_dir / name)
    detail = Image.open(out_dir / 'poster_detail.png')
    for label, box in (crops or {}).items():
        detail.crop(box).save(out_dir / 'qa' / (label + '.png'))
    (out_dir / 'qa/pdf_text.txt').write_text(extracted, encoding='utf-8')
    return dict(page_count=1, physical_mm=[round(width_mm, 3), round(height_mm, 3)],
                required_text_present=True, raster_images=len(images), logo_dpi=logo_dpi,
                embedded_fonts=len(fonts))
