"""Check the app's weekly table against the writing it is a table of.

    python3 -I tools/check_week_table.py docs/week-data.json docs/companion-posts.json

Every week of the year has seven readings, one to each KoT Book, and every one
of those has a post of its own — 364 posts for 364 days. The post names what
the table gives: week 33's Book 2 post is titled "Chabakuk and Torah that
Comes from Suffering", and the table's job is to say Chabakuk at week 33.

This exists because on 30 October 2026 it did not. Four separate faults had
got into one column and nobody could see any of them from one week alone:

  * Yoel was in the prophet list twice, at weeks 24 and 32, spelled Yoel and
    then Joel. Every prophet from week 24 to week 50 fell a week late.
  * Emunat Chachamim was in the quality list twice, at weeks 25 and 26, as
    "Trusting in the Sages" and "Faith in the Sages", with the same effect
    from week 26 — which then caught up at week 42, where two of the
    forty-eight were sharing one cell.
  * Chuldah was missing from the prophets altogether.
  * The city column had Jerusalem missing at week 25, the seven nations in
    weeks 40-42, daf of Nazir in weeks 43-45, and nothing at all in weeks
    46-52. Thirty-one of fifty-two were wrong.

None of it was going to be caught by reading one entry at a time. "The card
says Nahum and the post says Chabakuk" is a symptom; a duplicate nine weeks
earlier is the cause, and the cause is only visible with all fifty-two laid
side by side. A reader would have patched the symptom and left the rest.

So this lays them side by side. For each field it asks: does the week's own
post name this value, or does a neighbour's post name it instead? A value
that only its neighbour's post knows is a column a week out of step. It also
reports a column's duplicates and its empty cells, which is what the other
three faults looked like.

What it cannot do: know whether a value is right when no post mentions it.
Many posts name the prophet and not the city. A silent field is reported as
silent, not as sound.
"""
import json, pathlib, re, sys

# The same name, spelled as the table spells it and as the posts do. Written
# out rather than guessed at, because a clever matcher that folds Yoel into
# Joel on its own would have folded away the duplicate that caused all this.
ALIASES = [
    ('yoel', 'joel'), ('hoshea', 'hosea'), ('michah', 'micah'),
    ('michaiah', 'micah'), ('amotz', 'amoz'), ('ovadiah', 'obadiah'),
    ('yehu', 'jehu'), ('yachaziel', 'jahaziel'), ('chuldah', 'huldah'),
    ('chabakuk', 'habakkuk'), ('ahiah', 'achia'), ('shmuel', 'samuel'),
    ('yehoshua', 'joshua'), ('moshe', 'moses'), ('aharon', 'aaron'),
    ('natan', 'nathan'), ('shlomo', 'solomon'), ('yitzchak', 'isaac'),
    ('yaakov', 'jacob'), ('avraham', 'abraham'), ('chanah', 'hannah'),
    ('devorah', 'deborah'), ('eliyahu', 'elijah'), ('yirmiyahu', 'jeremiah'),
    ('yechezkel', 'ezekiel'), ('yeshayahu', 'isaiah'), ('yonah', 'jonah'),
]

# Words that identify nothing. A field matched on one of these matches
# everything, which reads as agreement and is the opposite of a check.
STOP = set("""the and that with from one ones week book quality city refuge also
future tribe half rests will have its own jordan river side other now short for
verb means temple eye fountain gilead galillee portion reading torah his her our
not but who whom whose this these those what when where there here all any both
each few more most some only same too very can may might must shall them him her
his she they you your was were been being had has have does did doing into over
under again further once about against between through during before after above
below down out off great greater than king kingship priesthood acquired ways
chapter prov psalm psalms song songs verse verses said says saying name names""".split())


def fold(tok):
    t = tok.lower().strip("'-")
    for a, b in ALIASES:
        if t == a:
            return b
    return t


