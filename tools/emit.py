"""Write companion.json for the app: the PDF, split by day, with the
post-PDF edits applied."""
import json, datetime, os
from build_companion import build
from overrides import OVERRIDES, TEXT_FIXES, WEEK_TITLES

def fix(s):
    for a, b in TEXT_FIXES: s = s.replace(a, b)
    return s

days = build()
for n, ov in OVERRIDES.items():
    if n not in days: raise SystemExit(f'override for a day the PDF does not have: {n}')
    days[n].update(ov)

import re

# The manuscript writes its last line two ways. Weeks 1-3 say "Tomorrow: the
# hours have their own character too."; weeks 4 on say "Teaser: Tomorrow —
# fifteen: why this number." Stripping only the "Teaser:" left the second kind
# still carrying its own "Tomorrow", which the card's label then said twice.
# So the lead word is taken off the text and kept beside it, and the few that
# point past tomorrow — to next week, or to the movement after — keep theirs.
LEAD = [(re.compile(r'^Next week\s*[—–-]\s*', re.I), 'Next week'),
        (re.compile(r'^Next\s*[:—–-]\s*',     re.I), 'Next'),
        (re.compile(r'^Tomorrow\s*[:—–-]\s*', re.I), 'Tomorrow')]

def split_lead(s):
    for rx, word in LEAD:
        if rx.match(s): return word, rx.sub('', s, count=1).strip()
    return 'Tomorrow', s

for d in days.values():
    if d.get('week') in WEEK_TITLES: d['weekTitle'] = WEEK_TITLES[d['week']]
    d['title']    = fix(d['title'] or '')
    d['practice'] = fix(d['practice'] or '')
    d['body']     = [fix(p) for p in d['body']]
    d.pop('weekNote', None)          # the week epigraphs repeat the day text
    if d['teaser']:
        d['teaserLead'], d['teaser'] = split_lead(fix(d['teaser']))
    else:
        d['teaserLead'] = ''

out = {
    'title': 'A Year Inside the Day',
    'subtitle': "A 52-week beginner's curriculum in the Kabbalah of Time",
    'pdf': 'a-year-inside-the-day.pdf',
    'generated': datetime.date.today().isoformat(),
    'days': {str(n): days[n] for n in range(1, 365)},
}
p = '/home/user/kabalahoftime/companion.json'
open(p, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print('wrote', p, os.path.getsize(p), 'bytes')

blob = json.dumps(out, ensure_ascii=False)
for word in ('fortnight', '�', 'ﬁ', 'ﬂ'):
    print(f'  {word!r}:', blob.count(word))
missing = [n for n in range(1, 365) if not days[n]['body'] or not days[n]['practice']]
print('  incomplete days:', missing)
print('  overrides applied:', len(OVERRIDES))
