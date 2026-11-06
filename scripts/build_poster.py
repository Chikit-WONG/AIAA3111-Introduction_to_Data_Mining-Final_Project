"""Build the editable vector A1 poster from saved evidence; no mining is rerun."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from statistics import mean, median

import matplotlib
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A0, A1, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
W, H = landscape(A1)
MARGIN, GAP = 64, 40
CW = (W - 2 * MARGIN - 2 * GAP) / 3
COLS = [MARGIN + i * (CW + GAP) for i in range(3)]
INK = HexColor('#102D40')
TEAL = HexColor('#087E83')
TEAL_LIGHT = HexColor('#C7E6E4')
MUTED = HexColor('#536A79')
RULE = HexColor('#D6E1E5')
FAILED = HexColor('#DCE3E8')
AMBER = HexColor('#E1AD50')
WHITE = HexColor('#FFFFFF')
PALE = HexColor('#F1F7F7')
SAND = HexColor('#FAF4E8')
REPOSITORY = 'https://github.com/Chikit-WONG/AIAA3111-Introduction_to_Data_Mining-Final_Project'


def table(name):
    with (ROOT / 'results/tables' / name).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def load_evidence():
    summary = json.loads((ROOT / 'results/summary.json').read_text())
    team = json.loads((ROOT / 'configs/team.json').read_text())
    selection = json.loads((ROOT / 'results/selection.json').read_text())
    profile = json.loads((ROOT / 'results/data_profile.json').read_text())
    monthly = [r for r in table('monthly_retention.csv') if r['split'] == 'test']
    grid = table('threshold_sensitivity.csv')
    observable = {r['configuration']: r for r in table('threshold_evaluability.csv')}
    persistence = {int(r['months_retained']): int(r['rules']) for r in table('stability_distribution.csv')}
    benchmark = table('benchmark.csv')
    n = summary['selected_rules']
    assert len(monthly) == 4 and n == 71
    assert all(int(r['discovered_rules']) == n for r in monthly)
    assert sum(int(r['retained_rules']) for r in monthly) == summary['test_retained_rule_months']
    assert sum(persistence.values()) == n
    assert persistence[4] == summary['rules_retained_all_test_months']
    assert selection['configuration'] == summary['selected_configuration']
    for support in {r['min_support'] for r in benchmark}:
        assert len({r['signature'] for r in benchmark if r['min_support'] == support}) == 1
    return dict(summary=summary, team=team, selection=selection, profile=profile, monthly=monthly,
                grid=grid, observable=observable, persistence=persistence, benchmark=benchmark,
                known=mean(float(r['retention_rate']) for r in table('customer_sensitivity.csv')),
                small=mean(float(r['retention_rate']) for r in table('basket_size_sensitivity.csv')),
                splits=table('splits.csv'))


def register_fonts():
    directory = Path(matplotlib.get_data_path()) / 'fonts/ttf'
    for name, filename in [('Poster', 'DejaVuSans.ttf'), ('Poster-Bold', 'DejaVuSans-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
    pdfmetrics.registerFontFamily('Poster', normal='Poster', bold='Poster-Bold')


class Poster:
    """Top-origin vector primitives and explicit text-bound checks."""
    def __init__(self, output, paper_size):
        page = landscape(A1 if paper_size == 'A1' else A0)
        self.c = canvas.Canvas(str(output), pagesize=page, pageCompression=1, invariant=1)
        self.c.scale(page[0] / W, page[1] / H)
        self.c.setTitle('Beyond Frequent Co-Purchases - AIAA3111 Group 11')
        self.c.setAuthor('Chi Kit WONG; Yuxuan OUYANG; Zhicheng SUN')
        self.c.setSubject('Temporal stability and observability of retail association rules')
        self.boxes = []

    def rect(self, x, top, width, height, fill, stroke=None, radius=0, line=1):
        self.c.setFillColor(fill)
        self.c.setStrokeColor(stroke or fill)
        self.c.setLineWidth(line)
        if radius:
            self.c.roundRect(x, H-top-height, width, height, radius, fill=1, stroke=int(stroke is not None))
        else:
            self.c.rect(x, H-top-height, width, height, fill=1, stroke=int(stroke is not None))

    def line(self, x1, top1, x2, top2, color=RULE, width=1):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(x1, H-top1, x2, H-top2)

    def text(self, value, x, top, size=23, bold=False, color=INK, align='left', width=None):
        font = 'Poster-Bold' if bold else 'Poster'
        actual = pdfmetrics.stringWidth(value, font, size)
        if width is not None and actual > width + .2:
            raise ValueError(f'Text exceeds {width:.1f} pt: {value!r} ({actual:.1f} pt)')
        left = x if align == 'left' else x-actual/2 if align == 'center' else x-actual
        assert left >= -1 and left+actual <= W+1, value
        assert top >= 0 and top+size <= H, value
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawString(left, H-top-size, value)
        self.boxes.append(dict(text=value, x=left, top=top, width=actual, height=size, font_size=size))
        return top+size

    def para(self, value, x, top, width, size=23, leading=None, color=INK, limit=None):
        style = ParagraphStyle('poster', fontName='Poster', fontSize=size,
                               leading=leading or size*1.32, textColor=color)
        p = Paragraph(value, style)
        _, height = p.wrap(width, H)
        if limit is not None and top+height > limit:
            raise ValueError(f'Paragraph exceeds section bottom {limit}: {top+height:.1f}; {value}')
        assert top+height < H
        p.drawOn(self.c, x, H-top-height)
        self.boxes.append(dict(text=value, x=x, top=top, width=width, height=height, font_size=size))
        return top+height

    def section(self, number, title, x):
        self.rect(x, 421, 42, 39, PALE, radius=5)
        self.text(number, x+21, 427, 20, True, TEAL, align='center')
        self.text(title, x+56, 419, 31, True, width=CW-56)
        self.line(x, 477, x+CW, 477)

    def circle(self, x, top, radius, fill):
        self.c.setFillColor(fill)
        self.c.circle(x, H-top, radius, stroke=0, fill=1)

    def save(self):
        self.c.showPage()
        self.c.save()


def header(p, e):
    p.rect(0, 0, W, H, WHITE)
    p.rect(0, 0, W, 220, INK)
    p.rect(0, 214, W, 6, TEAL)
    p.text('Beyond Frequent Co-Purchases', MARGIN, 47, 72, True, WHITE, width=W-2*MARGIN)
    p.text('A Study of Temporal Stability in Retail Association Rules', MARGIN, 132, 31, color=HexColor('#C8DFE7'))
    byline = '   |   '.join(f"{m['name']} ({m['student_id']})" for m in e['team']['members'])
    p.text(byline, MARGIN, 180, 21, color=WHITE)
    p.text('AIAA3111  /  GROUP 11', W-MARGIN, 43, 19, True, TEAL_LIGHT, align='right')
    p.text('Introduction to Data Mining', W-MARGIN, 75, 17, color=TEAL_LIGHT, align='right')
    s = e['summary']
    p.rect(MARGIN, 246, W-2*MARGIN, 136, PALE, radius=8)
    p.rect(MARGIN, 246, 6, 136, TEAL)
    p.text(f"{s['mean_monthly_test_retention']*100:.1f}%", MARGIN+28, 255, 70, True, TEAL)
    p.text('Mean monthly retention', 420, 262, 27, True)
    p.para(f"{s['test_retained_rule_months']} of {s['test_rule_months']} held-out rule-months<br/>pass every evaluation gate.", 420, 307, 585, 23, limit=378)
    for x in (1074, 1702):
        p.line(x, 268, x, 360, HexColor('#BFD4D8'), 1.3)
    p.text(f"{s['rules_retained_all_test_months']} / {s['selected_rules']}", 1110, 257, 53, True)
    p.para('rules pass in all four<br/>held-out months', 1390, 280, 275, 22, limit=368)
    p.text(f"{s['test_evaluation_coverage']*100:.1f}%", 1738, 257, 53, True)
    p.para('of test rule-months<br/>are evaluable', 2010, 280, 275, 22, limit=368)


def method_column(p, e):
    x = COLS[0]
    p.section('01', 'A test of future reliability', x)
    p.para('Do associations found in past orders remain reliable in later months?', x, 498, CW, 28, leading=36, limit=575)
    profile = e['profile']
    p.para(f"<b>{profile['raw_rows']:,}</b> raw line items → <b>{profile['all_country_baskets']:,}</b> cleaned baskets.<br/><b>{profile['uk_baskets']:,} UK invoices</b> define the primary population.", x, 590, CW, 22, limit=653)
    p.line(x+15, 683, x+15, 916, TEAL_LIGHT, 3)
    counts = {name: sum(int(r['orders']) for r in e['splits'] if r['split']==name)
              for name in ('discovery', 'validation', 'test')}
    stages = [
        ('1', 'Discover', 'Dec 2010-May 2011', f"{counts['discovery']:,} orders · Apriori + FP-Growth · length ≤ 3"),
        ('2', 'Select', 'Jun-Jul 2011', f"{counts['validation']:,} orders · Tune on validation only"),
        ('3', 'Freeze & test', 'Aug-Nov 2011', f"{counts['test']:,} orders · 71 fixed rules × four months"),
    ]
    for i, (n, title, dates, note) in enumerate(stages):
        top = 666+i*107
        p.rect(x+42, top, CW-42, 92, PALE, radius=6)
        p.circle(x+15, top+33, 15, TEAL)
        p.text(n, x+15, top+21, 19, True, WHITE, align='center')
        p.text(title, x+61, top+12, 24, True, TEAL)
        p.text(dates, x+CW-20, top+15, 21, color=MUTED, align='right')
        p.text(note, x+61, top+53, 21, width=CW-82)
    p.text('Retained = all four gates pass', x, 994, 27, True)
    th = e['selection']['evaluation_thresholds']
    gates = [(f"≥ {th['evaluation_min_support']*100:g}%", 'monthly support'),
             (f"≥ {th['evaluation_min_confidence']*100:g}%", 'monthly confidence'),
             (f"≥ {th['evaluation_min_lift']:g}", 'monthly lift'),
             (f"≥ {th['evaluation_min_antecedent_count']}", 'antecedent orders')]
    gw = (CW-14)/2
    for i, (value, label) in enumerate(gates):
        gx, gy = x+(i%2)*(gw+14), 1044+(i//2)*96
        p.rect(gx, gy, gw, 82, WHITE, RULE, radius=5)
        p.text(value, gx+17, gy+8, 31, True, TEAL)
        p.text(label, gx+17, gy+49, 20, color=MUTED)
    p.para('All <b>71 frozen rules</b> stay in the denominator. Too little evidence is reported separately from a failed quality threshold.', x, 1242, CW, 23, limit=1340)
    p.text('Audit before mining', x, 1350, 25, True)
    p.para('Use invoice-level product sets; remove duplicate, invalid and non-product lines and cancellations. Keep singleton and missing-ID baskets. Partial Dec 2011 is excluded from testing.', x, 1390, CW, 21, leading=27, limit=1472)


def temporal_chart(p, rows, x):
    p.text('Monthly outcomes for the same 71 rules', x, 511, 23, True)
    left, right, top, bottom = x+52, x+CW-14, 568, 832
    height = bottom-top
    for value in (0, 25, 50, 75, 100):
        yy = bottom-value/100*height
        p.line(left, yy, right, yy)
        p.text(str(value), left-11, yy-10, 18, color=MUTED, align='right')
    p.text('%', left-12, top-33, 18, color=MUTED, align='right')
    step = (right-left)/len(rows)
    for i, r in enumerate(rows):
        cx = left+step*(i+.5)
        retained, evaluable, n = int(r['retained_rules']), int(r['evaluable_rules']), int(r['discovered_rules'])
        width = 100
        p.rect(cx-width/2, top, width, height, FAILED)
        unavailable = height*(n-evaluable)/n
        if unavailable:
            p.rect(cx-width/2, top, width, unavailable, AMBER)
        passed_height = height*retained/n
        p.rect(cx-width/2, bottom-passed_height, width, passed_height, TEAL)
        p.text(f'{retained/n*100:.1f}', cx, bottom-passed_height+14, 25, True, WHITE, align='center')
        month = {'08':'Aug','09':'Sep','10':'Oct','11':'Nov'}[r['month'][-2:]]
        p.text(month, cx, 843, 23, True, align='center')
        p.text(f'{retained}/{n} pass', cx, 880, 19, color=MUTED, align='center')
    legend = [(TEAL,'Retained',x+5), (FAILED,'Quality gate failed',x+175), (AMBER,'Insufficient evidence',x+440)]
    for color, name, lx in legend:
        p.rect(lx, 925, 17, 17, color)
        p.text(name, lx+25, 921, 18, color=MUTED)


def results_column(p, e):
    x = COLS[1]
    p.section('02', 'What survives over time?', x)
    temporal_chart(p, e['monthly'], x)
    p.para('All 71 rules are evaluable in Sep-Nov. The November decline is therefore not a sample-count failure.', x, 966, CW, 22, limit=1032)
    p.text('Persistence across four test months', x, 1050, 27, True)
    counts = e['persistence']
    intermittent = sum(counts.get(n, 0) for n in (1,2,3))
    colors = [TEAL]*counts[4]+[TEAL_LIGHT]*intermittent+[FAILED]*counts[0]
    size, gap = 19, 6
    for i, color in enumerate(colors):
        p.rect(x+(i%18)*(size+gap), 1103+(i//18)*(size+gap), size, size, color, radius=2)
    for i, (color, text) in enumerate([(TEAL,f"{counts[4]} pass all 4"),(TEAL_LIGHT,f'{intermittent} pass 1-3'),(FAILED,f"{counts[0]} pass none")]):
        ly = 1101+i*34
        p.rect(x+476, ly+6, 18, 18, color, radius=2)
        p.text(text, x+507, ly, 21, bold=i==0)
    p.text('Each square is one rule.', x, 1212, 18, color=MUTED)
    p.text('Population choice changes the answer', x, 1258, 27, True)
    data = [('Primary UK invoices', e['summary']['mean_monthly_test_retention'], TEAL),
            ('Customer ID recorded', e['known'], HexColor('#62999F')),
            ('Baskets ≤ 100 products', e['small'], HexColor('#8BAEB2'))]
    for i, (label, value, color) in enumerate(data):
        yy = 1311+i*46
        p.text(label, x, yy, 20)
        p.rect(x+292, yy+2, 325, 23, PALE, radius=2)
        p.rect(x+292, yy+2, 325*value, 23, color, radius=2)
        p.text(f'{value*100:.1f}%', x+CW, yy-2, 22, True, align='right')
    p.text('Mean retention · same 71 rules · descriptive subsets', x, 1451, 18, color=MUTED)


def heat_color(value):
    low, high = HexColor('#EAF4F4'), HexColor('#075F68')
    return Color(*(a+(b-a)*value for a,b in zip((low.red,low.green,low.blue),(high.red,high.green,high.blue))))


def tradeoff_column(p, e):
    x = COLS[2]
    p.section('03', 'The coverage trade-off', x)
    p.text('Test retention (%) and discovered rule count', x, 511, 23, True)
    start, top, cellh = x+91, 596, 107
    cellw = (CW-91)/3
    p.text('Discovery minimum support', start+1.5*cellw, 552, 20, color=MUTED, align='center')
    for j, support in enumerate((.005,.01,.02)):
        p.text(f'{support*100:g}%', start+(j+.5)*cellw, 578, 18, True, align='center')
    p.c.saveState()
    p.c.translate(x+13, H-(top+1.5*cellh))
    p.c.rotate(90)
    p.c.setFont('Poster', 18)
    p.c.setFillColor(MUTED)
    p.c.drawCentredString(0, 0, 'Discovery minimum confidence')
    p.c.restoreState()
    grid = {(float(r['min_support']),float(r['min_confidence'])):r for r in e['grid']}
    for i, conf in enumerate((.3,.5,.7)):
        p.text(f'{conf*100:g}%', x+75, top+i*cellh+38, 20, True, align='right')
        for j, support in enumerate((.005,.01,.02)):
            r = grid[support,conf]
            value = float(r['test_retention'])
            selected = r['configuration']==e['selection']['configuration']
            xx, yy = start+j*cellw, top+i*cellh
            p.rect(xx+3, yy+3, cellw-6, cellh-6, heat_color(value), AMBER if selected else None, radius=3, line=4)
            color = WHITE if value>=.70 else INK
            p.text(f'{value*100:.1f}%', xx+cellw/2, yy+15, 31, True, color, align='center')
            label = f"{int(r['rules']):,} rules"+(' · chosen' if selected else '*' if int(r['rules'])<20 else '')
            p.text(label, xx+cellw/2, yy+63, 18, color=color, align='center', width=cellw-12)
    p.para('<b>*100% retention, only 14 rules.</b> This cohort is below the predeclared minimum of 20 rules.', x, 945, CW, 23, limit=1010)
    p.para('The 71-rule cohort was chosen on <b>Jun-Jul validation only</b>. Test-grid comparisons are descriptive.', x, 1026, CW, 22, limit=1090)
    sparse = e['observable']['s0.005_c0.5']
    p.rect(x, 1110, CW, 140, SAND, radius=6)
    p.text(f"{int(sparse['rules']):,} rules at 0.5% support / 50% confidence", x+18, 1124, 20, True, width=CW-36)
    for value,label,xx in [(float(sparse['test_evaluation_coverage'])*100,'evaluable rule-months',x+19),
                           (float(sparse['test_retention'])*100,'retained rule-months',x+CW/2+12)]:
        p.text(f'{value:.1f}%', xx, 1160, 37, True)
        p.text(label, xx, 1210, 19, color=MUTED)
    p.text('Equivalent mining outputs', x, 1275, 27, True)
    for label,xx,align in [('Min. support',x,'left'),('Apriori',x+382,'right'),('FP-Growth',x+CW,'right')]:
        p.text(label, xx, 1322, 20, True, color=MUTED, align=align)
    p.line(x, 1354, x+CW, 1354)
    for i, support in enumerate((.005,.01,.02)):
        yy = 1364+i*28
        p.text(f'{support*100:g}%', x, yy, 21)
        for algo,xx in [('apriori',x+382),('fpgrowth',x+CW)]:
            seconds = median(float(r['seconds']) for r in e['benchmark'] if r['algorithm']==algo and float(r['min_support'])==support)
            p.text(f'{seconds:.2f} s', xx, yy, 21, align='right')
    peak = e['summary']['benchmark_max_peak_rss_mib']
    p.text('Median of 3 runs · Apriori low-memory · Ryzen 9 7940H', x, 1449, 17.5, color=MUTED)
    p.text(f'Same itemsets/counts · peak worker memory < {int(peak)+1} MiB', x, 1471, 17.5, color=MUTED)


def conclusion_and_footer(p):
    p.rect(MARGIN, 1500, W-2*MARGIN, 94, INK, radius=6)
    p.text('Frequent co-purchases need temporal validation.', MARGIN+23, 1513, 32, True, WHITE)
    p.text('Report retention and observability; choose coverage before examining test results.', MARGIN+23, 1557, 23, color=TEAL_LIGHT)
    p.para('One retailer · Four test months · Dependent rules<br/>No claim of causation or sales uplift.', 1641, 1520, 640, 21, color=WHITE, limit=1587)
    p.text('DATA  Chen (2015), UCI Online Retail · doi:10.24432/C5BW33 · CC BY 4.0', MARGIN, 1611, 16, color=MUTED)
    p.text('METHODS  Agrawal & Srikant (1994); Han et al. (2000); Raschka (2018), MLxtend.', MARGIN, 1633, 16, color=MUTED)
    p.text('AIGC  Codex assisted code, experiments and drafting; team review and revision remain required.', MARGIN, 1655, 16, color=MUTED)
    qrsize, qr_top = 74, 1601
    widget = QrCodeWidget(REPOSITORY, barLevel='M', barBorder=4)
    bounds = widget.getBounds()
    scale = qrsize/(bounds[2]-bounds[0])
    drawing = Drawing(qrsize, qrsize, transform=[scale,0,0,scale,0,0])
    drawing.add(widget)
    renderPDF.draw(drawing, p.c, W-MARGIN-qrsize, H-qr_top-qrsize)
    p.text('Code + evidence', W-MARGIN-qrsize-20, 1614, 21, True, align='right')
    p.text('Scan the project repository', W-MARGIN-qrsize-20, 1647, 16, color=MUTED, align='right')
    p.c.linkURL(REPOSITORY, (W-MARGIN-qrsize,H-qr_top-qrsize,W-MARGIN,H-qr_top), relative=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', choices=('A1','A0'), default='A1')
    parser.add_argument('--output', type=Path, default=ROOT/'artifacts/Poster.pdf')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    register_fonts()
    evidence = load_evidence()
    p = Poster(args.output, args.size)
    header(p, evidence)
    for separator in (COLS[1]-GAP/2, COLS[2]-GAP/2):
        p.line(separator, 421, separator, 1472)
    method_column(p, evidence)
    results_column(p, evidence)
    tradeoff_column(p, evidence)
    conclusion_and_footer(p)
    p.save()
    qa = ROOT/'tmp/poster_qa'
    qa.mkdir(parents=True, exist_ok=True)
    (qa/'poster_layout.json').write_text(json.dumps(dict(size=args.size, vector_only=True, text_boxes=p.boxes), indent=2), encoding='utf-8')
    print(args.output)
    print(f'{args.size} landscape; vector charts; {len(p.boxes)} checked text boxes.')


if __name__ == '__main__':
    main()
