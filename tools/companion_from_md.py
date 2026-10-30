"""Turn the companion manuscript into the companion.json the app fetches.

The companion is written as one markdown file — 364 entries under week and
movement headings — and the app wants a flat map of day number to entry. This
converts one into the other so the manuscript stays the thing that is edited
and companion.json is never hand-held.

    python3 tools/companion_from_md.py docs/a-year-inside-the-day.md \
        companion.json companion.json

The third argument is the output and the second is the file the week and
movement names are taken from, which is normally the same file: those names
were sized to fit the two-line meta row above the entry, and the manuscript's
own headings are longer ("Week 22 — Keter: The Crown (Days 148-154)"). The
text is replaced; the furniture is kept.

What the manuscript may hold, and what becomes of it:

  ## Day 7 - The Whole Map     the entry, and its title
  **Practice:**                the practice line
  **Today's practice:**        the same
  **Teaser:** Tomorrow - ...   the teaser, and "Tomorrow" as its lead
  **Tomorrow:** ...            the same, written short
  - a line                     a bullet, which the app draws as its own
                               paragraph opening with a bullet
  # Appendix                   everything from here is production notes and
                               is not published

Paragraphs are blank-line separated and may be wrapped over any number of
lines; emphasis is stripped, because applyCompanion escapes what it is given
and markdown would print as asterisks. The app's esc() marks Hebrew for
itself, so Hebrew is passed through untouched.

It refuses to write unless all 364 days are present, each with a title and a
body, and unless every week it finds already exists in the file it takes the
names from. A companion with a hole in it is worse than no companion: the
app hides the section when an entry is missing, so day 212 would simply
vanish for a day and nobody would know why.
"""
import json, pathlib, re, sys

DAY = re.compile(r'^#{1,6}\s*Day\s+(\d+)\s*[-–—]\s*(.+?)\s*$')
HEAD = re.compile(r'^#{1,6}\s')
PRACTICE = re.compile(r"^\*\*(?:Practice|Today's practice)\s*:?\*\*\s*", re.I)
TEASER = re.compile(r'^\*\*(Teaser|Tomorrow|Next week|Next)\s*:?\*\*\s*', re.I)
# "Tomorrow - the gathering" — the lead word, which the app sets in small
# caps beside the line rather than inside it.
LEAD_IN = re.compile(r'^(Tomorrow|Next week|Next)\s*[-–—:]\s*')
BULLET = re.compile(r'^[-*+]\s+')


def strip_md(s):
    """Emphasis out, whitespace tidied. Runs on a joined paragraph.

    It has to run after the lines of a paragraph are joined: the manuscript
    wraps at about a hundred characters and an emphasis span crosses the wrap
    ninety-two times, so a line-at-a-time pass sees half a span and leaves
    the asterisk standing.
    """
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = re.sub(r'\*(.+?)\*', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()


def blocks(lines):
    """Blank-line separated blocks, each a list of its lines."""
    out, cur = [], []
    for l in lines:
        if l.strip():
            cur.append(l)
        elif cur:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def paragraphs(block):
    """One block to one or more paragraphs.

    A block is one paragraph unless it is a list, in which case each item is
    its own paragraph marked with a bullet. The app draws body paragraphs and
    nothing else, so a list has to arrive as paragraphs; .comp-li hangs the
    bullet in the margin.
    """
    if not any(BULLET.match(l.strip()) for l in block):
        return [strip_md(' '.join(block))]
    items, cur = [], []
    for l in block:
        if BULLET.match(l.strip()):
            if cur:
                items.append(cur)
            cur = [BULLET.sub('', l.strip())]
        elif cur:
            cur.append(l.strip())
        else:                              # prose above the first bullet
            items.append([l.strip()])
    if cur:
        items.append(cur)
    return ['• ' + strip_md(' '.join(i)) for i in items]


def parse(md):
    """The manuscript to a map of day number to its text."""
    text = md.split('\n# Appendix')[0]
    lines = text.split('\n')

    # Where each day begins, and where its text stops: at the next heading of
    # any level, which is either the next day or the next week.
    marks = [(i, int(m.group(1)), m.group(2)) for i, l in enumerate(lines)
             for m in [DAY.match(l)] if m]
    days = {}
    for k, (i, n, title) in enumerate(marks):
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if HEAD.match(lines[j]):
                end = j; break
        body, practice, teaser, lead = [], '', '', ''
        for b in blocks(lines[i + 1:end]):
            first = b[0].strip()
            if first == '---' and len(b) == 1:
                continue
            if PRACTICE.match(first):
                b = list(b); b[0] = PRACTICE.sub('', first)
                practice = strip_md(' '.join(b))
            elif TEASER.match(first):
                named = TEASER.match(first).group(1)
                b = list(b); b[0] = TEASER.sub('', first)
                t = strip_md(' '.join(b))
                m = LEAD_IN.match(t)
                if m:
                    lead, t = m.group(1), t[m.end():]
                elif named.lower() != 'teaser':
                    lead = named
                teaser = t
            else:
                body += paragraphs(b)
        days[n] = {'title': strip_md(title), 'body': [p for p in body if p],
                   'practice': practice, 'teaser': teaser,
                   'teaserLead': (lead or 'Tomorrow') if teaser else ''}
    return days


def main(md_path, meta_path, out_path):
    days = parse(pathlib.Path(md_path).read_text(encoding='utf-8'))

    missing = [n for n in range(1, 365) if n not in days]
    if missing:
        sys.exit(f'{len(missing)} days missing from the manuscript: '
                 f'{missing[:12]}{"..." if len(missing) > 12 else ""}')
    thin = [n for n, e in days.items() if not e['title'] or not e['body']]
    if thin:
        sys.exit(f'days with no title or no body: {thin}')

    old = json.loads(pathlib.Path(meta_path).read_text(encoding='utf-8'))
    # Week and movement names, by week. The week a day belongs to is the day
    # number, not anything the manuscript says, so a renamed heading cannot
    # move an entry.
    furniture = {}
    for e in old['days'].values():
        furniture.setdefault(e['week'], {k: e.get(k) for k in
                                         ('weekTitle', 'movement', 'movementTitle')})
    for n in days:
        w = (n - 1) // 7 + 1
        if w not in furniture:
            sys.exit(f'week {w} (day {n}) has no names in {meta_path}')
        days[n] = {'n': n, **days[n], 'week': w, **furniture[w]}

    out = {**{k: v for k, v in old.items() if k != 'days'},
           'days': {str(n): days[n] for n in sorted(days)}}
    pathlib.Path(out_path).write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')

    chars = sum(len(' '.join(e['body'])) for e in days.values())
    print(f'{len(days)} entries, {chars:,} characters of body -> {out_path}')
    print(f'  with a practice : {sum(1 for e in days.values() if e["practice"])}')
    print(f'  with a teaser   : {sum(1 for e in days.values() if e["teaser"])}')
    print(f'  bullets         : '
          f'{sum(1 for e in days.values() for p in e["body"] if p.startswith(chr(8226)))}')
    left = sorted(n for n, e in days.items()
                  if '*' in ' '.join(e['body'] + [e['practice'], e['teaser']]))
    if left:
        print(f'  asterisks left in: {left}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
