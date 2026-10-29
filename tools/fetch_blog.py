"""Pull the blog down into one corpus file.

kabbalahoftime.com is the source for the companion and for the door, so the
posts need to be on disk where a script can check a summary against the thing
it summarises. That is the whole difference between the daily companion that
failed and the Likutei Moharan summaries that held up: one had a source in the
room and one did not.

    python3 -I tools/fetch_blog.py out/corpus.json

Blogger's feed caps a page below the max-results asked for, and the cap moves,
so this pages three ways and keeps the union: straight paging, smaller pages,
and one request per year. 677 posts come back; the feed's own total counts
drafts.

Output is one JSON list, oldest first: date, title, url, words, text.
"""
import html, json, pathlib, re, sys, time, urllib.request

FEED = 'https://www.kabbalahoftime.com/feeds/posts/default?alt=json'


def get(url, tries=3):
    for a in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.loads(r.read().decode('utf-8'))['feed'].get('entry', [])
        except Exception as e:
            if a == tries - 1:
                print(f'  fail: {e}', file=sys.stderr)
                return []
            time.sleep(2 * (a + 1))


def main(out_path):
    seen = {}

    def take(entries):
        new = 0
        for e in entries:
            pid = e['id']['$t']
            if pid in seen:
                continue
            body = e.get('content', {}).get('$t', '')
            txt = re.sub(r'\s+', ' ',
                         html.unescape(re.sub(r'<[^>]+>', ' ', body))).strip()
            seen[pid] = {
                'date': e['published']['$t'][:10],
                'title': html.unescape(e['title']['$t']).strip(),
                'url': next((l['href'] for l in e.get('link', [])
                             if l.get('rel') == 'alternate'), ''),
                'words': len(txt.split()),
                'text': txt,
            }
            new += 1
        return new

    for size, step in ((150, 150), (50, 50)):
        for i in range(1, 800, step):
            n = take(get(f'{FEED}&max-results={size}&start-index={i}'))
            if n:
                print(f'  page {i:>3} (+{size}): {n} new')
            time.sleep(0.2)

    for y in range(2010, 2027):
        n = take(get(f'{FEED}&max-results=150'
                     f'&published-min={y}-01-01T00:00:00-00:00'
                     f'&published-max={y+1}-01-01T00:00:00-00:00'))
        if n:
            print(f'  {y}: {n} new')
        time.sleep(0.2)

    rows = sorted(seen.values(), key=lambda p: p['date'])
    out = pathlib.Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False), encoding='utf-8')
    print(f'\n{len(rows)} posts, {sum(p["words"] for p in rows):,} words '
          f'-> {out_path}')


if __name__ == '__main__':
    main(sys.argv[1])
