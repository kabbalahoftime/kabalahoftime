"""Make a fresh container able to set the books. Safe to re-run.

    python3.13 tools/setup_book_fonts.py

The container is rebuilt for every session and keeps none of this, so the
first attempt at a PDF fails three times in a row — once for the packages,
once for brotli, once for the faces — and each failure looks like a different
problem. This does the whole of it at once.

**python3 on PATH is 3.11; pip installs into 3.13.** That is the first trap
and the least obvious: `pip install reportlab` reports success and
`python3 tools/make_book_pdf.py` still says there is no module named
reportlab. The setters must be run as `python3.13`.

THE FACES

make_book_pdf.py wants Cormorant Garamond as TrueType in /root/.fonts, and
the repository holds only the webfonts the site serves. It already unpacks
Frank Ruhl Libre that way for Hebrew, for a stated reason — so the page and
the book cannot come to use different type — and the same reason applies to
Cormorant, so it is unpacked here rather than fetched from anywhere.

Google splits Cormorant into a latin subset and a latin-ext subset. Both are
unpacked; the plain latin one is what the setter is pointed at, because every
character in all six manuscripts is in it. Anything outside it would fall to
FreeSerif, which the setter handles and which is visible on the page, so a
manuscript that one day reaches for a character this subset lacks will show
it rather than hide it.
"""
import pathlib, shutil, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FD = pathlib.Path('/root/.fonts')

# brotli is the one that is easy to miss: fontTools imports fine and then
# refuses the woff2 at the moment it is read.
PACKAGES = ['reportlab', 'fonttools', 'python-bidi', 'brotli']

# source webfont -> the name make_book_pdf.py and make_alefbet_pdf.py expect
FACES = {
    'cormorant-garamond-latin.woff2': 'CormorantGaramond-Regular.ttf',
    'cormorant-garamond-italic-latin.woff2': 'CormorantGaramond-Italic.ttf',
}


def main():
    missing = []
    for pkg in PACKAGES:
        mod = {'python-bidi': 'bidi', 'fonttools': 'fontTools'}.get(pkg, pkg)
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print('installing: ' + ', '.join(missing))
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', *missing])

    from fontTools.ttLib import TTFont
    FD.mkdir(parents=True, exist_ok=True)
    for src_name, out_name in FACES.items():
        out = FD / out_name
        if out.exists():
            print(f'{out_name}: already there')
            continue
        src = REPO / 'fonts' / src_name
        if not src.exists():
            sys.exit(f'missing webfont: {src}')
        f = TTFont(str(src))
        f.flavor = None                       # woff2 in, TrueType out
        f.save(str(out))
        print(f'{out_name}: built from {src_name}, {len(f.getBestCmap())} glyphs')

    # The Hebrew face is built by make_book_pdf.py itself, the first time it
    # runs, from the same fonts/ directory. Nothing to do for it here.
    serif = pathlib.Path('/usr/share/fonts/truetype/freefont/FreeSerif.ttf')
    print('FreeSerif (what Cormorant lacks falls to it): '
          + ('found' if serif.exists() else 'MISSING — install fonts-freefont-ttf'))
    print(f'\nready. set a book with:\n  python3.13 tools/make_book_pdf.py '
          f'docs/<name>.md <name>.pdf')
    return 0


if __name__ == '__main__':
    sys.exit(main())
