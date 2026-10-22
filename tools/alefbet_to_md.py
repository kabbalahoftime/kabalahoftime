"""Turn the Alef Bet appendix into a manuscript the shared typesetter can set.

The document opens with a summary table and then is a book: sixteen cycles
of twenty-two days and a half cycle at the end, each with its two letters,
the two creatures that sing for them in Perek Shirah, the mishnayot of
Pirkei Avot that count for them, and the commentary that says why the four
belong together.

The table is a contents of what follows and is left out here: every line of
it is expanded in the prose, where the mishnayot are given whole rather than
trailing off in an ellipsis.

Each cycle becomes a part — its letters the title, its weeks the line under
them — with the creatures as the epigraph beneath, which is the shape the
other books already use.
"""
import pathlib, re, sys, zipfile
from xml.etree import ElementTree as ET

SRC, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
root = ET.fromstring(zipfile.ZipFile(SRC).read('word/document.xml'))
BR = '\x01'
def segs(el):
    """A paragraph's text, split where the writer pressed shift-return.

    The document carries two hundred and thirty-two of those, and they are
    doing the work of paragraph breaks — drop them and sentences weld
    together: "running until the middle of Sukkot.The Talmud teaches".
    """
    buf = []
    for n in el.iter():
        if n.tag == W + 't': buf.append(n.text or '')
        elif n.tag == W + 'br': buf.append(BR)
    return [' '.join(s.split()) for s in ''.join(buf).split(BR)]

ORD = ('First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|'
       'Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth')
CYCLE = re.compile(r'^((?:%s)\s+Cycle|Additional Half Cycle)\s*:\s*(.*)$' % ORD, re.I)

paras = [s for el in root.find(W + 'body') if el.tag == W + 'p'
         for s in segs(el) if s]

parts, cur = [], None
for p in paras:
    m = CYCLE.match(p)
    if m:
        cur = {'kicker': m.group(1).upper(), 'when': m.group(2).strip(),
               'letters': '', 'song': '', 'body': []}
        parts.append(cur); continue
    if cur is None: continue                       # the title, before any cycle
    if not cur['letters']: cur['letters'] = p; continue
    if not cur['song']:    cur['song'] = p;    continue
    cur['body'].append(p)

out = ['# Hebrew Alphabet, Perek Shirah and Pirkei Avot', '',
       '### an appendix to the Kabbalah of Time', '']
for c in parts:
    out += ['## %s | %s | %s' % (c['kicker'], c['letters'], c['when']), '']
    if c['song']: out += ['*%s*' % c['song'], '']
    for b in c['body']: out += [b, '']
OUT.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')
print('wrote %s | %d parts, %d paragraphs'
      % (OUT.name, len(parts), sum(len(c['body']) for c in parts)))
