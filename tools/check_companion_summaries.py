"""Check each daily summary against the post it summarises.

    python3 -I tools/check_companion_summaries.py out/posts.json companion-days.json

The companion's 364 entries are summaries of 364 posts, one to a day. A
summary can be checked against its source; that is the only reason writing
them is safe. This is the check, and it is the same one that cleared the 828
Likutei Moharan summaries: two passes, neither of which understands anything.

  1. vocabulary — every content word of the summary, and whether it occurs in
     the post. A summary of a post should be made almost entirely of the
     post's own words. A high unfound score means sentences arrived from
     somewhere else, which is exactly how the first companion invented a
     motto for this app.

  2. numbers and references — every number, chapter-and-verse, year and date
     in the summary, and whether the post has it. This is the pass that
     would have caught "Isaiah 60:22" standing where the app says 60:2.

What it cannot do: tell a true summary from a plausible one. A sentence built
of the post's own words can still say the opposite of what the post said. A
low score means nothing was imported; it does not mean nothing was twisted.
That part needs a reader, and the reader is the author.
"""
import json, pathlib, re, sys

# Words that carry no claim. Kept short on purpose: the more that is excused
# here, the less the vocabulary pass is measuring.
STOP = set("""a an the and or but if then than that this these those of in on at to
from by for with without as is are was were be been being it its his her their our
your my we you they he she i there here not no nor so such which who whom whose what
when where why how all any both each few more most other some only own same too very
can will just also into over under again further once about against between through
during before after above below up down out off again more again does do did doing
have has had having would should could may might must shall them him us me
one two three four five six seven eight nine ten first second third week day""".split())

NUM = re.compile(r'\b\d[\d:\u2013\u2014.\-/]*\d\b|\b\d\b')


def words(text):
    return re.findall(r"[a-z']+", (text or '').lower())


def content(text):
    return [w.strip("'") for w in words(text)
            if len(w.strip("'")) > 2 and w.strip("'") not in STOP]


def numbers(text):
    """Numbers and references, loosely: 33, 29:11, 32:33, 1950, 2019-05-12."""
    return [m.group(0) for m in NUM.finditer(text or '')]


def summary_text(entry):
    body = entry.get('body')
    parts = body if isinstance(body, list) else [str(body or '')]
    for k in ('title', 'teaser'):
        if entry.get(k):
            parts.append(str(entry[k]))
    return ' '.join(parts)


def main(posts_path, companion_path, limit=None):
    posts = {r['day']: r for r in
             json.loads(pathlib.Path(posts_path).read_text(encoding='utf-8'))}
    days = json.loads(pathlib.Path(companion_path).read_text(encoding='utf-8'))['days']

    rows, flagged, skipped = [], 0, 0
    for k in sorted(days, key=int):
        n = int(k)
        src = posts.get(n)
        entry = days[k]
        # Only the written summaries are checked here. The rest are
        # transcriptions of the app's own weekly table, which are true by
        # construction and share almost no wording with the post — running
        # them through a vocabulary pass measures nothing and buries the
        # entries that need reading.
        if entry.get('kind') and entry['kind'] != 'summary':
            skipped += 1
            continue
        text = summary_text(entry)
        if not src or not src.get('text'):
            print(f'day {n:>3}  NO SOURCE  (nothing to check against)')
            flagged += 1
            continue

        have = set(content(src['text'])) | set(content(src.get('title', '')))
        mine = content(text)
        unfound = sorted({w for w in mine if w not in have})
        pct = (len(unfound) / len(set(mine)) * 100) if mine else 0.0

        srcnums = set(numbers(src['text']))
        mynums = [x for x in numbers(text) if x not in srcnums]
        # A week number and a day number are the companion's own, not the
        # post's, so they are not expected to be in it.
        own = {str(n), str(entry.get('week', '')), str(entry.get('book', '')), '364', '52'}
        mynums = [x for x in mynums if x not in own]

        rows.append((n, pct, len(set(mine)), unfound, mynums))

    rows.sort(key=lambda r: -r[1])
    print(f'{len(rows)} summaries checked against their posts'
          f'  ({skipped} table entries skipped)\n')
    if rows:
        pcts = sorted(r[1] for r in rows)
        print(f'unfound vocabulary: {pcts[0]:.1f}% best, '
              f'{pcts[len(pcts)//2]:.1f}% median, {pcts[-1]:.1f}% worst\n')

    print('=' * 72)
    print('WORST BY VOCABULARY  (words not in the post)')
    print('=' * 72)
    for n, pct, total, unfound, _ in rows[:int(limit or 20)]:
        print(f'day {n:>3}  {pct:5.1f}%  of {total:>3} words: '
              f'{", ".join(unfound[:14])}{" ..." if len(unfound) > 14 else ""}')

    print('\n' + '=' * 72)
    print('NUMBERS AND REFERENCES NOT IN THE POST')
    print('=' * 72)
    bad = [(n, nums) for n, _, _, _, nums in rows if nums]
    for n, nums in bad:
        print(f'day {n:>3}  {", ".join(nums[:12])}')
        flagged += 1
    if not bad:
        print('none')

    print(f'\n{flagged} flagged')
    return 1 if flagged else 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:4]))
