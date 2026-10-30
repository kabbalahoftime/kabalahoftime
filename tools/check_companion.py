"""Check the daily companion's claims about this app against the app itself.

The companion's text was generated, which means it can describe an app that
does not exist and put words in this one's mouth. It did both. The sweep that
found it is in docs/companion-audit.md; this is the same sweep, so a reworked
companion can be checked the same way before it goes back online.

    python3 tools/check_companion.py index.html companion.json

Three passes, all of them string checks against what index.html can actually
render — text nodes, JS string and template literals, title/aria-label/
placeholder. Nothing here understands meaning:

  1. routes    — sentences naming a view, tab, button, card, pane or dial,
                 and whether that name exists anywhere in the app.
  2. claims    — sentences that say "the app"/"the site" does or has
                 something, listed in full for a reader.
  3. quotations — anything in quotation marks sitting next to a phrase that
                 attributes it to the app. These are the dangerous ones: a
                 fabricated motto reads exactly like a real one.

It exits 1 if anything is flagged, so it can gate a rebuild.

What it cannot do: the teaching is ~290,000 characters of Torah, Chassidus and
practice. A string check finds an invented button. It will not find an
invented teaching, a misquoted Rebbe or a wrong date. Those need a reader.
"""
import json, re, sys, html, pathlib

def app_strings(app):
    # Comments are never shown to anyone, so they are not the app saying
    # anything. This matters more than it sounds: the comment explaining why
    # the companion was taken offline quotes the invented motto, and without
    # this the checker finds its own explanation and calls the motto real.
    app = re.sub(r'<!--.*?-->', ' ', app, flags=re.S)       # html
    app = re.sub(r'/\*.*?\*/', ' ', app, flags=re.S)        # js and css blocks
    app = re.sub(r'^[ \t]*//.*$', ' ', app, flags=re.M)     # whole-line js
    parts  = re.findall(r'>([^<>{}]{2,200})<', app)
    parts += re.findall(r"'([^'\\\n]{2,200})'", app)
    parts += re.findall(r'"([^"\\\n]{2,200})"', app)
    parts += re.findall(r'`([^`\\]{2,400})`', app)
    parts += re.findall(r'(?:title|aria-label|placeholder)="([^"]{2,200})"', app)
    hay = ' · '.join(html.unescape(p) for p in parts).lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', hay))

def flatten(entry):
    out = []
    for k in ('title', 'body', 'practice', 'teaser', 'teaserLead'):
        v = entry.get(k)
        out.append(' '.join(v) if isinstance(v, list) else str(v or ''))
    return ' '.join(out)

NUMBERS = {'88': 'eighty-eight', '52': 'fifty-two', '49': 'forty-nine',
           '22': 'twenty-two', '28': 'twenty-eight', '13': 'thirteen',
           '15': 'fifteen', '72': 'seventy-two', '91': 'ninety-one',
           '41': 'forty-one', '40': 'forty', '364': 'three hundred and sixty-four'}


def variants(phrase):
    """The same claim, spelled the ways the app might spell it.

    Day 151's "88 Mochin minutes" was reported as invented because the search
    was for 88 and the app writes "eighty-eight". Absence was concluded from a
    search that could not have found it. Apostrophes do the same: Ma'alot
    HaZman is in the app with a curly one.
    """
    out = {phrase}
    for a, b in NUMBERS.items():
        if a in phrase:
            out.add(phrase.replace(a, b))
        if b in phrase.lower():
            out.add(re.sub(b, a, phrase, flags=re.I))
    return {v.replace('\u2019', "'").replace('\u2018', "'") for v in out}


def present(phrase, hay):
    """Is this phrase somewhere in the app? Short ones are not worth judging."""
    if any(_present_one(v, hay) for v in variants(phrase)):
        return True
    return False


def _present_one(phrase, hay):
    n = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', phrase.lower())).strip()
    if len(n) < 8:
        return True
    if n in hay:
        return True
    # A long phrase may be split across concatenated literals, so let a run of
    # eight words carry it. Shorter phrases must match whole: a nine-word
    # motto that only half-matches is exactly the thing being looked for.
    w = n.split()
    if len(w) >= 12:
        return any(' '.join(w[i:i + 8]) in hay for i in range(len(w) - 7))
    return False

