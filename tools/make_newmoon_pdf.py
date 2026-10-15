"""Typeset 'From the New Moon to the Next' as a PDF.

Grown out of the book.py that set 'From the Sunrise to the Next', and set in
the same face for the same reason: this machine's Chromium renders Cormorant
Garamond perfectly on screen but will not embed a webfont into its PDF export,
falling back to DejaVu every time. ReportLab embeds the TrueType directly.

Two things the first book did not have:

  * Phase headings in three parts — "Phase One", then the land, then the land's
    other name, the one the allegory is standing on. They come through the
    manuscript as "## kicker | title | subtitle", any part of which may be
    empty, and each opens a page of its own. Thirteen phases and an
    introduction, so the story reads as the thirteen chapters it is.

  * Footnotes. The piece carries nine, and they are not asides — they are the
    other half of it, the history running underneath the boy's own. They are
    set as endnotes rather than at the foot of the page: several run longer
    than the paragraph that calls them, and at the foot they would have pushed
    the text into a column an inch high. The marker in the text is a raised
    numeral; the note itself stands at the back under its own number.
"""
import pathlib, re, sys
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, KeepTogether)

MD, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
FD = pathlib.Path('/root/.fonts')
pdfmetrics.registerFont(TTFont('Cormorant', FD / 'CormorantGaramond-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Cormorant-It', FD / 'CormorantGaramond-Italic.ttf'))
pdfmetrics.registerFontFamily('Cormorant', normal='Cormorant', bold='Cormorant',
                              italic='Cormorant-It', boldItalic='Cormorant-It')

INK, DIM, FAINT, GOLD = '#1b1714', '#5b5048', '#8a7d72', '#8c6d2f'
body  = ParagraphStyle('body', fontName='Cormorant', fontSize=13.4, leading=19.6,
                       alignment=TA_JUSTIFY, textColor=INK, firstLineIndent=16,
                       spaceBefore=0, spaceAfter=0, hyphenationLang='')
first = ParagraphStyle('first', parent=body, firstLineIndent=0)
# The three lines of a phase opening. The kicker is letterspaced small capitals
# in all but name — Cormorant has no small-cap face here, so it is set small,
# tracked and faint, which reads the same way at this size.
kick  = ParagraphStyle('kick', fontName='Cormorant', fontSize=10, leading=14,
                       alignment=TA_CENTER, textColor=GOLD, spaceAfter=3.5*mm)
part  = ParagraphStyle('part', fontName='Cormorant', fontSize=20, leading=25,
                       alignment=TA_CENTER, textColor=INK)
psub  = ParagraphStyle('psub', fontName='Cormorant-It', fontSize=12.5, leading=17,
                       alignment=TA_CENTER, textColor=DIM, spaceBefore=2.5*mm)
ttl   = ParagraphStyle('ttl', fontName='Cormorant', fontSize=31, leading=36,
                       alignment=TA_CENTER, textColor=INK)
sub   = ParagraphStyle('sub', fontName='Cormorant-It', fontSize=14, leading=19,
                       alignment=TA_CENTER, textColor=DIM)
dat   = ParagraphStyle('dat', fontName='Cormorant', fontSize=10.5, leading=14,
                       alignment=TA_CENTER, textColor=FAINT)
# The notes, set smaller, with the number hanging out to the left of the text.
note  = ParagraphStyle('note', fontName='Cormorant', fontSize=11.2, leading=15.6,
                       alignment=TA_JUSTIFY, textColor=DIM,
                       leftIndent=9*mm, firstLineIndent=-9*mm, spaceAfter=4.5*mm)

def esc(s):
    """The manuscript keeps ASCII apostrophes; here they become typographic."""
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r"(?<=[A-Za-z])'(?=[A-Za-z])", '’', s)   # didn't, boy's
    s = re.sub(r"(?<=[A-Za-z])'(?![A-Za-z])", '’', s)   # Camels' home
    # Straight doubles in and out, by position.
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append('“' if open_q else '”'); open_q = not open_q
        else:
            out.append(ch)
    s = ''.join(out)
    # The raised numeral that calls a note.
    return re.sub(r'\[\^(\d+)\]', r'<super><font size="8">\1</font></super>', s)

