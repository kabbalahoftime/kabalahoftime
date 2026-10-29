"""Build the companion's 52 week entries by transcription, not composition.

Every field here is lifted from index.html. Nothing is written per entry: the
connective wording is one template, reviewed once, and the 52 entries are 52
fillings of it. That is the only way a generated entry cannot invent — not
because a reference is attached to it, but because there is no sentence in it
that anybody composed.

The companion failed the other way. Day 154 cited Isaiah 60:22 for a phrase
that does not exist. The citation read exactly as sound as a true one, which
is why "referenced" is not the same as "verified".

    python3 -I tools/build_week_entries.py index.html out.json

Each entry carries `from_app`: the field it came from, so
tools/check_companion.py can re-derive it and fail the build if the app and
the entry ever drift apart.

Weeks 50-52 carry no Sefirah pairing: they are the three Mochin weeks, which
stand outside the 7x7. The template leaves that sentence out rather than
inventing one.
"""
import json, pathlib, re, sys


def read_app(path):
    s = pathlib.Path(path).read_text(encoding='utf-8')

    m = re.search(r'\bSEF\s*=\s*\[(.*?)\]', s, re.S)
    sef = [(he, en) for en, he in
           re.findall(r"\{en:'([^']+)',he:'([^']+)'", m.group(1))]
    if len(sef) != 7:
        sys.exit(f'expected 7 Sefirot in SEF, found {len(sef)}')

    w = re.search(r'\bW\s*=\s*\[\s*\{', s)
    weeks = re.findall(r"\{a:'((?:[^'\\]|\\.)*)',r:'((?:[^'\\]|\\.)*)',"
                       r"t:'((?:[^'\\]|\\.)*)'\}", s[w.start():])

    shirah = {}
    for m in re.finditer(r"'([^']+)': \['(Ch [^']+)', '([^']+)', "
                         r"'((?:[^'\\]|\\.)*)'\]", s):
        shirah[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    return sef[:7], weeks, shirah


def unesc(x):
    return x.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


def pairing(n, sef):
    """The app's own combo(): week n is SEF[(n-1)%7] of SEF[(n-1)//7]."""
    if n > 49:
        return None
    k, p = (n - 1) // 7, (n - 1) % 7
    return {'he': f'{sef[p][0]} שֶׁבְּ{sef[k][0]}', 'en': f'{sef[p][1]} of {sef[k][1]}'}


def creature_key(animal, shirah):
    a = unesc(animal)
    if a in shirah:
        return a
    base = re.sub(r'\s*\(.*?\)\s*', '', a).strip()
    return base if base in shirah else None


def main(app_path, out_path):
    sef, weeks, shirah = read_app(app_path)
    if len(weeks) != 52:
        sys.exit(f'expected 52 week rows, found {len(weeks)}')

    entries, unmatched = [], []
    for i, (a, r, t) in enumerate(weeks, start=1):
        animal, rabbi, trait = unesc(a), unesc(r), unesc(t)
        key = creature_key(a, shirah)
        if key is None:
            unmatched.append((i, animal))
        song = shirah.get(key)
        pair = pairing(i, sef)

        # the one template, filled — no per-entry prose
        says = [f'Week {i} of fifty-two.']
        if pair:
            says.append(f'Its pairing is {pair["en"]} — {pair["he"]}.')
        says.append(f'Its creature is the {animal}.')
        if song:
            says.append(f'In Perek Shirah ({song[0]}) it says, from {song[1]}: '
                        f'“{unesc(song[2])}”')
        says.append(f'From Pirkei Avot: {rabbi}')
        says.append(f'The week’s trait: {trait}')

        entries.append({
            'week': i,
            'says': ' '.join(says),
            'from_app': {
                'animal': animal,
                'avot': rabbi,
                'trait': trait,
                'pairing': pair,
                'shirah': ({'chapter': song[0], 'ref': song[1],
                            'text': unesc(song[2])} if song else None),
            },
            'composed': False,
        })

    pathlib.Path(out_path).write_text(
        json.dumps({'built_from': app_path, 'template_version': 1,
                    'entries': entries}, ensure_ascii=False, indent=1),
        encoding='utf-8')

    print(f'{len(entries)} week entries written to {out_path}')
    print(f'  with a Perek Shirah song : '
          f'{sum(1 for e in entries if e["from_app"]["shirah"])}')
    print(f'  with a Sefirah pairing   : '
          f'{sum(1 for e in entries if e["from_app"]["pairing"])}  '
          f'(weeks 50-52 are the Mochin, outside the 7x7)')
    if unmatched:
        print(f'  creature not found in Perek Shirah: {len(unmatched)}')
        for n, a in unmatched:
            print(f'    week {n}: {a}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