UI_WORDS = (r'view|tab|button|card|pane|panel|dial|toggle|widget|menu|icon|link')
# The word boundaries after "app" and "site" are load-bearing. Without them
# "the apple of the eye" contains "the app", and a psalm was reported as a
# claim about this application.
INTERFACE = re.compile(r'\b(the app\b|this app\b|the site\b|the screen\b|on screen\b|'
                       r'\w+ (?:' + UI_WORDS + r')\b|tap\b|tapping\b|click\b|'
                       r'scroll\b|swipe\b|long-press)', re.I)
SENTENCE = re.compile(r'[^.!?\n]{6,400}?[.!?]')
ABOUT_APP = re.compile(r'\b(the app|this app|the site)\b[^.!?]{0,220}', re.I)
QUOTED = re.compile(r'“([^”]{6,200})”|"([^"]{6,200})"')
ATTRIBUTED = re.compile(
    r"(app'?s? own words|app'?s? motto|app'?s? words|app'?s? guide|"
    r"the app (?:says|calls|puts|names|offers|takes)|in the app'?s?|"
    r"the (?:card|dial|pane|tab|view|button|screen|guide) (?:says|carries|reads|calls)|"
    r"the app'?s? (?:own|rule|line|phrase|name)|the site (?:says|calls))", re.I)

def named_in(sentence):
    out  = re.findall(r'“([^”]{2,46})”', sentence)
    out += re.findall(r'"([^"]{2,46})"', sentence)
    out += [m.group(1) for m in re.finditer(
        r'\b((?:[A-Z][\w’\'-]*)(?:\s+[A-Z][\w’\'-]*){0,3})\s+(?:' + UI_WORDS + r')\b',
        sentence)]
    out += [m.group(1) for m in re.finditer(
        r'\bthe\s+([a-z][\w’\'-]*(?:\s+[a-z][\w’\'-]*){0,2})\s+(?:' + UI_WORDS + r')\b',
        sentence)]
    return [c for c in dict.fromkeys(x.strip() for x in out) if c]

def main(app_path, companion_path):
    hay  = app_strings(pathlib.Path(app_path).read_text(encoding='utf-8'))
    days = json.loads(pathlib.Path(companion_path).read_text(encoding='utf-8'))['days']
    flagged = 0

    print(f'{len(days)} entries\n')

    print('=' * 72)
    print('1. ROUTES AND LABELS')
    print('=' * 72)
    for n in sorted(days, key=int):
        for s in SENTENCE.findall(flatten(days[n])):
            if not INTERFACE.search(s):
                continue
            miss = [c for c in named_in(s) if not present(c, hay)]
            if miss:
                flagged += 1
                print(f'\nday {int(n):>3}  not in the app: {miss}\n   {s.strip()[:300]}')

    print('\n' + '=' * 72)
    print('2. CLAIMS ABOUT THE APP  (read these by eye)')
    print('=' * 72)
    for n in sorted(days, key=int):
        for m in ABOUT_APP.finditer(flatten(days[n])):
            print(f'day {int(n):>3}: {m.group(0).strip()[:220]}')

    print('\n' + '=' * 72)
    print('3. QUOTATIONS ATTRIBUTED TO THE APP')
    print('=' * 72)
    for n in sorted(days, key=int):
        t = flatten(days[n])
        for m in QUOTED.finditer(t):
            q = (m.group(1) or m.group(2)).strip()
            if not ATTRIBUTED.search(t[max(0, m.start() - 180): m.end() + 180]):
                continue
            if present(q, hay):
                print(f'day {int(n):>3}  ok              “{q[:120]}”')
            else:
                flagged += 1
                print(f'day {int(n):>3}  NOT IN THE APP  “{q[:120]}”')

    print(f'\n{flagged} flagged')
    return 1 if flagged else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
