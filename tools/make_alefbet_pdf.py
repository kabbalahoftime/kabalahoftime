"""Typeset the Alef Bet appendix as a PDF.

The other books on the shelf are prose and verse, and the shared typesetter
sets them. This one is a table — the twenty-seven letters against their
cycle, their creature in Perek Shirah, their mishnah in Pirkei Avot and their
weeks of the year — so it has a setter of its own rather than bending that
one out of shape. It keeps the same faces, the same palette and the same
title page.

Read straight out of the .docx, because the document is the source and a PDF
exported by hand would be a second copy to keep in step. Landscape: the
Pirkei Avot column runs to two hundred and sixty characters, and in portrait
it becomes a gutter.

The document names its letters and does not write them. They are written
here, beside the name, in the face the site sets Hebrew in — which is the
one thing a table of the alphabet should not have to be told.
"""
import pathlib, sys, zipfile
from xml.etree import ElementTree as ET
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak)

SRC, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
FD = pathlib.Path('/root/.fonts')
pdfmetrics.registerFont(TTFont('Cormorant', FD / 'CormorantGaramond-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Cormorant-It', FD / 'CormorantGaramond-Italic.ttf'))
_HEB = FD / 'FrankRuhlLibre-Hebrew.ttf'
if not _HEB.exists():
    from fontTools.ttLib import TTFont as _TTF
    _w = pathlib.Path(__file__).resolve().parent.parent / 'fonts' / 'frank-ruhl-libre-hebrew.woff2'
    _f = _TTF(str(_w)); _f.flavor = None; _f.save(str(_HEB))
pdfmetrics.registerFont(TTFont('Hebrew', _HEB))

INK  = colors.HexColor('#1b1714')
DIM  = colors.HexColor('#5b5048')
FAINT= colors.HexColor('#8a7d72')
GOLD = colors.HexColor('#8c6d2f')
RULE = colors.HexColor('#e7ddc9')

# The letter each name stands for. The document names them and the alphabet
# is what the table is of, so they are drawn.
GLYPH = {
 'alef': 'א', 'beit': 'ב', 'gimmel': 'ג', 'dalet': 'ד', 'heh': 'ה', 'vav': 'ו',
 'zayin': 'ז', 'chet': 'ח', 'tet': 'ט', 'yud': 'י', 'kaf': 'כ', 'lamed': 'ל',
 'mem': 'מ', 'nun': 'נ', 'samech/ayin': 'ס ע', 'peh': 'פ', 'tzadi': 'צ',
 'kuf': 'ק', 'resh': 'ר', 'shin': 'ש', 'tav': 'ת', 'kaf sofit': 'ך',
 'mem sofit': 'ם', 'nun sofit': 'ן', 'peh sofit': 'ף', 'tzadi sofit': 'ץ',
}
TRACK = lambda s: '&nbsp;'.join(s)          # the letterspacing the app uses by hand

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
root = ET.fromstring(zipfile.ZipFile(SRC).read('word/document.xml'))
cell = lambda el: ' '.join(''.join(t.text or '' for t in el.iter(W + 't')).split())
rows = [[cell(tc) for tc in tr.findall(W + 'tc')]
        for tr in next(root.iter(W + 'tbl')).findall(W + 'tr')]

def esc(s):
    # The document writes G-d with a non-breaking hyphen, which Cormorant has
    # no glyph for and ReportLab draws as a black box. In a table cell nothing
    # would break it anyway, so a plain hyphen says the same and can be drawn.
    s = s.replace('‑', '-').replace(' ', ' ')
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

ttl  = ParagraphStyle('ttl', fontName='Cormorant', fontSize=27, leading=33,
                      alignment=TA_CENTER, textColor=INK)
sub  = ParagraphStyle('sub', fontName='Cormorant-It', fontSize=13, leading=18,
                      alignment=TA_CENTER, textColor=DIM)
kick = ParagraphStyle('kick', fontName='Cormorant', fontSize=8.4, leading=11,
                      alignment=TA_CENTER, textColor=GOLD)
