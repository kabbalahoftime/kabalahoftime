"""Build the companion's 364 daily entries from the app's own weekly table.

The companion is one KoT Book for one week, each day, filed the way Binah
files them: day 1 is Book 1's entry for week 1, day 2 is Book 2's for week 1,
day 8 is Book 1's for week 2, day 225 is Book 1's for week 33. Seven books
times fifty-two weeks is three hundred and sixty-four, which is the year.

    node tools/dump_week_data.mjs http://127.0.0.1:8731/index.html week.json
    python3 -I tools/build_companion_days.py week.json index.html companion.json

Every entry is already in index.html before this runs — the weekly table holds
all seven books' readings for all fifty-two weeks. So nothing here is written
per entry. There are seven templates, one to each book, reviewed once, and
364 fillings of them. That is the only way a generated entry cannot invent
something: not because a source is named beside it, but because no sentence
in it was composed.

The companion that came down in October failed the other way. It was written
entry by entry, and day 154 cited Isaiah 60:22 for a phrase that does not
exist. The citation read exactly as sound as a true one.

Each entry also carries `source`: the week's post for that book, from the
app's own BOOKn_WEEK_URLS and b7_url — 364 posts for 364 days, one each. The
reader who wants the whole thing rather than the digest has somewhere to go.

Fields the table leaves empty are left out rather than filled. Four creatures
have no Perek Shirah verse in the app (Wild Goose, Fly, Sheep & Goat, Pig &
Rabbit) and weeks 50-52 have no Sefirah pairing, standing outside the 7x7 as
the Mochin. In both cases the sentence is dropped, not invented.
"""
import json, pathlib, re, sys

# ── the seven templates ──────────────────────────────────────────────────────
# Each is: what the book is (one fixed sentence), then its fields as lines.
# `lines` is (label, key) — a missing or empty value drops the line.
BOOKS = [
    dict(
        n=1, opens='Book 1 reads the week the way nature reads it: a theme, a '
                   'creature that sings for it in Perek Shirah, and a teaching '
                   'from Pirkei Avot.',
        title='theme',
        lines=[('The week’s theme', 'theme'),
               ('From Pirkei Avot', 'avot')],
    ),
    dict(
        n=2, opens='Book 2 counts the forty-eight qualities by which Torah is '
                   'acquired, one a week, each with a prophet, a city of the '
                   'Levites, and the week’s verse of Haazinu.',
        title='quality',
        lines=[('This week’s quality', 'quality'),
               ('Its prophet', 'prophet'),
               ('Its Levitical city', 'city'),
               ('From Haazinu', 'haazinu'),
               ('From the haftorah', 'haftorah')],
    ),
    dict(
        n=3, opens='Book 3 follows the line that runs to David — a name a '
                   'week from Ruth’s genealogy, with the haftara, a portion '
                   'of Tractate Sotah, and a stage of the journeys through the '
                   'desert.',
        title='ruth', title_lead='The line to David: ',
        lines=[('This week’s name', 'ruth'),
               ('Its haftara', 'haftara'),
               ('From Sotah', 'sotah'),
               ('The journey', 'journeys')],
    ),
    dict(
        n=4, opens='Book 4 reads Solomon’s writings beside Hannah’s '
                   'song, with the sixth chapter of Pirkei Avot and the '
                   'week’s yahrzeit.',
        title='proverbs',
        lines=[('From Solomon', 'proverbs'),
               ('From Hannah’s song', 'hannah'),
               ('From the sixth chapter of Pirkei Avot', 'avot6'),
               ('The yahrzeit', 'yahrzeit')],
    ),
    dict(
        n=5, opens='Book 5 walks Song of Songs through the year, with one of '
                   'the seventy souls who went down to Egypt, a chapter of '
                   'Jeremiah, and a portion of Tractate Shevuot.',
        title='shir',
        lines=[('This week’s reading', 'shir'),
               ('Its soul', 'souls'),
               ('From Jeremiah', 'jeremiah'),
               ('From Shevuot', 'talmud')],
    ),
    dict(
        n=6, opens='Book 6 is the general remedy: the week’s psalms with '
                   'Perek Shirah, the ten psalms of the Tikkun HaKlali, and '
                   'Psalm 89 read a little at a time.',
        title='psalms',
        lines=[('This week’s psalms', 'psalms'),
               ('From the Tikkun HaKlali', 'tikkun'),
               ('From Psalm 89', 'psalm89')],
    ),
    dict(
        n=7, opens='Book 7 gathers the week: every verse the six books sang, '
                   'rearranged and combined into a single song.',
        title='theme',
        lines=[('This week’s gathering', 'theme'),
               ('From Mesilat Yesharim', 'mesilas')],
    ),
]


def perek_shirah(app_text):
    """The Perek Shirah verses, keyed by creature, as index.html holds them."""
    out = {}
    for m in re.finditer(r"'([^']+)': \['(Ch [^']+)', '([^']+)', "
                         r"'((?:[^'\\]|\\.)*)'\]", app_text):
        out[m.group(1)] = (m.group(2), m.group(3), unesc(m.group(4)))
    return out


def unesc(x):
    return x.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


