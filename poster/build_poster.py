"""Draw the 800 x 1000 mm Group 11 research poster (V04 visual design)."""
from pathlib import Path
import json
import math
from scene_engine import Scene, render_and_check, measure, UNIT_PT

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
(BUILD / 'qa').mkdir(parents=True, exist_ok=True)
LOGO = ROOT / 'assets' / 'hkustgz_logo.png'
DATA = json.loads((ROOT / 'poster_data.json').read_text(encoding='utf-8'))
selection = DATA['selection']
summary = DATA['summary']
rule_count = selection['rules']
validation_months = DATA['validation_months']
validation_passes = sum(month['passed'] for month in validation_months)
validation_checks = rule_count * len(validation_months)
test_passes = summary['test_retained_rule_months']
test_checks = summary['test_rule_months']
discovery_orders = DATA['discovery_orders']
validation_orders = sum(month['orders'] for month in validation_months)
test_orders = sum(month['orders'] for month in DATA['test_months'])
main_orders = discovery_orders + validation_orders + test_orders
partial_orders = DATA['partial_december_orders']
all_passed = summary['rules_retained_all_test_months']
S = Scene()

# Visual system. Navy and gold follow the HKUST(GZ) mark; blue carries the data.
# Apriori blue / FP-Growth teal pass the colour-vision and contrast checks as a pair.
# Gold is reserved for the selected rule group.
NAVY, BLUE, TEAL, GOLD = '#0B2C52', '#2463B5', '#00A88A', '#E8A33D'
INK, GRAY, WHITE = '#1B2430', '#5B6675', '#FFFFFF'
PALE, MIST, LINE, EDGE, GRID, AXIS = '#EAF2FC', '#F4F7FB', '#CBD5E3', '#8FA1BA', '#E1E7EF', '#AEB8C6'
PHASES = ['#17509E', '#3F86DA', '#8DBDF0']  # discover, validate, test (ordered, dark to light)

# Page geometry: three cards share the width; text sits 28 units inside each card.
HEAD_H, KPI_Y, KPI_H = 422, 472, 208
CARD_X, CARD_W, CARD_TOP, BAR_H, CARD_BOT, FOOT_Y = [60, 1100, 2140], 1000, 714, 84, 3790, 3826
LEFT = [x + 28 for x in CARD_X]
CWD = CARD_W - 56


def tag(name):
    S.tag = name


def txt(x, y, value, size=40, bold=False, color=INK, anchor='start', width=None, mono=False):
    S.text(x, y, value, size, 'mono' if mono else 'bold' if bold else 'regular', color, anchor, width)


def rich(x, y, parts, size):
    """One line that mixes weights and colours. Each part is (text, bold, colour)."""
    for value, bold, color in parts:
        style = 'bold' if bold else 'regular'
        S.text(x, y, value, size, style, color)
        x += measure(value, size, style)
    return x


def panel(x, y, w, h, fill=PALE, accent=BLUE):
    """Tinted callout with a short accent bar on the left."""
    S.rect(x, y, w, h, fill, 'none', 0, r=18)
    S.rect(x + 18, y + 20, 9, h - 40, accent, 'none', 0, r=4.5)


def heading(x, y, label):
    """Small label followed by a hairline that runs to the edge of the column."""
    txt(x, y, label, 38, True, NAVY)
    S.line([(x + measure(label, 38, 'bold') + 22, y - 13), (x + CWD, y - 13)], LINE, 2.5)


def section(x, y, number, title):
    S.rect(x, y - 44, 66, 58, BLUE, 'none', 0, r=12)
    txt(x + 33, y - 2, number, 36, True, WHITE, 'middle')
    txt(x + 88, y, title, 46, True, NAVY, width=CWD - 88)


def ring(cx, cy, radius, share, check=False):
    """Gauge: a share of a full turn, clockwise from twelve o'clock."""
    S.circle(cx, cy, radius, 'none', '#D3E2F6', 22)
    if share >= .999:
        S.circle(cx, cy, radius, 'none', BLUE, 22)
    else:
        steps = max(8, int(share * 120))
        S.line([(cx + radius * math.sin(2 * math.pi * share * i / steps),
                 cy - radius * math.cos(2 * math.pi * share * i / steps)) for i in range(steps + 1)],
               BLUE, 22, cap='round')
    if check:
        S.line([(cx - 27, cy + 2), (cx - 8, cy + 22), (cx + 28, cy - 20)], BLUE, 13, cap='round')