heb  = ParagraphStyle('heb', fontName='Hebrew', fontSize=16, leading=19,
                      alignment=TA_CENTER, textColor=GOLD)
name = ParagraphStyle('name', fontName='Cormorant', fontSize=9.4, leading=12,
                      alignment=TA_CENTER, textColor=INK, spaceBefore=1)
num  = ParagraphStyle('num', fontName='Cormorant', fontSize=8.6, leading=11,
                      alignment=TA_CENTER, textColor=FAINT)
cyc  = ParagraphStyle('cyc', fontName='Cormorant-It', fontSize=9.2, leading=12,
                      alignment=TA_CENTER, textColor=GOLD)
body = ParagraphStyle('body', fontName='Cormorant', fontSize=9.8, leading=12.8,
                      textColor=INK)
song = ParagraphStyle('song', parent=body, textColor=DIM)
when = ParagraphStyle('when', fontName='Cormorant-It', fontSize=9, leading=12.4,
                      textColor=FAINT)

PAGE = landscape(LETTER)
L = R = 17*mm
T, B = 17*mm, 15*mm
doc = BaseDocTemplate(str(OUT), pagesize=PAGE, leftMargin=L, rightMargin=R,
                      topMargin=T, bottomMargin=B,
                      title='Hebrew Alphabet, Perek Shirah and Pirkei Avot',
                      author='Kabbalah of Time')
def foot(c, d):
    if c.getPageNumber() == 1: return        # the title page carries no number
    c.setFont('Cormorant', 8.6); c.setFillColor(FAINT)
    c.drawCentredString(PAGE[0] / 2, 8*mm, str(c.getPageNumber() - 1))
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(
    L, B, PAGE[0] - L - R, PAGE[1] - T - B, id='f',
    leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=foot)])

HEADS = ['', 'The Letter', 'Cycle', 'Perek Shirah', 'Pirkei Avot', 'Weeks of the Year']
WIDTH = [10*mm, 30*mm, 22*mm, 39*mm, 103*mm, 44*mm]
data = [[Paragraph(TRACK(h.upper()), kick) if h else '' for h in HEADS]]
starts = []                                   # rows that open a cycle
for r in rows:
    r = (r + [''] * 6)[:6]
    glyph = GLYPH.get(r[1].strip().lower(), '')
    letter = ((('<font name="Hebrew" size="16" color="#8c6d2f">%s</font><br/>' % glyph)
               if glyph else '') + esc(r[1]))
    if r[2].strip(): starts.append(len(data))
    data.append([Paragraph(esc(r[0]), num),
                 Paragraph(letter, name),
                 Paragraph(esc(r[2]), cyc),
                 Paragraph(esc(r[3]), song),
                 Paragraph(esc(r[4]), body),
                 Paragraph(esc(r[5]), when)])

# Five and six, not six and seven: at the looser setting the last two
# letters fell onto a fifth page by themselves, and two rows alone under a
# repeated heading is not a page, it is a remainder.
style = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
         ('TOPPADDING', (0, 0), (-1, -1), 5),
         ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
         ('LEFTPADDING', (0, 0), (-1, -1), 6),
         ('RIGHTPADDING', (0, 0), (-1, -1), 6),
         ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
         ('LINEBELOW', (0, 0), (-1, 0), 0.7, GOLD),
         ('LINEBELOW', (0, 1), (-1, -2), 0.3, RULE)]
# A cycle is two letters, and the eye should be able to see where one ends.
for i in starts[1:]:
    style.append(('LINEABOVE', (0, i), (-1, i), 0.55, colors.HexColor('#d8c9a8')))
t = Table(data, colWidths=WIDTH, repeatRows=1)
t.setStyle(TableStyle(style))

doc.build([Spacer(1, 52*mm),
           Paragraph('Hebrew Alphabet, Perek Shirah and Pirkei Avot', ttl),
           Spacer(1, 9*mm),
           Paragraph('an appendix to the Kabbalah of Time', sub),
           PageBreak(), t])
print('wrote %s (%d KB) | %d rows, %d cycles'
      % (OUT.name, OUT.stat().st_size // 1024, len(rows), len(starts)))
