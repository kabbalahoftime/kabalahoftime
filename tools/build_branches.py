"""Build a Branches volume — ten chapters on the tree — for the app.

    python3 -I build_branches.py <the book>.pdf branches-<volume>.json

Read from the page's own layout rather than from its text, because the text
alone does not say where a paragraph ends and the guesses go wrong. The PDF
sets the book in one column and tells us everything we need:

  36.0pt   a chapter title            18.0pt   a section heading
  16.0pt   the chapter's subtitle     14.7pt   body
  12.7pt   the station, letterspaced  12.0pt   a page number

Ten chapters, and every chapter carries the same number of 18pt sections —
five in the sciences volume, four in the arts, which has no closing "at
work". That regularity is what is asserted below: a count fixed at fifty was
right for one volume and wrong for the other, where the shape holding even
is right for both and still catches a section dropped from one chapter.
Paragraphs come from
vertical gap: 23-24 points between two lines of one paragraph, 36-37 between
two paragraphs, with nothing in between, so 30 separates them cleanly.

Two things the text needs on the way out. Ligatures arrive as single
characters, so "fixed" would reach a reader as "ﬁxed". And the station lines
are letterspaced, so "C H O C H M A H" has to be closed up before it can be
matched against a name.
"""
import json, pathlib, re, sys
from pypdf import PdfReader

LIG = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl'}
TITLE, HEAD, SUB, BODY, STATION = 36.0, 18.0, 16.0, 14.7, 12.7
BOOK, KICKER = 53.3, 12.7          # the title page's own two sizes
PARA_GAP = 30.0

STATIONS = ["Keter / Da'at", 'Chochmah', 'Binah', 'Chesed', 'Gevurah',
            'Tiferet', 'Netzach', 'Hod', 'Yesod', 'Malchut']
# the Sefirah each chapter stands on, for the card. Mathematics is given as
# Keter / Da'at in the book: the crown that is also knowledge.
SEFIRAH = ['Keter', 'Chochmah', 'Binah', 'Chesed', 'Gevurah',
           'Tiferet', 'Netzach', 'Hod', 'Yesod', 'Malchut']
HEBREW = ['כֶּתֶר', 'חָכְמָה', 'בִּינָה', 'חֶסֶד', 'גְּבוּרָה',
          'תִּפְאֶרֶת', 'נֶצַח', 'הוֹד', 'יְסוֹד', 'מַלְכוּת']


def lines_of(pdf):
    out = []
    for page in PdfReader(str(pdf)).pages:
        runs = []
        page.extract_text(visitor_text=lambda t, cm, tm, fd, fs: runs.append(
            {'y': round(tm[5], 1), 'size': round(fs or 0, 1), 't': t})
            if t and t.strip() else None)
        cur, last = [], None
        for r in runs:
            if last is not None and abs(r['y'] - last) >= 1.5 and cur:
                out.append(cur); cur = []
            cur.append(r); last = r['y']
        if cur:
            out.append(cur)
    merged = []
    for ln in out:
        txt = ''.join(r['t'] for r in ln)
        for a, b in LIG.items():
            txt = txt.replace(a, b)
        txt = ' '.join(txt.split())
        if txt:
            merged.append({'y': ln[0]['y'], 'size': max(r['size'] for r in ln),
                           'text': txt})
    return merged


def near(a, b):
    return abs(a - b) < 0.3


def main(pdf_path, out_path):
    lines = lines_of(pdf_path)

    # The title page says which volume this is. The kicker is letterspaced —
    # "T H E  S E F I R O T  A N D  T H E  A R T S" — so it is closed up
    # before it is read, and the volume is taken from it rather than from the
    # title, which is "Branches" in one book and "Branches / Roots" in the
    # other and will not tell them apart.
    book = next((l['text'] for l in lines if near(l['size'], BOOK)), '')
    kick = next((re.sub(r'\s+', '', l['text']).upper()
                 for l in lines if near(l['size'], KICKER)), '')
    m = re.match(r'THESEFIROTANDTHE(.+)$', kick)
    assert m, f'no "THE SEFIROT AND THE ..." kicker on the title page: {kick!r}'
    volume = 'The ' + m.group(1).capitalize()

    # chapter openings: a station line followed by a 36pt title
    opens = []
    for i, l in enumerate(lines):
        if not near(l['size'], STATION):
            continue
        flat = re.sub(r'\s+', '', l['text']).upper()
        hit = next((s for s in STATIONS if re.sub(r'\s+', '', s).upper() == flat), None)
        if hit and i + 2 < len(lines) and near(lines[i + 1]['size'], TITLE):
            opens.append({'i': i, 'station': hit, 'name': lines[i + 1]['text'],
                          'subtitle': lines[i + 2]['text']
                          if near(lines[i + 2]['size'], SUB) else ''})
    assert len(opens) == 10, f'expected 10 chapters, found {len(opens)}'

    def paras(seq):
        out, buf, last = [], [], None
        for l in seq:
            if last is not None and (l['y'] - last) > PARA_GAP and buf:
                out.append(' '.join(buf)); buf = []
            buf.append(l['text']); last = l['y']
        if buf:
            out.append(' '.join(buf))
        # A word hyphenated across a line break arrives as "four- color".
        # Only a hyphen sitting tight against the word before it and a space
        # before the word after is joined, so a dash with air on both sides
        # is left alone.
        return [re.sub(r'(\w)- (\w)', r'\1-\2', ' '.join(p.split()))
                for p in out if p.strip()]

    chapters = []
    for k, o in enumerate(opens):
        end = opens[k + 1]['i'] if k + 1 < len(opens) else len(lines)
        body = [l for l in lines[o['i'] + 3: end]
                if near(l['size'], BODY) or near(l['size'], HEAD)]
        cuts = [j for j, l in enumerate(body) if near(l['size'], HEAD)]
        assert len(cuts) >= 3, f"{o['name']}: only {len(cuts)} sections"
        secs = []
        for s, j in enumerate(cuts):
            nxt = cuts[s + 1] if s + 1 < len(cuts) else len(body)
            secs.append({'head': body[j]['text'], 'paras': paras(body[j + 1: nxt])})
        chapters.append({
            'n': k + 1, 'sefirah': SEFIRAH[k], 'hebrew': HEBREW[k],
            'station': o['station'], 'name': o['name'], 'subtitle': o['subtitle'],
            'opening': paras(body[:cuts[0]]), 'sections': secs,
        })

    # Every chapter the same shape. One chapter short of the rest is a
    # section lost in extraction, and it is the fault worth catching.
    counts = {len(c['sections']) for c in chapters}
    assert len(counts) == 1, (
        'chapters disagree on how many sections they have: '
        + ', '.join(f"{c['name']} {len(c['sections'])}" for c in chapters))

    total = 0
    for c in chapters:
        w = sum(len(p.split()) for p in c['opening']) + \
            sum(len(p.split()) for s in c['sections'] for p in s['paras'])
        total += w
        print(f"{c['n']:>2}. {c['station']:<13} {c['name']:<14} {w:>5}w  "
              f"“{c['subtitle']}”")
        print(f"      opening {len(c['opening'])}¶ | " +
              ' | '.join(f"{s['head']} {len(s['paras'])}¶" for s in c['sections']))

    doc = {'title': book, 'volume': volume, 'chapters': chapters}
    pathlib.Path(out_path).write_text(
        json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"\n{book} \u00b7 {volume}: 10 chapters \u00d7 "
          f"{counts.pop()} sections, {total:,} words -> {out_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