# The kicker's letterspacing, done by hand: a space between every letter, and
# a wider gap between words. Spacing the whole string uniformly collapsed in
# the render — HTML eats the run of spaces between two words — so "PHASE ONE"
# came out reading PHASEONE.
TRACK = lambda s: '&nbsp;&nbsp;&nbsp;'.join(' '.join(w) for w in s.split())

blocks, title, subtitle, dateline, notes = [], None, None, None, []
for raw in MD.read_text(encoding='utf-8').split('\n\n'):
    b = raw.strip()
    if not b: continue
    if b.startswith('# '):   title = b[2:]
    elif b.startswith('### ') and not blocks and subtitle is None: subtitle = b[4:]
    elif b.startswith('*') and b.endswith('*') and not blocks and dateline is None:
        dateline = b.strip('*')
    elif b.startswith('## '):
        bits = [x.strip() for x in b[3:].split('|')]
        bits += [''] * (3 - len(bits))
        blocks.append(('part', bits[:3]))
    elif re.match(r'^\^\d+\.\s', b):
        n, txt = re.match(r'^\^(\d+)\.\s+(.*)$', b, re.S).groups()
        notes.append((n, ' '.join(txt.split())))
    else: blocks.append(('p', b))

story = [Spacer(1, 62*mm), Paragraph(esc(title), ttl), Spacer(1, 13*mm),
         Paragraph(esc(subtitle), sub), Spacer(1, 3*mm),
         Paragraph(esc(dateline), dat), PageBreak()]

prev = None
for i, (kind, val) in enumerate(blocks):
    if kind == 'part':
        kicker, head, tail = val
        if i: story.append(PageBreak())
        story.append(Spacer(1, 14*mm))
        grp = []
        if kicker: grp.append(Paragraph(TRACK(esc(kicker).upper()), kick))
        grp.append(Paragraph(esc(head), part))
        if tail: grp.append(Paragraph(esc(tail), psub))
        grp.append(Spacer(1, 9*mm))
        # The heading and the paragraph under it are one block, so a phase can
        # never open at the very foot of a page with its first line overleaf.
        nxt = blocks[i+1] if i+1 < len(blocks) else None
        if nxt and nxt[0] == 'p':
            grp.append(Paragraph(esc(nxt[1]), first))
        story.append(KeepTogether(grp))
        prev = 'part-consumed'
        continue
    if prev == 'part-consumed':
        prev = kind
        continue
    story.append(Paragraph(esc(val), body))
    prev = kind

if notes:
    story.append(PageBreak())
    story.append(Spacer(1, 14*mm))
    story.append(KeepTogether([Paragraph(TRACK('NOTES'), kick), Spacer(1, 9*mm)]))
    for n, txt in notes:
        story.append(Paragraph(
            f'<super><font size="8">{n}</font></super>&nbsp;&nbsp;{esc(txt)}', note))

L, R, T, B = 30*mm, 30*mm, 24*mm, 26*mm
def footer(canvas, doc):
    if doc.page == 1: return
    canvas.saveState()
    canvas.setFont('Cormorant', 10)
    canvas.setFillColor(FAINT)
    canvas.drawCentredString(LETTER[0] / 2, 15*mm, str(doc.page - 1))
    canvas.restoreState()

doc = BaseDocTemplate(str(OUT), pagesize=LETTER, leftMargin=L, rightMargin=R,
                      topMargin=T, bottomMargin=B, title=title,
                      author='Daniel Kahane')
frame = Frame(L, B, LETTER[0]-L-R, LETTER[1]-T-B, id='f',
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=footer)])
doc.build(story)
print('wrote', OUT.name, f'({OUT.stat().st_size//1024} KB)',
      f'| {len(blocks)} blocks, {len(notes)} notes')
