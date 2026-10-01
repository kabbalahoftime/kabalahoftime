"""Split the companion PDF into one entry per day of the Kabbalah of Time year.

Reads the paragraph stream from pdftxt2 and segments it on the "Day N — Title"
headings, keeping the week and movement each day sits under. Writes
companion.json: { generated, source, days: { "1": {...}, ... } }
"""
import re, json, sys, unicodedata
from pdftxt2 import paragraphs

LIG = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi',
       'ﬄ': 'ffl', 'ﬅ': 'st', 'ﬆ': 'st'}

def clean(s):
    for k, v in LIG.items(): s = s.replace(k, v)
    s = unicodedata.normalize('NFC', s)
    return re.sub(r'\s+', ' ', s).strip()

DAY   = re.compile(r'^Day (\d+)\s+[—–-]\s+(.+)$')
WEEK  = re.compile(r'^Week (\d+)\s+[—–-]\s+(.+?)(?:\s*\(Days [\d–—-]+\))?$')
NAMED = re.compile(r"^The (First|Second|Third) Week\s+[—–-]\s+(.+)$", re.I)
MOVE  = re.compile(r'^(Movement [IVX]+)\s+[—–-]\s+(.+)$')
HEADR = re.compile(r'^Movement [IVX]+: ')          # the running week epigraph
DRAFT = re.compile(r'^Draft for Daniel')
MOCHIN = re.compile(r'^The Mochin$')
PRACT = re.compile(r"^(?:Today's practice|Practice)\s*:\s*(.+)$", re.S)
TEASE = re.compile(r'^(?:Teaser|Tomorrow|Next)\s*:\s*(.+)$', re.S)

ORDINAL = {'First': 1, 'Second': 2, 'Third': 3}

def build():
    paras = [clean(p) for p in paragraphs()]
    # Everything before "Day 1 — " is the contents page.
    start = next(i for i, p in enumerate(paras) if DAY.match(p) and DAY.match(p).group(1) == '1')
    # Walk back over the week/movement headings that introduce day 1.
    head = max(0, start - 6)
    days, cur = {}, None
    movement = week = weektitle = movetitle = None
    weeknote = None
    for p in paras[head:]:
        m = MOVE.match(p)
        if m and not HEADR.match(p):
            movement, movetitle = m.group(1), m.group(2); continue
        if MOCHIN.match(p):
            movement, movetitle = 'The Mochin', 'Chochmah, Binah, Da’at'; continue
        m = NAMED.match(p)
        if m:
            week, weektitle, weeknote = ORDINAL[m.group(1).title()], m.group(2), None; continue
        m = WEEK.match(p)
        if m:
            week, weektitle, weeknote = int(m.group(1)), m.group(2), None; continue
        if DRAFT.match(p): continue
        if HEADR.match(p):
            # "Movement IV: The Ten Cycles (Weeks 22-31). <the week's epigraph>"
            rest = p.split('. ', 1)
            weeknote = rest[1].strip() if len(rest) > 1 and len(rest[1]) > 20 else None
            continue
        m = DAY.match(p)
        if m:
            n = int(m.group(1))
            cur = {'n': n, 'title': m.group(2).strip(), 'body': [],
                   'practice': '', 'teaser': '',
                   'week': week, 'weekTitle': weektitle,
                   'movement': movement, 'movementTitle': movetitle}
            if weeknote: cur['weekNote'] = weeknote
            days[n] = cur
            continue
        if cur is None: continue
        m = PRACT.match(p)
        if m: cur['practice'] = m.group(1).strip(); continue
        m = TEASE.match(p)
        if m: cur['teaser'] = m.group(1).strip(); continue
        cur['body'].append(p)
    return days

if __name__ == '__main__':
    days = build()
    missing = [n for n in range(1, 365) if n not in days]
    nobody = [n for n, d in days.items() if not d['body']]
    nopract = [n for n, d in days.items() if not d['practice']]
    notease = [n for n, d in days.items() if not d['teaser']]
    extra = [n for n in days if n < 1 or n > 364]
    print('days found      :', len(days))
    print('missing 1-364   :', missing[:30], '…' if len(missing) > 30 else '')
    print('out of range    :', extra)
    print('no body         :', nobody)
    print('no practice     :', nopract)
    print('no teaser       :', notease)
    wk = sorted({(d['week'], d['weekTitle']) for d in days.values() if d['week']})
    print('weeks           :', len(wk))
    if len(sys.argv) > 1:
        for n in [int(x) for x in sys.argv[1:]]:
            print('\n=== Day', n, json.dumps(days.get(n), indent=1, ensure_ascii=False)[:1400])
