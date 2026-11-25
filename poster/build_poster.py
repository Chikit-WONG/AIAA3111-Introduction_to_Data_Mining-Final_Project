"""Draw the 800 x 1000 mm Group 11 research poster."""
from pathlib import Path
import json
from scene_engine import Scene, measure, render_and_check, UNIT_PT

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
(BUILD / 'qa').mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / 'poster_data.json').read_text(encoding='utf-8'))
S = Scene()
BLUE, INK, GRAY, PALE, GRID = '#2463B5', '#202020', '#626B77', '#EEF4FD', '#D9DDE3'
CW = (3200 - 160 - 96) / 3
COL = [80 + i * (CW + 48) for i in range(3)]


def tag(name):
    S.tag = name


def txt(x, y, value, size=40, bold=False, color=INK, anchor='start', width=None, mono=False):
    S.text(x, y, value, size, 'mono' if mono else 'bold' if bold else 'regular', color, anchor, width)


def section(x, y, number, title):
    txt(x + 16, y, number, 36, True, BLUE)
    txt(x + 94, y, title, 46, True, width=CW - 110)


def phase(y, num, title, dates):
    x = COL[1] + 16
    S.rect(x, y - 44, 58, 58, BLUE, 'none', 0)
    txt(x + 29, y - 2, num, 40, True, '#FFFFFF', 'middle')
    txt(x + 86, y, title, 50, True)
    txt(x, y + 62, dates, 40, width=CW - 32)


def down(y1, y2):
    S.arrow(COL[1] + CW / 2, y1, COL[1] + CW / 2, y2, BLUE, 4, 12)


def node(y, h, title, sub=None, title_size=48):
    x = COL[1] + 16
    S.rect(x, y, CW - 32, h, PALE, BLUE, 3)
    txt(x + 26, y + 60, title, title_size, True, BLUE, width=CW - 84)
    if sub:
        txt(x + 26, y + h - 27, sub, 38, width=CW - 84)


def paper(x, y, w, h, future=False, month=None):
    # Receipt and calendar silhouettes share the same stroke and text scale.
    S.rect(x, y, w, h, '#FFFFFF', 'none', 0)
    if future:
        S.rect(x, y, w, 60, PALE, 'none', 0)
        S.line([(x, y + 60), (x + w, y + 60)], INK, 3)
        txt(x + w / 2, y + 45, month, 36, True, anchor='middle')
        for xx in [x + 34, x + w - 34]:
            S.line([(xx, y - 11), (xx, y + 7)], INK, 3)
    else:
        txt(x + w / 2, y + 36, 'ORDER', 34, True, anchor='middle')
        S.line([(x + 16, y + 48), (x + w - 16, y + 48)], GRID, 2)
    # Draw the complete outline after all fills so no edge is painted over.
    S.rect(x, y, w, h, 'none', INK, 3)
    product_y = y + (82 if future else 69)
    S.rect(x + 15, product_y, 57, 57, BLUE, 'none', 0)
    txt(x + 43.5, product_y + 43, 'A', 43, True, '#FFFFFF', 'middle')
    S.rect(x + 88, product_y, 57, 57, '#FFFFFF', INK, 2.5)
    txt(x + 116.5, product_y + 43, 'B', 43, True, anchor='middle')
    if future:
        txt(x + 169, product_y + 43, '?', 40, True, BLUE, 'middle')


def comparison_chart(y, title, metric, maximum, ticks, decimals):
    x = COL[2]
    txt(x + 16, y, title, 40, True, width=CW - 32)
    left, right, top, base = x + 101, x + CW - 16, y + 67, y + 266
    for tick in ticks:
        yy = base - tick / maximum * (base - top)
        S.line([(left, yy), (right, yy)], GRID, 1.7)
        txt(left - 20, yy + 12, str(tick), 34, color=GRAY, anchor='end')
    group_w = (right - left) / 3
    for i, row in enumerate(DATA['benchmark']):
        c = left + (i + .5) * group_w
        for j, (algo, color) in enumerate([('apriori', BLUE), ('fpgrowth', '#939BA5')]):
            value = row[algo][metric]
            xx = c - 93 + j * 101
            bh = value / maximum * (base - top)
            S.rect(xx, base - bh, 82, bh, color, 'none', 0)
            txt(xx + 41, base - bh - 16, f'{value:.{decimals}f}', 36, True,
                BLUE if j == 0 else INK, 'middle')
        txt(c, base + 55, f'{row["support"]*100:g}%', 38, True, anchor='middle')
    S.line([(left, base), (right, base)], INK, 2.5)
    txt((left + right) / 2, base + 109, 'Discovery support', 36, color=GRAY, anchor='middle')


