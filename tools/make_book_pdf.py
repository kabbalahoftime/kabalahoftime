"""Typeset one of the KoT books as a PDF.

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

  * Chapters inside a part, for the second book, which has four parts and
    chapters within two of them. "### title | subtitle" — centred, with air
    above, held together with the paragraph beneath so a chapter never opens
    at the foot of a page. The first ### in a file is still the book's
    subtitle; a ### after the text has begun is a chapter.

  * An epigraph line, "*...*" once the text has begun: the note under a part
    heading saying which draft it came from.

  * Footnotes. The first book carries nine, and they are not asides — they are the
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
# A chapter inside a part. Smaller than a part's title and not page-breaking,
# with its other name under it where it has one — the land's real name.
chap  = ParagraphStyle('chap', fontName='Cormorant', fontSize=15.5, leading=20,
                       alignment=TA_CENTER, textColor=INK, spaceBefore=11*mm)
csub  = ParagraphStyle('csub', fontName='Cormorant-It', fontSize=11.5, leading=15,
                       alignment=TA_CENTER, textColor=DIM, spaceBefore=1.5*mm)
# The line under a part heading that says where the draft came from.
epig  = ParagraphStyle('epig', fontName='Cormorant-It', fontSize=11.5, leading=16,
                       alignment=TA_CENTER, textColor=FAINT, spaceAfter=6*mm)
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
    elif b.startswith('### '):
        bits = [x.strip() for x in b[4:].split('|')]
        bits += [''] * (2 - len(bits))
        blocks.append(('chap', bits[:2]))
    elif b.startswith('*') and b.endswith('*'):
        blocks.append(('epig', b.strip('*')))
    elif re.match(r'^\^\d+\.\s', b):
        n, txt = re.match(r'^\^(\d+)\.\s+(.*)$', b, re.S).groups()
        notes.append((n, ' '.join(txt.split())))
    else: blocks.append(('p', b))

L, R, T, B = 30*mm, 30*mm, 24*mm, 26*mm
FW, FH = LETTER[0] - L - R, LETTER[1] - T - B       # the text block

# The air a phase opens with: above the number, and under the heading.
AIR_TOP, AIR_HEAD = 14*mm, 9*mm
# How little it may be squeezed to. Below these the opening stops reading as
# an opening and starts reading as a paragraph that happens to be centred.
MIN_TOP, MIN_HEAD = 5*mm, 6*mm

# The title page takes what the manuscript gives it. A book that has
# stopped calling itself a draft has no dateline, and the page should
# close up rather than print the word None.
story = [Spacer(1, 62*mm), Paragraph(esc(title), ttl)]
if subtitle: story += [Spacer(1, 13*mm), Paragraph(esc(subtitle), sub)]
if dateline: story += [Spacer(1, 3*mm), Paragraph(esc(dateline), dat)]
story.append(PageBreak())

# Gather the phases, each with everything that belongs under it in order.
phases, cur = [], None
for kind, val in blocks:
    if kind == 'part':
        cur = {'head': val, 'body': []}
        phases.append(cur)
    elif cur is not None:
        cur['body'].append((kind, val))

def _h(style, txt):
    return Paragraph(txt, style).wrap(FW, FH)[1]

def opening(q):
    """How much air this phase's opening should carry.

    A phase that runs a hair past the foot of its page sends a line or two
    over to a page of its own, and that page is then blank but for them.
    "The Pig and the Hare" was doing it with four words. The opening is the
    one place in the setting with any give — 23mm of it — so when a phase
    would spill by less than that, the air is taken back and the phase is
    held whole. Measured, not nudged by hand, so it still holds if the text
    is edited.

    Nothing is squeezed that does not need to be, and nothing is squeezed
    past the floor: a phase that genuinely runs two pages opens as wide as
    every other.
    """
    kicker, head, tail = q['head']
    h = AIR_TOP + AIR_HEAD
    if kicker: h += _h(kick, TRACK(esc(kicker).upper())) + kick.spaceAfter
    h += _h(part, esc(head))
    if tail:  h += psub.spaceBefore + _h(psub, esc(tail))
    for i, (kind, val) in enumerate(q['body']):
        if kind == 'chap':
            h += chap.spaceBefore + _h(chap, esc(val[0]))
            if val[1]: h += csub.spaceBefore + _h(csub, esc(val[1]))
        elif kind == 'epig':
            h += _h(epig, esc(val)) + epig.spaceAfter
        else:
            h += _h(first if i == 0 else body, esc(val))
    over = h - FH
    room = (AIR_TOP - MIN_TOP) + (AIR_HEAD - MIN_HEAD)
    if not (0 < over <= room - 2):
        return AIR_TOP, AIR_HEAD
    take = over + 2                       # 2pt so it is not sitting on the line
    top = max(MIN_TOP, AIR_TOP - take)
    return top, max(MIN_HEAD, AIR_HEAD - (take - (AIR_TOP - top)))

for i, q in enumerate(phases):
    kicker, head, tail = q['head']
    air_top, air_head = opening(q)
    if i: story.append(PageBreak())
    story.append(Spacer(1, air_top))
    grp = []
    if kicker: grp.append(Paragraph(TRACK(esc(kicker).upper()), kick))
    grp.append(Paragraph(esc(head), part))
    if tail: grp.append(Paragraph(esc(tail), psub))
    grp.append(Spacer(1, air_head))
    # The heading and whatever comes directly under it are one block, so a
    # part can never open at the very foot of a page with its first line
    # overleaf.
    rest = list(q['body'])
    if rest and rest[0][0] in ('p', 'epig'):
        k, v = rest.pop(0)
        grp.append(Paragraph(esc(v), epig if k == 'epig' else first))
        # An epigraph is a caption on the heading, so the paragraph after it
        # is held too — otherwise the part can open on a line about which
        # draft this is and nothing else.
        if k == 'epig' and rest and rest[0][0] == 'p':
            grp.append(Paragraph(esc(rest.pop(0)[1]), first))
    story.append(KeepTogether(grp))
    # A chapter is held with its first paragraph for the same reason.
    j = 0
    while j < len(rest):
        kind, val = rest[j]
        if kind == 'chap':
            cg = [Paragraph(esc(val[0]), chap)]
            if val[1]: cg.append(Paragraph(esc(val[1]), csub))
            cg.append(Spacer(1, 5*mm))
            if j + 1 < len(rest) and rest[j + 1][0] == 'p':
                cg.append(Paragraph(esc(rest[j + 1][1]), first))
                j += 1
            story.append(KeepTogether(cg))
        elif kind == 'epig':
            story.append(Paragraph(esc(val), epig))
        else:
            story.append(Paragraph(esc(val), body))
        j += 1

if notes:
    story.append(PageBreak())
    story.append(Spacer(1, 14*mm))
    story.append(KeepTogether([Paragraph(TRACK('NOTES'), kick), Spacer(1, 9*mm)]))
    for n, txt in notes:
        story.append(Paragraph(
            f'<super><font size="8">{n}</font></super>&nbsp;&nbsp;{esc(txt)}', note))

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
