"""Check the app's Likutei Moharan summaries against the book they summarise.

The 405 summaries behind Keter's daily reading were AI-generated, but unlike
the daily companion they were generated *from* something: Living Likutei
Moharan, which is in docs/. That difference is the whole point. A summary has
a ground truth and can be checked; an invention has none, which is how the
companion's fabricated motto survived a year.

    python3 -I tools/check_lm_summaries.py index.html docs/living-likutei-moharan.pdf

Two passes:

  1. vocabulary — do the distinctive words in each summary occur anywhere in
     the book? A faithful summary reuses its source's words. An invented one
     brings words the source never uses, which is what "88 Mochin minutes"
     looked like in the companion.

  2. dates — each summary names the day its lesson belongs to. Does the book
     put that lesson on that day?

Equivalences the book and the app write differently are folded in, because a
checker that cries wolf stops being read: Tinyana is volume II, the nth day of
Sukkot is 14+n Tishrei, and Iyar/Iyyar, Tevet/Teveth, Shvat/Shevat are one
month each.

Exits 1 if either pass finds something.

What it cannot do: it rules out invention and misdating. It does not judge
whether a summary represents its lesson's meaning. That needs a reader.
"""
import html, pathlib, re, statistics, subprocess, sys, tempfile

STOP = set("""the a an and or but if then than that this these those of in on at to for with
from by as is are was were be been being it its he she they them his her their we you your our
not no nor so such both each more most other some any all one two three into through during how
what which who whom when where why can will would should could may might must shall about also
only very just like over under again further once here there own same too don now
lesson teaches day teaching rebbe nachman likutei moharan torah learn learns taught""".split())

MONTH = {'iyyar': 'iyar', 'teveth': 'tevet', 'shevat': 'shvat', 'cheshvan': 'cheshvan'}

def words(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s)).lower()
    s = re.sub(r'[‘’“”]', ' ', s)
    return [w for w in re.findall(r'[a-z]{4,}', s) if w not in STOP]

def book_text(path):
    if path.lower().endswith('.pdf'):
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
            subprocess.run(['pdftotext', '-layout', path, tmp.name], check=True)
            raw = pathlib.Path(tmp.name).read_text(encoding='utf-8')
    else:
        raw = pathlib.Path(path).read_text(encoding='utf-8')
    return re.sub(r'\s+', ' ', re.sub(r'—\s*\d+\s*—', ' ', raw))

def norm_date(day, month):
    """One day, written one way. Sukkot's nth day is 14+n Tishrei."""
    m = month.lower()
    if m == 'sukkot':
        return (14 + day, 'tishrei')
    return (day, MONTH.get(m, m))

DATE = r'(\d+)(?:st|nd|rd|th)?\s+(?:day\s+)?of\s+([A-Z][a-z]+)'
ENTRY = r'\{\s*lesson:\s*"([^"]+)"\s*,\s*summary:\s*"((?:[^"\\]|\\.)*)"'

def main(app_path, book_path):
    app  = pathlib.Path(app_path).read_text(encoding='utf-8')
    book = book_text(book_path)
    vocab = set(words(book))
    entries = re.findall(ENTRY, app)
    print(f'{len(entries)} summaries | {len(vocab)} distinct words in the book\n')

    # ── 1. vocabulary ────────────────────────────────────────────────────
    rows = []
    for name, summ in entries:
        w = set(words(summ))
        if w:
            rows.append(((len(w - vocab) / len(w)), name, sorted(w - vocab)))
    rows.sort(reverse=True)
    scores = [r[0] for r in rows]
    loud = [r for r in rows if r[0] > 0.25]
    print('1. VOCABULARY')
    print(f'   words not in the book: median {statistics.median(scores):.1%}, '
          f'mean {statistics.mean(scores):.1%}')
    print(f'   summaries over 25%: {len(loud)}')
    for frac, name, miss in loud[:20]:
        print(f'     {name}  {frac:.0%}  {", ".join(miss[:14])}')

    # ── 2. dates ─────────────────────────────────────────────────────────
    bk = {}
    for m in re.finditer(r'(Likutei Moharan\s*(II)?\s*(Tinyana)?,?\s*|Tinyana,\s*)?'
                         r'(?:Lesson|Torah)\s+(\d+)[^.]{0,60}?for the ' + DATE, book):
        vol = 'II' if (m.group(2) or m.group(3)) else 'I'
        bk.setdefault((vol, int(m.group(4))), set()).add(
            norm_date(int(m.group(5)), m.group(6)))

    agree = absent = 0
    wrong = []
    for name, summ in entries:
        nm = re.match(r'Likutei Moharan(\s*II)?,\s*(?:Lesson|Torah)\s*(\d+)', name)
        dm = re.search(r'for the ' + DATE, summ)
        if not (nm and dm):
            continue
        key = ('II' if nm.group(1) else 'I', int(nm.group(2)))
        got = norm_date(int(dm.group(1)), dm.group(2))
        if key not in bk:
            absent += 1
        elif got in bk[key]:
            agree += 1
        else:
            wrong.append((name, got, sorted(bk[key])))

    print('\n2. DATES')
    print(f'   agree: {agree}   disagree: {len(wrong)}   '
          f'lesson not located in the book: {absent}')
    for name, got, want in wrong[:20]:
        print(f'     {name}: app {got}, book {want}')

    bad = len(loud) + len(wrong)
    print(f'\n{bad} flagged')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