# Header and headline results.
tag('header')
S.text(80, 86, 'AIAA 3111 课程项目海报', 40, 'cjkbold', BLUE)
txt(3120, 86, 'Group 11', 44, True, BLUE, 'end')
txt(80, 241, 'Beyond Frequent Co-Purchases', 132, True, width=3040)
txt(83, 326, 'A Study of Temporal Stability in Retail Association Rules', 62, width=3035)
txt(83, 390, 'Chi Kit WONG (50012338)  /  Yuxuan OUYANG (50013526)  /  Zhicheng SUN (50012546)', 38, width=3035)
S.line([(80, 430), (3120, 430)], INK, 3)
for x in COL:
    S.rect(x, 465, CW, 208, '#FFFFFF', INK, 2.5)
    S.rect(x, 465, 8, 208, BLUE, 'none', 0)
for x, label, value, sub, size in [
    (COL[0], 'MEAN MONTHLY RETENTION', '79.2%', '71 rules | Aug-Nov 2011', 100),
    (COL[1], 'PASSING EVERY TEST MONTH', '46 / 71', 'Rules passing all four months', 100),
    (COL[2], 'APRIORI / FP-GROWTH', 'Same itemsets', 'Different computational costs', 77),
]:
    txt(x + 29, 513, label, 34, True, width=CW - 55)
    txt(x + 27, 607, value, size, True, BLUE, width=CW - 55)
    txt(x + 29, 655, sub, 34, color=GRAY, width=CW - 55)

tag('column_headers')
for x, title in zip(COL, ['Task & Data', 'Experimental Design', 'Results & Discussion']):
    txt(x + 12, 759, title, 52, True, width=CW - 24)
    S.line([(x + 12, 789), (x + CW - 12, 789)], INK, 3)
for x in [COL[1] - 24, COL[2] - 24]:
    S.line([(x, 722), (x, 3760)], '#A7ADB5', 1.8)

