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

NUM_SRC = re.compile(r'\b\d[\d:\u2013\u2014.\-/]*\d\b|\b\d\b')


def words(text):
    return re.findall(r"[a-z'\-]+", flatten(text).lower())


def flatten(text):
    """One apostrophe, not three. The posts are twelve years of Blogger and
    use the curly one; a summary typed here uses the straight one, so
    She'ol, Lag Ba'Omer and ha'Olam each read as missing from a post that
    has them."""
    return (text or '').replace('\u2019', "'").replace('\u2018', "'") \
                       .replace('\u2013', '-').replace('\u2014', '-')


def bare(w):
    """A word without its possessive, which is not a different word.

    "David's" and "David" scored as two, so a summary that wrote about
    David's song where the post wrote about David lost a point for it.
    """
    return re.sub(r"'s$", '', w.strip("'"))


# The same name as the blog spells it over twelve years. Short and written
# out: each pair is one name, not two, and nothing here is folded together
# that a reader would call different people or different places.
ALT = {
    'pesach': 'pessach', 'chanah': 'channah', 'samuel': 'shmuel',
    'frankfurt': 'frankfort', 'haklali': 'klali', 'solomon': 'shlomoh',
    'deborah': 'devorah', 'hannah': 'channah',
    # The app writes G-d everywhere. The psalm texts the blog quotes are
    # Chabad's translation, which writes God. Spelling the Name is a house
    # convention, not a claim about anything.
    'g-d': 'god', 'shema': 'shemah', 'shabbat': 'shabat',
}

# Twelve years of Blogger has eaten a lot of spaces: "Midrashteaches",
# "Channahis", "commandedto". A name of five letters or more is counted as
# present when a word of the post begins with it, which finds the name
# inside the collision. Five, so that short words cannot swallow longer
# ones they merely start.
PREFIX_MIN = 5


def content(text):
    """Every word of the post, and the parts of its hyphenated ones.

    "Ramathaim-Zophim" has to answer for "Zophim" and "Yesod ha'Olam" for
    "Olam", or a summary that names the second half of a name is charged
    with inventing it.
    """
    out = []
    for w in words(text):
        b = bare(w)
        for part in [b] + re.split(r"['\-]", b):
            if len(part) > 2 and part not in STOP:
                out.append(part)
                if part in ALT:
                    out.append(ALT[part])
                out += [k for k, v in ALT.items() if v == part]
    return out


def claims(text):
    """The words in a summary that could carry a fact in from elsewhere.

    Proper nouns and numbers. This is the pass that matters, and it took a
    second look to see why: a summary written in one's own voice scores 20%
    or 30% on ordinary vocabulary purely for its connectives — alternating,
    beside, opens, holds — none of which is a claim about anything. Measuring
    those buries the one thing worth finding.

    A name or a citation is different. The first companion's worst line was
    "Isaiah 60:22", a reference the source did not carry, and that is exactly
    the shape of thing this finds: a proper noun or a number that the post
    being summarised does not have.
    """
    body = re.sub(r'^\W+', '', flatten(text))
    out = set()
    # Capitalised words, except where a sentence or a quotation starts.
    for m in re.finditer(r'(?<![.!?“"]\s)(?<!^)\b([A-Z][a-zA-Z\'-]{2,})',
                         body, re.M):
        out.add(bare(m.group(1).lower()))
    return {w for w in out if w not in STOP}


def numbers(text):
    """Numbers and references, loosely: 33, 29:11, 32:33, 1950, 2019-05-12."""
    return [m.group(0) for m in NUM_SRC.finditer(flatten(text))]


def summary_text(entry):
    """Only the written body.

    The title is the post's own title and the teaser is generated — "Book 3
    - Song of the Sea, week 1" — so checking them charged a summary for
    words nobody wrote in it. "Sea", "Hannah", "General", "Remedy" and a
    stray "3" were all tomorrow's book name arriving through the teaser.
    """
    body = entry.get('body')
    return ' '.join(body if isinstance(body, list) else [str(body or '')])


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

        # Book 7 is the gathering: its post is the other six books' verses
        # for the week, braided into one song, and it names none of them. So
        # its source is the whole week — the seven posts — because that is
        # what it is a summary of. Every other book answers to its own post.
        srcs = [src]
        if entry.get('book') == 7:
            first = (entry['week'] - 1) * 7 + 1
            srcs = [posts[d] for d in range(first, first + 7) if d in posts]
        have = set()
        for one in srcs:
            have |= set(content(one.get('text', '')))
            have |= set(content(one.get('title', '')))
        mine = claims(text)
        joined = [h for h in have if len(h) > PREFIX_MIN]
        unfound = sorted({w for w in mine if w not in have and not (
            len(w) >= PREFIX_MIN and any(h.startswith(w) for h in joined))})
        pct = (len(unfound) / len(mine) * 100) if mine else 0.0

        srcnums = set()
        for one in srcs:
            srcnums |= set(numbers(one.get('text', '')))
            srcnums |= set(numbers(one.get('title', '')))
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
        print(f'names not in their post: {pcts[0]:.1f}% best, '
              f'{pcts[len(pcts)//2]:.1f}% median, {pcts[-1]:.1f}% worst\n')

    print('=' * 72)
    print('NAMES IN THE SUMMARY THAT THE POST DOES NOT HAVE')
    print('=' * 72)
    for n, pct, total, unfound, _ in rows[:int(limit or 20)]:
        print(f'day {n:>3}  {pct:5.1f}%  of {total:>3} names: '
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