def song_for(animal, songs):
    """The creature's verse, matched on the name and then on the name alone.

    The weekly table writes some creatures with a note after them — "Rooster
    (first bird)" — and Perek Shirah is keyed by the bare name.
    """
    a = (animal or '').strip()
    if a in songs:
        return songs[a]
    base = re.sub(r'\s*\(.*?\)\s*', '', a).strip()
    return songs.get(base)


def sentence(label, value):
    """"Label: value." — with one full stop, whatever the value ends in.

    The table's values are written for a card, so some end in a full stop,
    some in nothing, and the verses of Haazinu end in an exclamation mark.
    Appending a stop to all of them gave "of my mouth!." twice over.

    Nothing is put in quotation marks here. Several of these values are
    verses and could carry them honestly, but the line that cost this
    companion its first life was an invented phrase wearing quotation marks,
    and a colon says where the words come from without dressing them up.
    """
    v = re.sub(r'\s+', ' ', str(value or '')).strip()
    if not v:
        return None
    return f'{label}: {v}' + ('' if v[-1] in '.!?…”' else '.')


def build(data, songs):
    books = data.get('books') or []
    days = {}
    for wk in data['weeks']:
        w = wk['week']
        pair = wk.get('pairing') or None
        face = wk.get('face') or {}
        for bi in range(7):
            n = (w - 1) * 7 + bi + 1
            spec = BOOKS[bi]
            f = wk['fields'][f'b{bi + 1}']
            meta = books[bi] if bi < len(books) else {}
            name = str(meta.get('book') or f'Book {bi + 1}')
            emoji = str(meta.get('emoji') or '')

            body = [spec['opens']]

            # Where the week sits, said once: the pairing, and the month and
            # portion it falls in. Weeks 50-52 have no pairing.
            where = []
            if pair:
                where.append(f'Week {w} of fifty-two is {pair["en"]} '
                             f'— {pair["he"]}')
            else:
                where.append(f'Week {w} of fifty-two stands outside the seven '
                             f'sevens, with the Mochin')
            if wk.get('month'):
                where.append(f'the month is {wk["month"]}')
            if wk.get('parasha'):
                where.append(f'the portion is {wk["parasha"]}')
            body.append('; '.join(where) + '.')

            for label, key in spec['lines']:
                s = sentence(label, f.get(key))
                if s:
                    body.append(s)

            # Book 1 carries the week's creature and its verse, which is what
            # Book 1 is. The other six do not, and are not given one.
            if bi == 0:
                animal = f.get('animal') or face.get('animal')
                if animal:
                    song = song_for(animal, songs)
                    line = f'Its creature is the {animal}.'
                    if song:
                        line += (f' In Perek Shirah ({song[0]}) it says, from '
                                 f'{song[1]}: “{song[2]}”')
                    body.append(line)
                if face.get('trait'):
                    body.append(sentence('The trait to build', face['trait']))

            raw = f.get(spec['title']) or name
            title = re.sub(r'\s+', ' ', str(raw)).strip()
            if spec.get('title_lead'):
                title = spec['title_lead'] + title

            # Tomorrow is the next book of the same week, or Book 1 of the
            # next week, which is what the year does on day 364 as well.
            nxt = (bi + 1) % 7
            nw = w + 1 if nxt == 0 else w
            nname = str((books[nxt] if nxt < len(books) else {}).get('book')
                        or f'Book {nxt + 1}')
            teaser = (f'{nname}, week {nw if nw <= 52 else 1}.'
                      if n < 364 else
                      f'{nname}, week 1 — the year begins again.')

            days[n] = {
                'n': n,
                'title': title,
                'body': [b for b in body if b],
                'teaser': teaser,
                'teaserLead': 'Tomorrow',
                'week': w,
                'weekTitle': pair['en'] if pair else 'the Mochin',
                'movementTitle': f'{emoji} {name}'.strip(),
                'source': wk['postUrls'][bi] or '',
                'sourceLabel': f'Week {w}, {name.split(" · ")[0]} '
                               f'— the whole entry',
            }
    return days


def main(week_path, app_path, out_path):
    data = json.loads(pathlib.Path(week_path).read_text(encoding='utf-8'))
    songs = perek_shirah(pathlib.Path(app_path).read_text(encoding='utf-8'))
    days = build(data, songs)

    missing = [n for n in range(1, 365) if n not in days]
    if missing:
        sys.exit(f'{len(missing)} days missing: {missing[:12]}')
    thin = sorted(n for n, e in days.items() if len(e['body']) < 3)
    if thin:
        sys.exit(f'days with fewer than three paragraphs: {thin}')

    out = {
        'title': 'A Year Inside the Day',
        'subtitle': 'One KoT Book for one week, each day — as Binah files them',
        'generated': '2026-10-30',
        'days': {str(n): days[n] for n in sorted(days)},
    }
    pathlib.Path(out_path).write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')

    chars = sum(len(' '.join(e['body'])) for e in days.values())
    print(f'{len(days)} entries, {chars:,} characters of body -> {out_path}')
    print(f'  with a source post : '
          f'{sum(1 for e in days.values() if e["source"])}')
    print(f'  with a Perek Shirah verse : '
          f'{sum(1 for e in days.values() for b in e["body"] if "Perek Shirah (" in b)}')
    sizes = sorted(len(e['body']) for e in days.values())
    print(f'  paragraphs per entry : {sizes[0]} to {sizes[-1]}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
