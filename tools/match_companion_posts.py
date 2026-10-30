"""Pair each of the 364 days with the post it is a summary of.

The companion is one KoT Book for one week, each day, and the week's writing
for that book is a post of its own: 52 weeks x 7 books = 364 posts for 364
days. The addresses are the app's own — BOOK1..6_WEEK_URLS and b7_url, taken
out of the page into docs/week-data.json — and the text is the corpus
tools/fetch_blog.py brings down.

    python3 -I tools/fetch_blog.py out/corpus.json
    python3 -I tools/match_companion_posts.py docs/week-data.json \
        out/corpus.json out/posts.json

The point of this step is that the summaries are then written against a source
that is on disk. That is the whole difference between the companion that came
down in October and the Likutei Moharan summaries that held up: one was
written from nothing and invented a motto, a verse and a route; the other had
its book in the room and came out clean. A summary of a post can be checked
against the post. A summary of nothing cannot be checked at all.

Output is one JSON list, in day order: day, week, book, url, and the post's
title, date, word count and text. A day whose post is not in the corpus is
reported and carries no text, so it cannot be quietly summarised from memory.
"""
import json, pathlib, re, sys
from urllib.parse import urlsplit


def key(url):
    """A post's address, reduced to the part that identifies it.

    Blogger serves the same post at http and https, with and without www,
    and the app's tables were written across twelve years, so the two do not
    always agree on any of that.
    """
    if not url:
        return ''
    s = urlsplit(url.strip())
    path = re.sub(r'\.html?$', '', s.path.rstrip('/')).lower()
    return path or url.strip().lower()


def main(week_path, corpus_path, out_path):
    weeks = json.loads(pathlib.Path(week_path).read_text(encoding='utf-8'))['weeks']
    corpus = json.loads(pathlib.Path(corpus_path).read_text(encoding='utf-8'))

    by_key = {}
    for post in corpus:
        k = key(post.get('url'))
        if k:
            by_key.setdefault(k, post)

    rows, missing = [], []
    for wk in weeks:
        for bi in range(7):
            day = (wk['week'] - 1) * 7 + bi + 1
            url = wk['postUrls'][bi] or ''
            post = by_key.get(key(url))
            if not post:
                missing.append((day, wk['week'], bi + 1, url))
            rows.append({
                'day': day,
                'week': wk['week'],
                'book': bi + 1,
                'url': url,
                'title': (post or {}).get('title', ''),
                'date': (post or {}).get('date', ''),
                'words': (post or {}).get('words', 0),
                'text': (post or {}).get('text', ''),
            })

    rows.sort(key=lambda r: r['day'])
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out_path).write_text(
        json.dumps(rows, ensure_ascii=False), encoding='utf-8')

    have = [r for r in rows if r['text']]
    print(f'{len(rows)} days, {len(have)} with their post in the corpus '
          f'-> {out_path}')
    if have:
        n = sorted(r['words'] for r in have)
        print(f'  words per post: {n[0]} / {n[len(n)//2]} median / {n[-1]}')
        print(f'  total: {sum(r["words"] for r in have):,} words')
    if missing:
        print(f'\n  {len(missing)} without a post in the corpus:')
        for day, w, b, url in missing[:20]:
            print(f'    day {day:>3} (week {w}, book {b}): {url or "(no url)"}')
        if len(missing) > 20:
            print(f'    ... and {len(missing) - 20} more')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:4]))
