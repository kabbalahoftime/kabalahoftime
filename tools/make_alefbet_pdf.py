"""Typeset the Alef Bet appendix as a PDF.

The other books on the shelf are prose and verse, and the shared typesetter
sets them. This one is a table — thirty-three rows across six columns, the
letters against their cycle, their creature in Perek Shirah, their mishnah in
Pirkei Avot and their weeks of the year — so it has a setter of its own
rather than bending that one out of shape.

Read straight out of the .docx, because the document is the source and a
PDF exported from it would be a second copy to keep in step. Set landscape:
the Pirkei Avot column runs to two hundred and sixty characters, and in
portrait it becomes a gutter.
"""
import pathlib, re, sys, zipfile
from xml.etree import ElementTree as ET
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle)

SRC, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
FD = pathlib.Path('/root/.fonts')
pdfmetrics.registerFont(TTFont('Cormorant', FD / 'CormorantGaramond-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Cormorant-It', FD / 'CormorantGaramond-Italic.ttf'))

INK, DIM, GOLD, RULE = colors.HexColor('#1b1714'), colors.HexColor('#5b5048'), \
                       colors.HexColor('#8c6d2f'), colors.HexColor('#e3d9c6')

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
root = ET.fromstring(zipfile.ZipFile(SRC).read('word/document.xml'))
cell = lambda el: ' '.join(''.join(t.text or '' for t in el.iter(W + 't')).split())
tbl = next(root.iter(W + 'tbl'))
rows = [[cell(tc) for tc in tr.findall(W + 'tc')] for tr in tbl.findall(W + 'tr')]

# The document writes G\u2011d with a non-breaking hyphen, which Cormorant
# has no glyph for and ReportLab draws as a black box. It is a hyphen that
# asks not to be broken across lines; in a table cell nothing would break
# it anyway, so a plain hyphen says the same thing and can be drawn.
def esc(s):
    s = s.replace('\u2011', '-').replace('\u00a0', ' ')
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

ttl  = ParagraphStyle('ttl', fontName='Cormorant', fontSize=19, leading=24,
                      alignment=TA_CENTER, textColor=INK)
sub  = ParagraphStyle('sub', fontName='Cormorant-It', fontSize=11, leading=15,
                      alignment=TA_CENTER, textColor=DIM, spaceBefore=2*mm)
head = ParagraphStyle('head', fontName='Cormorant', fontSize=8.6, leading=11,
                      textColor=GOLD, alignment=TA_CENTER)
body = ParagraphStyle('body', fontName='Cormorant', fontSize=9.6, leading=12.8,
                      textColor=INK)
mid  = ParagraphStyle('mid', parent=body, alignment=TA_CENTER, textColor=DIM)
note = ParagraphStyle('note', parent=body, fontName='Cormorant-It', textColor=DIM)

PAGE = landscape(LETTER)
L = R = 16*mm
T, B = 18*mm, 16*mm
doc = BaseDocTemplate(str(OUT), pagesize=PAGE, leftMargin=L, rightMargin=R,
                      topMargin=T, bottomMargin=B,
                      title='Kabbalah of Time — Hebrew Alphabet, Perek Shirah and Pirkei Avot',
                      author='Kabbalah of Time')
def foot(c, d):
    c.setFont('Cormorant', 8.5); c.setFillColor(DIM)
    c.drawCentredString(PAGE[0] / 2, 9*mm, str(c.getPageNumber()))
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(
    L, B, PAGE[0] - L - R, PAGE[1] - T - B, id='f',
    leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=foot)])

HEADS = ['', 'Letter', 'Cycle', 'Perek Shirah', 'Pirkei Avot', 'Weeks of the year']
WIDTH = [11*mm, 26*mm, 23*mm, 40*mm, 104*mm, 44*mm]
data = [[Paragraph(esc(h), head) for h in HEADS]]
for r in rows:
    r = (r + [''] * 6)[:6]
    data.append([Paragraph(esc(r[0]), mid), Paragraph(esc(r[1]), body),
                 Paragraph(esc(r[2]), mid), Paragraph(esc(r[3]), body),
                 Paragraph(esc(r[4]), body), Paragraph(esc(r[5]), note)])

t = Table(data, colWidths=WIDTH, repeatRows=1)
t.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ('LINEBELOW', (0, 0), (-1, 0), 0.7, GOLD),
    ('LINEBELOW', (0, 1), (-1, -2), 0.35, RULE),
]))

story = [Paragraph('Hebrew Alphabet, Perek Shirah and Pirkei Avot', ttl),
         Paragraph('an appendix to the Kabbalah of Time', sub),
         Spacer(1, 7*mm), t]
doc.build(story)
print('wrote %s (%d KB) | %d rows' % (OUT.name, OUT.stat().st_size // 1024, len(rows)))