def column(i, title):
    x = CARD_X[i]
    S.rect(x, CARD_TOP, CARD_W, CARD_BOT - CARD_TOP, WHITE, LINE, 3, r=26)
    S.rect(x, CARD_TOP, CARD_W, BAR_H, NAVY, NAVY, 3, r=26)
    S.rect(x, CARD_TOP + BAR_H - 32, CARD_W, 32, NAVY, NAVY, 3)  # square the bar's lower corners
    S.rect(x + 30, CARD_TOP + 21, 10, 42, GOLD, 'none', 0, r=5)
    txt(x + 60, CARD_TOP + 60, title, 52, True, WHITE, width=CARD_W - 90)


def value_label(cx, y, value, size):
    """Bar value on a patch of surface colour, so no gridline runs through the digits."""
    w = measure(value, size, 'bold') + 6
    S.rect(cx - w / 2, y - size * .8, w, size * .95, WHITE, 'none', 0)
    txt(cx, y, value, size, True, INK, 'middle')


def bar(x, base, w, h, color):
    """Column with a rounded data end and a square foot on the baseline."""
    r = min(12, h / 2)
    S.rect(x, base - h, w, h, color, 'none', 0, r=r)
    S.rect(x, base - h + r, w, h - r, color, 'none', 0)


def phase(y, num, title, dates):
    x = LEFT[1]
    S.rect(x, y, CWD, 84, PALE, 'none', 0, r=18)
    S.circle(x + 46, y + 42, 30, BLUE)
    txt(x + 46, y + 56, num, 40, True, WHITE, 'middle')
    txt(x + 92, y + 59, title, 48, True, NAVY)
    txt(x + CWD - 26, y + 55, dates, 36, color=INK, anchor='end',
        width=CWD - 150 - measure(title, 48, 'bold'))


def down(y1, y2):
    S.arrow(LEFT[1] + CWD / 2, y1, LEFT[1] + CWD / 2, y2, BLUE, 5, 16)


def step(y, h):
    S.rect(LEFT[1], y, CWD, h, WHITE, EDGE, 3, r=18)


def node(y, h, title, sub=None, title_size=48):
    x = LEFT[1]
    S.rect(x, y, CWD, h, PALE, BLUE, 3.5, r=18)
    txt(x + 30, y + 60, title, title_size, True, BLUE, width=CWD - 60)
    if sub:
        txt(x + 30, y + h - 27, sub, 38, width=CWD - 60)


def paper(x, y, w, h, future=False, month=None):
    """Receipt (past order) or calendar page (later month) holding products A and B."""
    S.rect(x, y, w, h, WHITE, 'none', 0, r=14)
    if future:
        S.rect(x, y, w, 60, PALE, 'none', 0, r=14)
        S.rect(x, y + 30, w, 30, PALE, 'none', 0)
        txt(x + w / 2, y + 44, month, 36, True, NAVY, 'middle')
        S.rect(x, y, w, h, 'none', BLUE, 3, r=14, dash=(15, 9))
        for xx in [x + 34, x + w - 34]:
            S.line([(xx, y - 11), (xx, y + 8)], NAVY, 6, cap='round')
    else:
        txt(x + w / 2, y + 37, 'ORDER', 34, True, GRAY, 'middle')
        S.line([(x + 16, y + 49), (x + w - 16, y + 49)], GRID, 2.5)
        S.rect(x, y, w, h, 'none', EDGE, 3, r=14)
    product_y = y + (80 if future else 70)
    S.rect(x + 15, product_y, 57, 57, BLUE, 'none', 0, r=10)
    txt(x + 43.5, product_y + 43, 'A', 43, True, WHITE, 'middle')
    S.rect(x + 88, product_y, 57, 57, WHITE, NAVY, 3, r=10)
    txt(x + 116.5, product_y + 43, 'B', 43, True, NAVY, 'middle')
    if future:
        txt(x + 169, product_y + 43, '?', 40, True, BLUE, 'middle')


