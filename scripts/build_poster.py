"""Editable ReportLab source for a provisional A1 landscape course poster."""
from pathlib import Path
import csv
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A1, landscape
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
NAVY = HexColor('#15324F')
BLUE = HexColor('#317CB0')
TEAL = HexColor('#198B83')
GRAY = HexColor('#536779')


def main():
    summary = json.loads((ROOT/'results/summary.json').read_text())
    team = json.loads((ROOT/'configs/team.json').read_text())
    with (ROOT/'results/tables/customer_sensitivity.csv').open() as f:
        rows = list(csv.DictReader(f))
    known = sum(float(r['retention_rate']) for r in rows)/len(rows)*100
    out = ROOT/'artifacts'
    out.mkdir(exist_ok=True)
    target = out/'Poster.pdf'
    W,H = landscape(A1)
    c = canvas.Canvas(str(target), pagesize=(W,H))
    c.setTitle('Beyond Frequent Co-Purchases - AIAA3111 Group 11')
    c.setAuthor('Chi Kit WONG; Yuxuan OUYANG; Zhicheng SUN')
    margin = 64

    def text(value, x, y, size=22, bold=False, color=NAVY):
        c.setFillColor(color)
        c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
        c.drawString(x,y,value)

    def para(value, x, y, width, size=22, leading=None, color=NAVY):
        style=ParagraphStyle('p',fontName='Helvetica',fontSize=size,leading=leading or size*1.35,textColor=color,spaceAfter=0)
        p=Paragraph(value,style)
        _,height=p.wrap(width,2000)
        p.drawOn(c,x,y-height)
        return y-height

    def heading(value,x,y):
        text(value,x,y,29,True,TEAL)
        return y-25

    def picture(name,x,top,width):
        source=ROOT/'results/figures'/name
        im=ImageReader(str(source)); iw,ih=im.getSize(); height=width*ih/iw
        c.drawImage(im,x,top-height,width,height,mask='auto')
        return top-height

    text('Beyond Frequent Co-Purchases',margin,H-95,58,True)
    text('A Study of Temporal Stability in Retail Association Rules',margin,H-147,34)
    byline='Group 11 | '+ '   |   '.join(f"{m['name']} ({m['student_id']})" for m in team['members'])
    text(byline,margin,H-188,21,color=GRAY)
    c.setFillColor(HexColor('#EDF4F7'))
    c.rect(margin,H-343,W-2*margin,115,fill=1,stroke=0)
    positions=[margin+30,margin+790,margin+1540]
    headline=[(f"{summary['mean_monthly_test_retention']*100:.1f}%",'mean monthly retention'),(f"{summary['rules_retained_all_test_months']} / {summary['selected_rules']}",'rules retained in all four test months'),('Aug-Nov 2011','held-out evaluation after validation')]
    for x,(number,label) in zip(positions,headline):
        text(number,x,H-285,48,True)
        text(label,x,H-322,22,color=GRAY)

    left=margin; lw=690; rx=810; rw=W-rx-margin
    y=H-400
    y=heading('Question',left,y)
    y=para('Do purchasing associations discovered in earlier orders remain reliable in later months?',left,y,lw,25)-38
    y=heading('Data and unit of analysis',left,y)
    y=para('<b>541,909</b> UCI retail line items become <b>19,773</b> cleaned baskets; <b>17,901</b> UK orders define the primary population. Each invoice is a set of product codes. Missing customer IDs and singleton baskets are retained.',left,y,lw,22)-34
    y=heading('Chronological design',left,y)
    y=para('<b>Discover:</b> Dec 2010-May 2011<br/><b>Select:</b> Jun-Jul 2011<br/><b>Test:</b> Aug-Nov 2011<br/>Apriori and FP-Growth use the same input and maximum itemset length 3. Parameters are selected before test metrics are computed.',left,y,lw,22)-34
    y=heading('A common retention standard',left,y)
    y=para('Support at least <b>0.5%</b>, confidence at least <b>50%</b>, lift at least <b>1.2</b>, and at least <b>20 antecedent orders</b> per month.<br/>Denominator: all 71 frozen rules. Insufficient evidence is reported separately.',left,y,lw,22)-34
    y=heading('What qualifies the finding',left,y)
    y=para(f'With customer-ID-recorded orders only, retention falls to <b>{known:.1f}%</b>. Large and unidentified baskets affect the result. A narrower 14-rule setting retains 100%, but is below the predeclared 20-rule floor.',left,y,lw,22)-25
    y=para('One retailer, four test months, dependent rules and no inventory/promotion history limit generalization. These associations do not establish causation or sales uplift.',left,y,lw,21,color=GRAY)
    if y < 145:
        raise RuntimeError(f'Poster text exceeds content area: {y}')

    text('Follow the same rules into future months',rx,H-400,31,True)
    bottom=picture('03_temporal_retention.png',rx+80,H-426,rw-160)
    text('Quantity and reliability trade off',rx,bottom-38,28,True)
    text('Equivalent mining outputs',rx+rw/2+20,bottom-38,28,True)
    width=(rw-32)/2
    end1=picture('04_threshold_sensitivity.png',rx,bottom-62,width)
    end2=picture('02_benchmark.png',rx+width+32,bottom-62,width)
    end2=para('All itemset/count signatures agree. Mining took about <b>0.3-5.7 seconds</b> per run, with worker peaks below <b>160 MiB</b> on the local CPU. The speed ordering is implementation- and setting-dependent.',rx+width+32,end2-18,width,20)
    if min(end1,end2) < 145:
        raise RuntimeError(f'Poster figures exceed content area: {end1:.1f}, {end2:.1f}')

    c.setStrokeColor(HexColor('#B8C7D1')); c.setLineWidth(1)
    c.line(margin,120,W-margin,120)
    text('Source: Chen (2015), UCI Online Retail, doi:10.24432/C5BW33 (CC BY 4.0). Methods: Agrawal & Srikant (1994); Han et al. (2000); MLxtend.',margin,90,16,color=GRAY)
    text('AIGC: OpenAI Codex assisted implementation, experiments and drafting; team review and revision are required. Full evidence and limitations are in the report.',margin,62,16,color=GRAY)
    c.showPage(); c.save()
    print(target)


if __name__=='__main__':
    main()
