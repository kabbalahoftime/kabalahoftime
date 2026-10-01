"""Split the UPDATED manuscript into one entry per day of the KoT year.

Same shape as the first builder, with two repairs the new producer needs:
page numbers are drawn as ordinary text and land as paragraphs of their own,
and a paragraph that crosses a page break arrives in two pieces with the
number wedged between them.
"""
import re, json, unicodedata, datetime, os
from pdftxt3 import paragraphs

LIG = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl'}

def clean(s):
    for k, v in LIG.items(): s = s.replace(k, v)
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip()

DAY   = re.compile(r'^Day (\d+)\s+[—–-]\s+(.+)$')
WEEK  = re.compile(r'^(?:[–-]\s*)?Week (\d+)\s+[—–-]\s+(.+?)(?:\s*\(Days [\d–—-]+\))?$')
NAMED = re.compile(r"^(?:[–-]\s*)?The (First|Second|Third) Week\s+[—–-]\s*(.*)$", re.I)
MOVE  = re.compile(r'^(?:[–-]\s*)?(Movement [IVX]+)\s+[—–-]\s+(.+)$')
HEADR = re.compile(r'^Movement [IVX]+: ')
DRAFT = re.compile(r'^Draft for Daniel')
MOCHIN = re.compile(r'^(?:[–-]\s*)?The Mochin$')
PAGENO = re.compile(r'^\d{1,3}$')
PRACT = re.compile(r"^(?:Today's practice|Practice)\s*:\s*(.+)$", re.S)
TEASE = re.compile(r'^(?:Teaser|Tomorrow|Next week|Next)\s*:\s*(.+)$', re.S)
ORDINAL = {'First': 1, 'Second': 2, 'Third': 3}
ENDS = tuple('.!?:;"’”)…')

def source():
    """Paragraphs, with page numbers dropped and page-split ones rejoined."""
    raw = [clean(p) for p in paragraphs()]
    raw = [p for p in raw if p and not PAGENO.match(p)]
    out = []
    for p in raw:
        # A paragraph interrupted by a page break: the tail starts lowercase
        # and the head stopped without finishing a sentence.
        if (out and not out[-1].endswith(ENDS) and p[:1].islower()
                and not DAY.match(p) and not WEEK.match(p)):
            out[-1] = out[-1] + ' ' + p
        else:
            out.append(p)
    return out

def build():
    paras = source()
    start = next(i for i, p in enumerate(paras)
                 if DAY.match(p) and DAY.match(p).group(1) == '1')
    days, cur = {}, None
    movement = movetitle = week = weektitle = None
    for p in paras[max(0, start - 8):]:
        m = MOVE.match(p)
        if m and not HEADR.match(p): movement, movetitle = m.group(1), m.group(2); continue
        if MOCHIN.match(p): movement, movetitle = 'The Mochin', 'Chochmah, Binah, Da’at'; continue
        m = NAMED.match(p)
        if m: week, weektitle = ORDINAL[m.group(1).title()], m.group(2).strip(); continue
        m = WEEK.match(p)
        if m: week, weektitle = int(m.group(1)), m.group(2).strip(); continue
        if DRAFT.match(p) or HEADR.match(p): continue
        m = DAY.match(p)
        if m:
            n = int(m.group(1))
            cur = {'n': n, 'title': m.group(2).strip(), 'body': [], 'practice': '', 'teaser': '',
                   'week': week, 'weekTitle': weektitle,
                   'movement': movement, 'movementTitle': movetitle}
            days[n] = cur
            continue
        if cur is None: continue
        m = PRACT.match(p)
        if m: cur['practice'] = m.group(1).strip(); continue
        m = TEASE.match(p)
        if m: cur['teaser'] = m.group(1).strip(); continue
        cur['body'].append(p)
    return days

LEAD = [(re.compile(r'^Next week\s*[—–-]\s*', re.I), 'Next week'),
        (re.compile(r'^Next\s*[:—–-]\s*',     re.I), 'Next'),
        (re.compile(r'^Tomorrow\s*[:—–-]\s*', re.I), 'Tomorrow')]
def split_lead(s):
    for rx, word in LEAD:
        if rx.match(s): return word, rx.sub('', s, count=1).strip()
    return 'Tomorrow', s

WEEK_TITLES = {1: "A Beginner's On-Ramp", 2: "How to Read a Week", 3: "Seven Songs for Seven Days"}

if __name__ == '__main__':
    days = build()
    miss = [n for n in range(1, 365) if n not in days]
    print('days          :', len(days), '| missing:', miss[:20])
    print('no body       :', [n for n, e in days.items() if not e['body']])
    print('no practice   :', [n for n, e in days.items() if not e['practice']])
    print('no teaser     :', [n for n, e in days.items() if not e['teaser']])
    print('fortnight     :', sum(json.dumps(e).count('fortnight') for e in days.values()))
    for d in days.values():
        if d['week'] in WEEK_TITLES: d['weekTitle'] = WEEK_TITLES[d['week']]
        d['teaserLead'], d['teaser'] = (split_lead(d['teaser']) if d['teaser'] else ('', ''))
    out = {'title': 'A Year Inside the Day',
           'subtitle': "A 52-week beginner's curriculum in the Kabbalah of Time",
           'pdf': 'a-year-inside-the-day.pdf',
           'generated': datetime.date.today().isoformat(),
           'days': {str(n): days[n] for n in range(1, 365)}}
    p = '/home/user/kabalahoftime/companion.json'
    open(p, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
    print('wrote', p, os.path.getsize(p), 'bytes')