def comparison_chart(y, title, metric, maximum, ticks, decimals, axis_title=None):
    x = LEFT[2]
    txt(x, y, title, 40, True, NAVY, width=CWD)
    left, right, top, base = x + 85, x + CWD, y + 60, y + 250
    for tick in ticks:
        yy = base - tick / maximum * (base - top)
        S.line([(left, yy), (right, yy)], GRID, 2)
        txt(left - 18, yy + 12, str(tick), 34, color=GRAY, anchor='end')
    group_w = (right - left) / 3
    for i, row in enumerate(DATA['benchmark']):
        c = left + (i + .5) * group_w
        for j, (algo, color) in enumerate([('apriori', BLUE), ('fpgrowth', TEAL)]):
            value = row[algo][metric]
            xx = c - 92 + j * 96
            bh = value / maximum * (base - top)
            bar(xx, base, 88, bh, color)
            value_label(xx + 44, base - bh - 14, f'{value:.{decimals}f}', 36)
        txt(c, base + 52, f'{row["support"]*100:g}%', 38, True, anchor='middle')
    S.line([(left, base), (right, base)], AXIS, 3)
    if axis_title:
        txt((left + right) / 2, base + 104, axis_title, 36, color=GRAY, anchor='middle')


RAMP = [(0, '#E3EEFB'), (.1, '#CFE2FA'), (.4, '#A3CAF5'), (.6, '#6FAAEC'), (.8, BLUE)]


def retention_color(value):
    """One-hue ramp: the more rules a group retains, the darker its cell."""
    value = min(max(value, 0), RAMP[-1][0])
    for (v0, c0), (v1, c1) in zip(RAMP, RAMP[1:]):
        if value <= v1:
            t = (value - v0) / (v1 - v0)
            return '#' + ''.join(f'{round(int(c0[k:k+2], 16) * (1 - t) + int(c1[k:k+2], 16) * t):02X}'
                                 for k in (1, 3, 5))


# Header band with the university mark, then the three headline results.
tag('header')
S.rect(0, 0, 3200, HEAD_H, NAVY, 'none', 0)
for radius in (208, 292, 376):  # quiet ripples around the university mark, kept inside the band
    run = []
    for step_no in range(361):
        px = 2586 + radius * math.cos(math.radians(step_no))
        py = 214 + radius * math.sin(math.radians(step_no))
        if 0 <= py <= HEAD_H and px <= 3200:
            run.append((px, py))
        elif run:
            S.line(run, '#163F72', 4)
            run = []
    if run:
        S.line(run, '#163F72', 4)
S.rect(0, HEAD_H, 3200, 14, GOLD, 'none', 0)
txt(80, 82, 'AIAA 3111 | Introduction to Data Mining | Course Project Poster', 38, True, '#9FC4F2')
txt(80, 228, 'Beyond Frequent Co-Purchases', 132, True, WHITE, width=2330)
txt(83, 308, 'A Study of Temporal Stability in Retail Association Rules', 60, color='#DCE8F7', width=2330)
members = [('Chi Kit WONG', '50012338'), ('Yuxuan OUYANG', '50013526'), ('Zhicheng SUN', '50012546')]
cursor = 83
for n, (member, student_id) in enumerate(members):
    cursor = rich(cursor, 376, [(member + ' ', True, WHITE), (f'({student_id})', False, '#B9CEE9')], 38)
    if n < len(members) - 1:
        S.circle(cursor + 38, 363, 6, GOLD)
        cursor += 76
S.circle(2586, 214, 124, WHITE, GOLD, 8)
S.image(2528, 120, 116, 188, LOGO)
txt(2746, 196, 'HKUST(GZ)', 66, True, WHITE)
txt(2746, 294, 'Group 11', 84, True, GOLD)