def tokens(value):
    """A field's identifying words — proper nouns and the unusual ones."""
    s = str(value or '')
    s = re.sub(r'^Week\s*\d+\s*\((?:Book\s*\d+|From the Book)\)\s*:\s*', '', s,
               flags=re.I)
    out = {fold(t) for t in re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", s)}
    return {t for t in out if len(t) > 2 and t not in STOP}


def numbers(value):
    return set(re.findall(r'\d{1,3}', str(value or '')))


def post_words(post):
    blob = (post.get('title', '') + ' ' + post.get('text', ''))
    return {fold(t) for t in re.findall(r"[A-Za-z][A-Za-z'\-]{2,}", blob)}


def post_numbers(post):
    return set(re.findall(r'\d{1,3}', post.get('text', '') or ''))


# book -> the fields worth asking about, and how to read them.
#   'words'   — matched on identifying words
#   'numbers' — matched on the numbers in it (the psalms)
#
# Only fields a post reliably names are here. Book 4's Solomon column holds a
# verse rather than a reference — "Prov 8 — Does not Wisdom call out" — and
# twenty of the fifty-two posts never cite the chapter, so the words left to
# match on are "wisdom", "call" and "out", which any neighbour's post also
# has. A check that reports on a field it cannot read is worse than no check:
# the noise teaches the reader to skip it.
FIELDS = {
    1: [('animal', 'words'), ('theme', 'words')],
    2: [('prophet', 'words'), ('quality', 'words'), ('city', 'words')],
    3: [('ruth', 'words'), ('journeys', 'words')],
    4: [('yahrzeit', 'words')],
    5: [('souls', 'words'), ('shir', 'words')],
    6: [('psalms', 'numbers')],
    7: [('theme', 'words')],
}

# Repeats that are not mistakes, with the reason. Anything else repeated in a
# column is reported, because two of the four faults above were duplicates.
ALLOWED_REPEATS = {
    (2, 'city'): {
        'gath-rimmon': 'Joshua 21 names Gath-Rimmon twice',
        'future city of refuge': 'two weeks are given to the cities still to come',
        'jerusalem': 'half of it lies in Benjamin and half in Judah, a week each',
    },
}


def norm(value):
    """A value reduced for comparing with another value.

    Digits are kept. Dropping them made "Kohelet: Chapter 2" and "Kohelet:
    Chapter 9" the same string, so a column that counts through a book
    chapter by chapter reported itself as twelve duplicates.
    """
    return re.sub(r'\s+', ' ', re.sub(r'\(.*?\)|[^A-Za-z0-9 \-]', ' ',
                                      str(value or ''))).strip().lower()


def reviews_last_week(post):
    """Is this post a review of the week before it?

    Book 6 spends the last third of the year reviewing: "Week 43 (Book 6):
    Reviewing the Week of Rosh Chodesh Av". Such a post quotes the previous
    week's psalms, so finding this week's value in last week's post is what
    it should do, not a column out of step.
    """
    return bool(re.search(r'\breview(ing|s)?\b', post.get('title', ''), re.I))


JOURNEY = re.compile(r'They journeyed from (.+?) and camped (?:in|at) (.+?)\.?$',
                     re.I)


def check_journey_chain(weeks):
    """Book 3's journeys are a chain, so the chain can be checked.

    Each week sets out from where the week before camped — they are the
    journeys of Numbers 33 in order. A break means a journey has been dropped
    or doubled, which is the same fault that took Jerusalem out of the cities
    and Chuldah out of the prophets, and it is invisible from either week on
    its own. The break this found: week 39 camps in Dibon-gad and week 40
    sets out from Almon-diblathaimah.
    """
    link = {}
    for w in range(1, 53):
        m = JOURNEY.match(str(weeks[w]['fields']['b3'].get('journeys') or ''))
        if m:
            link[w] = (m.group(1).strip(), m.group(2).strip())

    def bare(s):
        return set(re.sub(r'\b(the|of|in|at)\b|[^a-z ]', ' ', s.lower()).split())

    breaks = []
    for w in range(2, 53):
        a, b = link.get(w - 1), link.get(w)
        if a and b and not (bare(a[1]) & bare(b[0])):
            breaks.append((w, a[1], b[0]))

    print('=' * 72)
    print('BOOK 3 — the journeys as a chain')
    print('=' * 72)
    print(f'  {len(link)} of 52 weeks read as "they journeyed from X and '
          f'camped in Y"')
    if breaks:
        for w, camped, from_ in breaks:
            print(f'  [FAIL] week {w - 1} camped in {camped!r} but week {w} '
                  f'sets out from {from_!r}')
    else:
        print('  [ ok ] every week sets out from where the week before camped')
    print()
    return len(breaks)


def main(week_path, posts_path):
    weeks = {w['week']: w for w in
             json.loads(pathlib.Path(week_path).read_text(encoding='utf-8'))['weeks']}
    rows = json.loads(pathlib.Path(posts_path).read_text(encoding='utf-8'))
    posts = {r['day']: r for r in rows}

    words = {d: post_words(p) for d, p in posts.items()}
    nums = {d: post_numbers(p) for d, p in posts.items()}
    bad = 0

    for book in sorted(FIELDS):
        print('=' * 72)
        print(f'BOOK {book}')
        print('=' * 72)
        for field, how in FIELDS[book]:
            vals = {w: weeks[w]['fields'][f'b{book}'].get(field)
                    for w in range(1, 53)}

            empty = [w for w, v in vals.items() if not str(v or '').strip()]

            seen = {}
            for w, v in vals.items():
                seen.setdefault(norm(v), []).append(w)
            allowed = ALLOWED_REPEATS.get((book, field), {})
            repeats = []
            for k, ws in seen.items():
                if len(ws) < 2 or not k:
                    continue
                why = next((r for key, r in allowed.items() if key in k), None)
                if why:
                    continue
                repeats.append((k, ws))

            agree = late = early = silent = 0
            drift = []
            for w in range(1, 53):
                day = (w - 1) * 7 + book
                if day not in posts:
                    continue
                want = tokens(vals[w]) if how == 'words' else numbers(vals[w])
                if not want:
                    silent += 1
                    continue
                have = (lambda d: words.get(d, set()) if how == 'words'
                        else nums.get(d, set()))
                here = bool(want & have(day))
                nxt = bool(want & have(day + 7)) if w < 52 else False
                prv = bool(want & have(day - 7)) if w > 1 else False
                # A review post quotes the week it reviews, so a value turning
                # up in a neighbour that is a review says nothing about this
                # column. Book 6 spends the last third of the year reviewing.
                if here:
                    agree += 1
                elif nxt and not (w < 52 and reviews_last_week(posts[day + 7])):
                    late += 1
                    drift.append((w, 'a week late', vals[w], posts[day]['title']))
                elif prv and not reviews_last_week(posts[day]):
                    early += 1
                    drift.append((w, 'a week early', vals[w], posts[day]['title']))
                else:
                    silent += 1

            # Drift and empty cells are faults. A repeat is reported but does
            # not fail: the two duplicates that cost a day of work were found
            # because the drift they caused was flagged, and a column that
            # legitimately names the same thing twice — Gath-Rimmon, two
            # Hezrons in the seventy souls — would otherwise cry wolf forever.
            flag = bool(empty or late or early)
            if flag:
                bad += 1
            mark = 'FAIL' if flag else ' ok '
            print(f'  [{mark}] {field:<10} {agree:>2} named by their own post, '
                  f'{late} a week late, {early} a week early, '
                  f'{silent} not named anywhere near')
            for w, how_bad, val, title in drift:
                print(f'          week {w:>2} is {how_bad}: {str(val)[:38]!r}')
                print(f'                  its post: {title[:56]}')
            for k, ws in repeats:
                print(f'          note: repeated at weeks {ws}: {k[:44]!r}')
            if empty:
                print(f'          empty at weeks {empty}')
        print()

    bad += check_journey_chain(weeks)

    print(f'{bad} fault(s) flagged')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:3]))