# LEFT: all original image content rebuilt as native code/vector geometry.
x = COL[0]
tag('left_question')
section(x, 855, '01', 'Research question')
S.paragraph(x + 16, 931, 'Do past co-purchase patterns remain reliable in later months?', CW - 32, 44, 58, 'bold')
txt(x + 205, 1085, 'Past orders', 42, True, anchor='middle')
txt(x + 755, 1085, 'Later months', 42, True, anchor='middle')
for i in range(4):
    paper(x + 16 + (i % 2) * 193, 1125 + (i // 2) * 185, 177, 152)
    paper(x + 550 + (i % 2) * 203, 1125 + (i // 2) * 185, 191, 152, True, f'Month {i+1}')
S.arrow(x + 425, 1292, x + 517, 1292, BLUE, 5, 20)
txt(x + 471, 1250, 'Time', 36, True, BLUE, 'middle')
txt(x + 205, 1522, 'Co-purchase examples', 35, True, anchor='middle')
txt(x + 755, 1522, 'Still together?', 40, True, BLUE, 'middle')
S.paragraph(x + 16, 1580, 'For A → B, confidence is the share of orders with A that also contain B.',
            CW - 32, 38, 48, fill=GRAY)

tag('left_dataset')
section(x, 1700, '02', 'Dataset & preprocessing')
txt(x + 16, 1773, 'UCI Online Retail', 48, True)
tx, ty, widths, rh = x + 16, 1810, [280, 276, 265, CW - 853], 76
heads = ['InvoiceNo', 'CustomerID', 'UnitPrice', '...']
rows = [['536365', '17850', '2.55', '...'], ['536365', '17850', '3.39', '...'],
        ['536365', '17850', '2.75', '...'], ['536366', '17850', '1.85', '...'], ['...', '...', '...', '...']]
S.rect(tx, ty, CW - 32, rh * 6, '#FFFFFF', 'none', 0)
S.rect(tx, ty, widths[0], rh * 6, PALE, 'none', 0)
# Each black grid line is drawn once. Invoice grouping is a separate blue frame.
S.rect(tx, ty, CW - 32, rh * 6, 'none', INK, 2.5)
column_x = tx
for w in widths[:-1]:
    column_x += w
    S.line([(column_x, ty), (column_x, ty + rh * 6)], INK, 2.5)
for i in range(1, 6):
    S.line([(tx, ty + i * rh), (tx + CW - 32, ty + i * rh)], INK, 2.5)
S.rect(tx, ty + rh, widths[0], 3 * rh, 'none', BLUE, 3.5)
for i, row in enumerate([heads] + rows):
    xx = tx
    for j, (value, w) in enumerate(zip(row, widths)):
        txt(xx + w / 2, ty + i * rh + 51, value, 38 if i else 36, i == 0 or j == 0,
            BLUE if i == 0 and j == 0 else INK, 'middle', width=w - 12)
        xx += w
txt(tx, 2328, '* Same InvoiceNo = same order.', 38, True, width=CW - 32)
txt(tx, 2382, '* 8 fields per record; selected fields shown.', 36, color=GRAY, width=CW - 32)

txt(tx, 2482, 'DATASET INFO', 40, True)
for yy, label, value in [(2553, 'Source', 'UK retailer transaction line items'),
                          (2617, 'Period', '2010-12-01 to 2011-12-09'),
                          (2681, 'Size', '541,909 line items')]:
    txt(tx, yy, label, 40, True)
    txt(tx + 177, yy, value, 40, width=CW - 209)
S.line([(tx, 2722), (x + CW - 16, 2722)], GRID, 2)
txt(tx, 2790, 'PREPROCESS', 40, True)
for yy, label, value in [(2862, 'Format', 'IDs; date and numeric types.'),
                          (2932, 'Remove', 'Duplicates, missing keys, fees, ...'),
                          (3002, 'Aggregate', 'Group items by InvoiceNo.')]:
    txt(tx, yy, label, 40, True, BLUE)
    txt(tx + 240, yy, value, 38, width=CW - 272)

tag('left_aggregation')
txt(tx, 3110, 'One invoice → one transaction', 44, True, width=CW - 32)
txt(tx + 171, 3180, 'InvoiceNo | StockCode', 34, True, anchor='middle')
for i, code in enumerate(['85123A', '71053', '84406B']):
    yy = 3210 + i * 105
    S.rect(tx, yy, 356, 76, '#FFFFFF', INK, 2.5)
    txt(tx + 178, yy + 50, f'536365 | {code}', 34, anchor='middle', mono=True)
    S.line([(tx + 356, yy + 38), (tx + 403, yy + 38)], BLUE, 3)
S.line([(tx + 403, 3248), (tx + 403, 3458)], BLUE, 3)
S.arrow(tx + 403, 3353, tx + 482, 3353, BLUE, 4, 17)
S.rect(tx + 498, 3210, CW - 530, 290, '#FFFFFF', INK, 2.5)
S.rect(tx + 498, 3210, CW - 530, 69, PALE, INK, 2.5)
txt(tx + 523, 3257, 'Transaction 536365', 38, True, width=CW - 580)
for yy, line in [(3345, '{85123A,'), (3403, ' 71053, 84406B,'), (3461, ' ...}')]:
    txt(tx + 526, yy, line, 38, mono=True, width=CW - 583)
txt(tx + 178, 3538, '...', 44, True, anchor='middle')
txt(x + CW / 2, 3624, '17,901 transactions used', 48, True, BLUE, 'middle')
S.paragraph(tx, 3700, 'Each product appears once per transaction, even if several units were bought.', CW - 32, 38, 49, fill=GRAY)

# MIDDLE: connected workflow with larger, shorter labels.
x, c = COL[1], COL[1] + CW / 2
tag('discovery')
phase(855, '1', 'Discover', 'Dec 2010-May 2011 | 7,365 orders')
for xx, name in [(x + 16, 'Apriori'), (x + CW / 2 + 15, 'FP-Growth')]:
    S.rect(xx, 1002, (CW - 62) / 2, 100, '#FFFFFF', INK, 2.5)
    txt(xx + (CW - 62) / 4, 1070, name, 46, True, anchor='middle')
txt(c, 1168, 'Support: 0.5% / 1% / 2%', 42, True, anchor='middle')
down(1190, 1224)
S.rect(x + 16, 1240, CW - 32, 175, '#FFFFFF', INK, 2.5)
txt(x + 42, 1298, 'Frequent itemsets', 44, True)
txt(x + 42, 1361, '{A, B}    {A, B, C}    ...', 42, mono=True, width=CW - 84)
txt(x + CW - 42, 1397, 'Up to 3 items', 34, color=GRAY, anchor='end')
down(1433, 1471)
S.rect(x + 16, 1490, CW - 32, 182, '#FFFFFF', INK, 2.5)
txt(x + 42, 1548, 'Generate rules', 44, True)
txt(x + 42, 1614, 'A -> B   AB -> C   ...', 42, mono=True)
txt(x + CW - 42, 1654, 'One item on the right', 34, color=GRAY, anchor='end')
txt(c, 1742, 'Confidence: 30% / 50% / 70%', 40, True, anchor='middle')
txt(c, 1796, 'Lift >=1.2', 40, anchor='middle')
down(1815, 1843)
node(1860, 145, '9 candidate groups', '3 support x 3 confidence', 54)

tag('validation')
phase(2100, '2', 'Validate', 'Jun-Jul 2011 | 2,696 orders')
node(2200, 103, 'The same 9 groups', title_size=46)
down(2313, 2355)
S.rect(x + 16, 2365, CW - 32, 145, '#FFFFFF', INK, 2.5)
txt(c, 2421, 'Evaluate June and July separately', 40, True, anchor='middle', width=CW - 64)
txt(c, 2476, 'Average their monthly retention', 40, anchor='middle', width=CW - 64)
txt(x + 16, 2571, 'Best mean; group size >=20 rules', 40, width=CW - 32)
node(2610, 160, 'Selected: 71 rules', 'Support 2% | Confidence 50%', 54)

tag('shared_criteria')
S.rect(x + 16, 2810, CW - 32, 240, PALE, INK, 2.5)
txt(x + 42, 2865, 'Shared monthly criteria', 42, True)
txt(x + 42, 2920, 'Support >=0.5% | Confidence >=50%', 38, True, BLUE, width=CW - 84)
txt(x + 42, 2970, 'Lift >=1.2 | Antecedent orders >=20', 38, width=CW - 84)
txt(x + 42, 3020, 'Consequent must be observed.', 36, color=GRAY)

tag('test')
phase(3130, '3', 'Test', 'Aug-Nov 2011 | 7,096 orders')
node(3215, 143, 'Frozen: the same 71 rules', 'Evaluate only - no re-mining', 44)
bw = (CW - 74) / 4
month_centers = [x + 16 + i * (bw + 14) + bw / 2 for i in range(4)]
S.line([(c, 3366), (c, 3384)], BLUE, 4)
S.line([(month_centers[0], 3384), (month_centers[-1], 3384)], BLUE, 4)
for month_center in month_centers:
    S.arrow(month_center, 3384, month_center, 3407, BLUE, 4, 12)
for i, month in enumerate(['Aug', 'Sep', 'Oct', 'Nov']):
    xx = x + 16 + i * (bw + 14)
    S.rect(xx, 3417, bw, 91, '#FFFFFF', 'none', 0)
    S.rect(xx, 3417, bw, 12, PALE, 'none', 0)
    S.rect(xx, 3417, bw, 91, 'none', INK, 2.5)
    txt(xx + bw / 2, 3481, month, 42, True, anchor='middle')
txt(c, 3571, 'Monthly retention = passed / 71', 42, True, anchor='middle', width=CW - 32)
txt(c, 3628, 'Recheck every rule in every month.', 38, anchor='middle')
for xx, label, color in [(x + 16, 'Pass', BLUE), (x + 246, 'Metric fail', '#939BA5'), (x + 555, 'Insufficient evidence', '#FFFFFF')]:
    S.rect(xx, 3660, 22, 22, color, INK, 1.5)
    txt(xx + 32, 3685, label, 34)
txt(x + 16, 3740, 'All 71 stay in each month\'s denominator.', 36, color=GRAY, width=CW - 32)

# RIGHT: native benchmark charts, retention grid and monthly results.
x = COL[2]
tag('algorithm_comparison')
section(x, 855, '03', 'Algorithm comparison')
for xx, label, color in [(x + 16, 'Apriori', BLUE), (x + 350, 'FP-Growth', '#939BA5')]:
    S.rect(xx, 917, 28, 28, color, 'none', 0)
    txt(xx + 44, 945, label, 40, True)
comparison_chart(1021, 'Mining time (seconds)', 'seconds', 6, [0, 3, 6], 2)
comparison_chart(1465, 'Peak process memory (MiB)', 'peak_mib', 180, [0, 90, 180], 1)
txt(x + 16, 1907, 'Same itemsets: 20,906 / 2,218 / 413.', 40, True, width=CW - 32)
txt(x + 16, 1963, 'Apriori: faster at 1% / 2% support;', 40, width=CW - 32)
txt(x + 16, 2018, 'lower peak memory at all settings.', 40, width=CW - 32)
txt(x + 16, 2071, '3-run medians; mining only; low-memory Apriori.', 34, color=GRAY, width=CW - 32)

tag('test_grid')
section(x, 2182, '04', 'Rule retention')
gx, gy = x + 180, 2380
gw, gh = (x + CW - 16 - gx) / 3, 235
txt(gx + 1.5 * gw, 2258, 'Discovery support', 40, True, anchor='middle')
S.text(x + 47, gy + 1.5 * gh, 'Discovery confidence', 40, 'bold', INK, 'middle',
       max_width=3 * gh, vertical=True)
for j, value in enumerate(['0.5%', '1%', '2%']):
    txt(gx + (j + .5) * gw, 2325, value, 42, True, anchor='middle')
for i, confidence in enumerate([.3, .5, .7]):
    txt(gx - 20, gy + (i + .5) * gh + 13, f'{confidence*100:g}%', 40, True, anchor='end')
    for j, support in enumerate([.005, .01, .02]):
        row = next(v for v in DATA['grid'] if v['support'] == support and v['confidence'] == confidence)
        xx, yy = gx + j * gw, gy + i * gh
        selected, excluded = row['selected'], row['rules'] < 20
        S.rect(xx, yy, gw, gh, BLUE if selected else '#F3F5F7' if excluded else '#FFFFFF', INK, 2.5)
        color = '#FFFFFF' if selected else INK
        txt(xx + gw / 2, yy + 86, f'{row["test"]*100:.1f}%', 60, True, color, 'middle')
        txt(xx + gw / 2, yy + 148, f'{row["rules"]:,} rules', 36, color=color, anchor='middle', width=gw - 16)
        if selected:
            txt(xx + gw / 2, yy + 205, 'Selected', 36, True, '#FFFFFF', 'middle')
        if excluded:
            txt(xx + gw / 2, yy + 205, '<20-rule min.', 34, color=GRAY, anchor='middle', width=gw - 12)
txt(x + 16, 3149, 'Cells: mean test retention, Aug-Nov 2011.', 36, width=CW - 32)
txt(x + 16, 3201, 'Counts: original groups; blue: selected.', 36, width=CW - 32)
txt(x + 16, 3265, 'Selected rules show short-term persistence.', 40, True, width=CW - 32)
txt(x + 16, 3319, 'Keep monitoring: not every rule lasts.', 40, True, BLUE, width=CW - 32)

tag('monthly_results')
txt(x + 16, 3407, 'Frozen cohort: monthly retention', 42, True, width=CW - 32)
pl, pr, pt, pb = x + 89, x + CW - 16, 3465, 3640
for value in [0, .5, 1]:
    yy = pb - value * (pb - pt)
    S.line([(pl, yy), (pr, yy)], GRID, 1.7)
    txt(pl - 16, yy + 11, f'{value*100:g}', 34, color=GRAY, anchor='end')
for i, row in enumerate(DATA['test_months']):
    cc = pl + (i + .5) * (pr - pl) / 4
    bh = row['retention'] * (pb - pt)
    S.rect(cc - 56, pb - bh, 112, bh, BLUE, 'none', 0)
    txt(cc, pb - bh - 14, f'{row["retention"]*100:.1f}%', 38, True, BLUE, 'middle')
    txt(cc, 3690, ['Aug', 'Sep', 'Oct', 'Nov'][i], 40, True, anchor='middle')
    txt(cc, 3740, f'{row["passed"]}/71', 36, color=GRAY, anchor='middle')
S.line([(pl, pb), (pr, pb)], INK, 2.5)

tag('footer')
S.line([(80, 3805), (3120, 3805)], INK, 2.5)
txt(84, 3855, 'Data: UCI Online Retail (Chen, 2015). Methods: Agrawal & Srikant (1994); Han et al. (2000).', 28)
txt(84, 3902, 'AI assistance: Codex supported implementation, analysis, writing and visuals. Methods via MLxtend; see report disclosure.', 28, color=GRAY)
txt(84, 3947, 'Code: github.com/Chikit-WONG/AIAA3111-Introduction_to_Data_Mining-Final_Project', 28, color=BLUE)

if __name__ == '__main__':
    S.export_svg(BUILD / 'poster_editable.svg')
    S.export_pdf(BUILD / 'poster_800x1000mm.pdf')
    validation = S.validate()
    validation['pdf'] = render_and_check(BUILD / 'poster_800x1000mm.pdf', BUILD)
    body = [e['size'] * UNIT_PT for e in S.elements if e['kind'] == 'text' and e['tag'] not in {'header', 'column_headers', 'footer'}]
    validation['body_font_points'] = {'min': round(min(body), 1), 'max': round(max(body), 1)}
    (BUILD / 'qa/validation.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')
    (BUILD / 'poster_scene.json').write_text(json.dumps(S.elements, indent=2), encoding='utf-8')
    print(json.dumps(validation, indent=2))