for x, label, value, sub, size, share, check in [
    (CARD_X[0], 'MEAN MONTHLY TEST RETENTION', f'{test_passes / test_checks:.1%}',
     f'{test_passes}/{test_checks} rule-months passed | Aug–Nov 2011', 100, test_passes / test_checks, False),
    (CARD_X[1], 'PASSING EVERY TEST MONTH', f'{all_passed} / {rule_count}',
     'Rules passing all four months', 100, all_passed / rule_count, False),
    (CARD_X[2], 'APRIORI / FP-GROWTH', 'Same itemsets', 'Different computational costs', 77, 1, True),
]:
    S.rect(x, KPI_Y, CARD_W, KPI_H, WHITE, LINE, 3, r=26)
    S.rect(x + 26, KPI_Y + 28, 11, KPI_H - 56, GOLD, 'none', 0, r=5.5)
    txt(x + 62, KPI_Y + 52, label, 34, True, NAVY, width=CARD_W - 280)
    txt(x + 60, KPI_Y + 145, value, size, True, BLUE, width=CARD_W - 280)
    txt(x + 62, KPI_Y + 190, sub, 34, color=GRAY, width=CARD_W - 280)
    ring(x + CARD_W - 116, KPI_Y + KPI_H / 2, 62, share, check)

tag('column_headers')
for i, title in enumerate(['Task & Data', 'Experimental Design', 'Results & Discussion']):
    column(i, title)

# LEFT: from the research question to the baskets that enter the study.
x = LEFT[0]
tag('left_question')
section(x, 868, '01', 'Research question')
panel(x, 904, CWD, 142)
question_end = S.paragraph(x + 50, 966, 'Do past co-purchase patterns remain reliable in later months?',
                           CWD - 76, 44, 58, 'bold', NAVY)
