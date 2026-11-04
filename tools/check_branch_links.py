"""Check the leaves against the branches they hang on.

    python3 -I tools/check_branch_links.py branches-links.json \
        branches-sciences.json branches-arts.json

branches-links.json is written by hand; the two volumes are generated from
their PDFs and are overwritten on every rebuild. So the two can drift apart
in a way nobody sees: a station renamed in a book leaves its links pointing
at a name that no longer exists, and the app simply draws no leaves there
rather than saying anything.

That is the whole point of this. It is cheap, and it fails loudly.

  * every volume named in the links is a volume that exists
  * every station named is one of that volume's ten
  * every link has a label and an address, and the address is http(s)
  * nothing is listed twice under one station

What it cannot do: say whether a link is any good, or whether it still
resolves. It does not go out to the network — a checker that needs the
internet is a checker that fails on a train.
"""
import json, pathlib, re, sys

OK_SCHEME = re.compile(r'^https?://', re.I)


def main(links_path, *volume_paths):
    links = json.loads(pathlib.Path(links_path).read_text(encoding='utf-8'))
    tree = links.get('links') or {}

    volumes = {}
    for p in volume_paths:
        doc = json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
        # the file is named branches-<volume>.json; that is the key the
        # links use, and it is taken from the name rather than from inside
        # so the two cannot disagree about what a volume is called.
        name = pathlib.Path(p).stem.replace('branches-', '')
        volumes[name] = {c['sefirah']: c['name'] for c in doc['chapters']}

    bad, n = [], 0
    for vol, stations in tree.items():
        if vol not in volumes:
            bad.append(f'no such volume: {vol!r} (have {", ".join(sorted(volumes))})')
            continue
        for station, items in stations.items():
            if station not in volumes[vol]:
                bad.append(f'{vol}: no station {station!r} '
                           f'(have {", ".join(volumes[vol])})')
                continue
            seen = set()
            for i, it in enumerate(items, 1):
                where = f'{vol}/{station}[{i}]'
                label, url = (it.get('label') or '').strip(), (it.get('url') or '').strip()
                if not label:
                    bad.append(f'{where}: no label')
                if not url:
                    bad.append(f'{where}: no url')
                elif not OK_SCHEME.match(url):
                    bad.append(f'{where}: {url!r} is not http(s)')
                if url and url in seen:
                    bad.append(f'{where}: {url} is listed twice under this station')
                seen.add(url)
                n += 1

    for vol in sorted(volumes):
        got = {s: len(tree.get(vol, {}).get(s, [])) for s in volumes[vol]}
        live = {s: c for s, c in got.items() if c}
        print(f'{vol}: {sum(got.values())} leaves over {len(live)} of 10 stations'
              + (('  — ' + ', '.join(f'{s} {c}' for s, c in live.items())) if live else ''))

    print()
    for b in bad:
        print('  FAIL  ' + b)
    print(f'{n} leaves checked, {len(bad)} faults')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