assert question_end == 966 + 2 * 58, 'The research question must stay on two lines'
txt(x + 185, 1104, 'Past orders', 42, True, NAVY, 'middle')
txt(x + 731, 1104, 'Later months', 42, True, NAVY, 'middle')
for i in range(4):
    paper(x + (i % 2) * 193, 1140 + (i // 2) * 185, 177, 152)
    paper(x + 534 + (i % 2) * 203, 1140 + (i // 2) * 185, 191, 152, True, f'Month {i+1}')
S.arrow(x + 396, 1308, x + 510, 1308, BLUE, 7, 26)
txt(x + 450, 1278, 'Time', 36, True, BLUE, 'middle')
txt(x + 185, 1537, 'Co-purchase examples', 34, True, anchor='middle')
txt(x + 731, 1537, 'Still together?', 40, True, BLUE, 'middle')
S.paragraph(x, 1596, 'For A → B, confidence is the share of orders with A that also contain B.',
            CWD, 38, 48, fill=GRAY)

tag('left_dataset')
section(x, 1720, '02', 'Dataset & preprocessing')
txt(x, 1794, 'UCI Online Retail', 48, True, NAVY)
ty, widths, rh = 1826, [280, 276, 265, CWD - 821], 70
heads = ['InvoiceNo', 'CustomerID', 'UnitPrice', '...']
rows = [['536365', '17850', '2.55', '...'], ['536365', '17850', '3.39', '...'],
        ['536365', '17850', '2.75', '...'], ['536366', '17850', '1.85', '...'], ['...', '...', '...', '...']]
S.rect(x, ty, CWD, rh * 6, WHITE, 'none', 0)
S.rect(x, ty + rh, widths[0], rh * 5, PALE, 'none', 0)
S.rect(x, ty, CWD, rh, NAVY, 'none', 0)
for i in range(2, 6):
    S.line([(x, ty + i * rh), (x + CWD, ty + i * rh)], LINE, 2)
S.rect(x, ty, CWD, rh * 6, 'none', EDGE, 3)
# Invoice grouping is a separate blue frame around the three rows of one order.
S.rect(x + 8, ty + rh + 7, widths[0] - 16, 3 * rh - 14, 'none', BLUE, 4.5, r=12)
for i, row in enumerate([heads] + rows):
    xx = x
    for j, (value, w) in enumerate(zip(row, widths)):
        txt(xx + w / 2, ty + i * rh + 48, value, 38 if i else 36, i == 0 or j == 0,
            WHITE if i == 0 else NAVY if j == 0 else INK, 'middle', width=w - 12)
        xx += w
txt(x, 2304, '* Same InvoiceNo = same order.', 38, True, width=CWD)
txt(x, 2356, '* 8 fields per record; selected fields shown.', 36, color=GRAY, width=CWD)

heading(x, 2442, 'DATASET INFO')
for yy, label, value in [(2510, 'Source', 'UK retailer transaction line items'),
                          (2572, 'Period', '2010-12-01 to 2011-12-09'),
                          (2634, 'Size', '541,909 line items')]:
    txt(x, yy, label, 40, True, NAVY)
    txt(x + 177, yy, value, 40, width=CWD - 177)
heading(x, 2722, 'PREPROCESS')
for yy, label, value in [(2796, 'Format', 'IDs; date and numeric types.'),
                          (2864, 'Remove', 'Duplicates, missing keys, fees, ...'),
                          (2932, 'Aggregate', 'Group items by InvoiceNo.')]:
    S.rect(x, yy - 43, 218, 58, PALE, 'none', 0, r=29)
    txt(x + 109, yy, label, 38, True, BLUE, 'middle')
    txt(x + 244, yy, value, 38, width=CWD - 244)

tag('left_aggregation')
txt(x, 3024, 'One invoice → one transaction', 44, True, NAVY, width=CWD)
txt(x + 178, 3080, 'InvoiceNo | StockCode', 34, True, GRAY, 'middle')
for i, code in enumerate(['85123A', '71053', '84406B']):
    yy = 3100 + i * 94
    S.rect(x, yy, 356, 72, MIST, EDGE, 3, r=12)
    txt(x + 178, yy + 48, f'536365 | {code}', 34, anchor='middle', mono=True)
    S.line([(x + 356, yy + 36), (x + 406, yy + 36)], BLUE, 4)
S.line([(x + 406, 3136), (x + 406, 3324)], BLUE, 4, cap='square')
S.arrow(x + 406, 3230, x + 486, 3230, BLUE, 5, 20)
bx, bw = x + 498, CWD - 498
S.rect(bx, 3100, bw, 260, WHITE, 'none', 0, r=16)
S.rect(bx, 3100, bw, 68, PALE, 'none', 0, r=16)
S.rect(bx, 3134, bw, 34, PALE, 'none', 0)
S.rect(bx, 3100, bw, 260, 'none', BLUE, 3.5, r=16)
txt(bx + 26, 3147, 'Transaction 536365', 38, True, NAVY, width=bw - 52)
for yy, line in [(3226, '{85123A,'), (3282, ' 71053, 84406B,'), (3338, ' ...}')]:
    txt(bx + 28, yy, line, 38, mono=True, width=bw - 56)
txt(x + 178, 3398, '...', 44, True, GRAY, 'middle')
txt(bx, 3404, 'Each product appears once.', 34, color=GRAY, width=bw)

tag('left_orders')
total_orders = main_orders + partial_orders
txt(x, 3492, f'{total_orders:,} study orders', 49, True, BLUE, width=CWD)
parts = [(discovery_orders, PHASES[0], WHITE, 'Discover'), (validation_orders, PHASES[1], WHITE, 'Validate'),
         (test_orders, PHASES[2], NAVY, 'Test'), (partial_orders, '#C3CAD5', None, None)]
gap = 5
unit = (CWD - gap * (len(parts) - 1)) / total_orders
xx = x
for orders, color, label_color, name in parts:
    w = orders * unit
    S.rect(xx, 3516, w, 60, color, 'none', 0, r=10)
    if name:
        txt(xx + w / 2, 3559, f'{orders:,}', 36, True, label_color, 'middle', width=w - 16)
        txt(xx + w / 2, 3618, name, 34, color=GRAY, anchor='middle')
    xx += w + gap
txt(x + CWD, 3618, 'Dec 1–9', 34, color=GRAY, anchor='end')
for yy, orders, label in [(3676, main_orders, 'Main study (discovery, validation, test)'),
                          (3730, partial_orders, 'Supplementary analysis (Dec 1–9, 2011)')]:
    txt(x + 141, yy, f'{orders:,}', 41, True, NAVY, 'end')
    txt(x + 170, yy, label, 38, width=CWD - 170)

# MIDDLE: one connected workflow, from discovery to the frozen test.
x, c = LEFT[1], LEFT[1] + CWD / 2
tag('discovery')
phase(828, '1', 'Discover', f'Dec 2010–May 2011 · {discovery_orders:,} orders')
half = (CWD - 30) / 2
for xx, name, color in [(x, 'Apriori', BLUE), (x + half + 30, 'FP-Growth', TEAL)]:
    S.rect(xx, 946, half, 96, WHITE, EDGE, 3, r=18)
    name_w = measure(name, 46, 'bold')
    S.circle(xx + half / 2 - name_w / 2 - 14, 994, 15, color)
    txt(xx + half / 2 + 20, 1010, name, 46, True, NAVY, 'middle')
txt(c, 1106, 'Support: 0.5% / 1% / 2%', 42, True, anchor='middle')
down(1124, 1160)
step(1174, 170)
txt(x + 30, 1232, 'Frequent itemsets', 44, True, NAVY)
txt(x + 30, 1294, '{A, B}    {A, B, C}    ...', 42, mono=True, width=CWD - 60)
txt(x + CWD - 30, 1326, 'Up to 3 items', 34, color=GRAY, anchor='end')
down(1358, 1394)
step(1408, 174)
txt(x + 30, 1466, 'Generate rules', 44, True, NAVY)
txt(x + 30, 1530, 'A → B   AB → C   ...', 42, mono=True)
txt(x + CWD - 30, 1564, 'One item on the right', 34, color=GRAY, anchor='end')
txt(c, 1648, 'Confidence: 30% / 50% / 70%', 40, True, anchor='middle')
txt(c, 1700, 'Lift ≥ 1.2', 40, anchor='middle')
down(1720, 1756)
node(1770, 144, '9 candidate groups', '3 support × 3 confidence', 54)

tag('validation')
phase(1966, '2', 'Validate', f'Jun–Jul 2011 · {validation_orders:,} orders')
node(2082, 100, 'Compare the 9 candidate groups', title_size=46)
down(2196, 2232)
step(2246, 144)
txt(c, 2302, 'Choose the highest mean monthly retention', 40, True, NAVY, 'middle', CWD - 40)
txt(c, 2356, 'Only groups with at least 20 rules qualify.', 38, anchor='middle', width=CWD - 40)
down(2404, 2440)
S.rect(x, 2454, CWD, 238, PALE, GOLD, 6, r=18)
S.rect(x + 20, 2478, 10, 190, GOLD, 'none', 0, r=5)
txt(x + 52, 2512, f'Selected group of {rule_count} rules', 46, True, NAVY, width=CWD - 80)
txt(x + 52, 2561, f'Discovery support {selection["min_support"]:.0%} | confidence {selection["min_confidence"]:.0%}',
    37, width=CWD - 80)
txt(x + 52, 2625, f'{validation_passes / validation_checks:.1%} validation retention', 48, True, BLUE, width=CWD - 80)
txt(x + 52, 2671, f'{validation_passes}/{validation_checks} rule-months passed in June and July', 36, width=CWD - 80)

tag('shared_criteria')
S.rect(x, 2734, CWD, 240, MIST, LINE, 3, r=18)
txt(x + 30, 2790, 'Shared monthly criteria', 42, True, NAVY)
txt(x + 30, 2846, 'Support ≥ 0.5% | Confidence ≥ 50%', 38, True, BLUE, width=CWD - 60)
txt(x + 30, 2896, 'Lift ≥ 1.2 | Antecedent orders ≥ 20', 38, width=CWD - 60)
txt(x + 30, 2946, 'Consequent must be observed.', 36, color=GRAY)

tag('test')
phase(3024, '3', 'Test', f'Aug–Nov 2011 · {test_orders:,} orders')
node(3140, 144, f'{rule_count} rules frozen after validation', 'Check each rule again in each test month.', 44)
bw = (CWD - 42) / 4
month_centers = [x + i * (bw + 14) + bw / 2 for i in range(4)]
S.line([(c, 3284), (c, 3312)], BLUE, 5)
S.line([(month_centers[0], 3312), (month_centers[-1], 3312)], BLUE, 5, cap='square')
for month_center in month_centers:
    S.arrow(month_center, 3312, month_center, 3344, BLUE, 5, 16)
for i, month in enumerate(['Aug', 'Sep', 'Oct', 'Nov']):
    xx = x + i * (bw + 14)
    S.rect(xx, 3356, bw, 92, PALE, 'none', 0, r=16)
    txt(xx + bw / 2, 3417, month, 42, True, NAVY, 'middle')
S.rect(x, 3496, CWD, 100, NAVY, 'none', 0, r=18)
txt(c, 3560, f'Monthly retention = rules passing / {rule_count}', 42, True, WHITE, 'middle', CWD - 40)
txt(x, 3666, 'One rule-month is one rule checked in one month.', 38, width=CWD)
S.paragraph(x, 3722, 'Rules with too little evidence stay in the denominator.', CWD, 36, 46, fill=GRAY)

# RIGHT: benchmark charts, the retention grid and the monthly results.
x = LEFT[2]
tag('algorithm_comparison')
section(x, 868, '03', 'Algorithm comparison')
for xx, label, color in [(x, 'Apriori', BLUE), (x + 240, 'FP-Growth', TEAL)]:
    S.rect(xx, 918, 32, 32, color, 'none', 0, r=7)
    txt(xx + 46, 948, label, 40, True)
comparison_chart(1022, 'Mining time (seconds)', 'seconds', 6, [0, 3, 6], 2)
comparison_chart(1412, 'Peak process memory (MiB)', 'peak_mib', 180, [0, 90, 180], 1, 'Discovery support')
panel(x, 1810, CWD, 228)
txt(x + 46, 1866, 'Same itemsets: 20,906 / 2,218 / 413.', 40, True, NAVY, width=CWD - 70)
txt(x + 46, 1920, 'Apriori: faster at 1% / 2% support;', 40, width=CWD - 70)
txt(x + 46, 1972, 'lower peak memory at all settings.', 40, width=CWD - 70)
txt(x + 46, 2018, '3-run medians; mining only; low-memory Apriori.', 34, color=GRAY, width=CWD - 70)

tag('test_grid')
section(x, 2116, '04', 'Test retention by rule group')
gx, gy = x + 164, 2280
gw, gh = (x + CWD - gx) / 3, 226
txt(gx + 1.5 * gw, 2184, 'Discovery support', 40, True, NAVY, 'middle')
S.text(x + 31, gy + 1.5 * gh, 'Discovery confidence', 40, 'bold', NAVY, 'middle',
       max_width=3 * gh, vertical=True)
for j, value in enumerate(['0.5%', '1%', '2%']):
    txt(gx + (j + .5) * gw, 2246, value, 42, True, anchor='middle')
for i, confidence in enumerate([.3, .5, .7]):
    txt(gx - 20, gy + (i + .5) * gh + 13, f'{confidence*100:g}%', 40, True, anchor='end')
    for j, support in enumerate([.005, .01, .02]):
        row = next(v for v in DATA['grid'] if v['support'] == support and v['confidence'] == confidence)
        xx, yy, cw, ch = gx + j * gw + 4, gy + i * gh + 4, gw - 8, gh - 8
        selected, excluded = row['selected'], row['rules'] < 20
        if excluded:
            S.rect(xx, yy, cw, ch, '#F0F2F5', EDGE, 3, r=16, dash=(15, 9))
        else:
            S.rect(xx, yy, cw, ch, retention_color(row['test']), 'none', 0, r=16)
        color = GRAY if excluded else WHITE if row['test'] >= .7 else INK
        top = yy + (78 if selected or excluded else 96)
        txt(xx + cw / 2, top, f'{row["test"]*100:.1f}%', 60, True, color, 'middle')
        txt(xx + cw / 2, top + 54, f'{row["rules"]:,} rules', 36, color=color, anchor='middle', width=cw - 16)
        if selected:
            S.rect(xx + 5, yy + 5, cw - 10, ch - 10, 'none', GOLD, 10, r=12)
            S.rect(xx + cw / 2 - 92, yy + ch - 68, 184, 48, GOLD, 'none', 0, r=24)
            txt(xx + cw / 2, yy + ch - 32, 'Selected', 34, True, NAVY, 'middle')
        if excluded:
            txt(xx + cw / 2, yy + ch - 30, 'Ineligible (<20)', 34, color=GRAY, anchor='middle', width=cw - 12)
txt(x, 3016, 'Each cell gives mean monthly test retention; darker = higher.', 34, width=CWD)
txt(x, 3062, 'Gold marks the group chosen in June–July.', 34, width=CWD)
panel(x, 3094, CWD, 190)
txt(x + 46, 3150, f'{test_passes / test_checks:.1%} test retention ({test_passes}/{test_checks} rule-months)',
    42, True, BLUE, width=CWD - 70)
txt(x + 46, 3202, f'{all_passed} of {rule_count} rules passed in all four test months.', 39, True, NAVY, width=CWD - 70)
txt(x + 46, 3250, 'Recheck a rule before using it in a later month.', 36, color=GRAY, width=CWD - 70)

tag('monthly_results')
txt(x, 3358, 'Monthly retention of the frozen rules', 42, True, NAVY, width=CWD)
pl, pr, pt, pb = x + 85, x + CWD, 3414, 3614
for value in [0, .5, 1]:
    yy = pb - value * (pb - pt)
    S.line([(pl, yy), (pr, yy)], GRID, 2)
    txt(pl - 18, yy + 12, f'{value*100:g}', 34, color=GRAY, anchor='end')
for i, row in enumerate(DATA['test_months']):
    cc = pl + (i + .5) * (pr - pl) / 4
    bh = row['retention'] * (pb - pt)
    bar(cc - 62, pb, 124, bh, BLUE)
    value_label(cc, pb - bh - 14, f'{row["retention"]*100:.1f}%', 38)
    txt(cc, 3666, ['Aug', 'Sep', 'Oct', 'Nov'][i], 40, True, anchor='middle')
    txt(cc, 3716, f'{row["passed"]}/{rule_count}', 36, color=GRAY, anchor='middle')
S.line([(pl, pb), (pr, pb)], AXIS, 3)

tag('footer')
S.rect(0, FOOT_Y, 3200, 4000 - FOOT_Y, NAVY, 'none', 0)
S.rect(0, FOOT_Y, 3200, 8, GOLD, 'none', 0)
txt(84, 3902, 'Data: UCI Online Retail (Chen, 2015). Methods: Agrawal & Srikant (1994); Han et al. (2000).', 28, color=WHITE)
txt(84, 3950, 'AI assistance: Codex and Claude Code supported implementation, analysis, writing and visuals. '
    'Methods via MLxtend; see report disclosure.', 28, color='#B9CEE9')
txt(3116, 3902, 'The Hong Kong University of Science and Technology (Guangzhou)', 28, True, WHITE, 'end')
txt(3116, 3950, 'Code: github.com/Chikit-WONG/AIAA3111-Introduction_to_Data_Mining-Final_Project', 28, color='#9FC4F2',
    anchor='end')

REQUIRED = ['AIAA 3111 | Introduction to Data Mining', 'Group 11', 'Chi Kit WONG', 'Yuxuan OUYANG', 'Zhicheng SUN',
            '78.2% validation retention', '111/142 rule-months passed', '79.2% test retention',
            '225/284 rule-months', '46 / 71', '17,901 study orders', '17,157', '744',
            'Supplementary analysis (Dec 1–9, 2011)', 'Co-purchase examples', 'Discovery confidence',
            'Discovery support']
CROPS = {
    'header': (0, 0, 3200, 705),
    'left': (40, 700, 1080, 3810),
    'middle': (1080, 700, 2120, 3810),
    'right': (2120, 700, 3160, 3810),
    'course_label': (65, 20, 1400, 115),
    'footer': (0, 3800, 3200, 4000),
}

if __name__ == '__main__':
    S.export_svg(BUILD / 'poster_editable.svg')
    S.export_pdf(BUILD / 'poster_800x1000mm.pdf')
    validation = S.validate()
    validation['pdf'] = render_and_check(BUILD / 'poster_800x1000mm.pdf', BUILD, REQUIRED,
                                         forbidden=['Limitations', '54.9%'], logo_images=1, crops=CROPS)
    body = [e['size'] * UNIT_PT for e in S.elements if e['kind'] == 'text' and e['tag'] not in {'header', 'column_headers', 'footer'}]
    validation['body_font_points'] = {'min': round(min(body), 1), 'max': round(max(body), 1)}
    (BUILD / 'qa/validation.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')
    (BUILD / 'poster_scene.json').write_text(json.dumps(S.elements, indent=2), encoding='utf-8')
    print(json.dumps(validation, indent=2))
