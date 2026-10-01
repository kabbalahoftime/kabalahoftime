"""Paragraph-aware text extraction from a-year-inside-the-day.pdf.

Chrome's print-to-PDF draws one BT/Tm block per visual line, so the vertical
delta between consecutive Tm matrices is the leading. Measured over the body
pages it clusters: 22-23 units inside a paragraph, 38-39 between paragraphs,
44+ around headings. So a delta of 30 or more is a paragraph break and
anything smaller is a soft wrap to be rejoined.
"""
import re, zlib, sys, json

PDF = '/home/user/kabalahoftime/a-year-inside-the-day.pdf'
d = open(PDF, 'rb').read()
streams = []
for m in re.finditer(rb'stream\r?\n', d):
    s = m.end(); e = d.find(b'endstream', s)
    if e < 0: continue
    try: streams.append(zlib.decompress(d[s:e]))
    except Exception: pass

def parse_cmap(c):
    m = {}
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', c, re.S):
        for src, dst in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            m[int(src, 16)] = ''.join(chr(int(dst[i:i+4], 16)) for i in range(0, len(dst), 4))
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', c, re.S):
        for lo, hi, dst in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            lo, hi, base = int(lo, 16), int(hi, 16), int(dst, 16)
            for i, code in enumerate(range(lo, hi + 1)): m[code] = chr(base + i)
    return m

U = {}
for s in streams:
    if b'beginbfchar' in s or b'beginbfrange' in s: U.update(parse_cmap(s))

def hex2txt(h):
    h = h.decode('latin-1')
    return ''.join(U.get(int(h[i:i+4], 16), '�') for i in range(0, len(h) - 3, 4))

TOKEN = re.compile(
    rb'<([0-9A-Fa-f]+)>\s*Tj'
    rb'|\[(.*?)\]\s*TJ'
    rb'|([-\d.]+ [-\d.]+ [-\d.]+ [-\d.]+ [-\d.]+ ([-\d.]+))\s+Tm')

PARA_GAP = 30.0

def page_lines(st):
    """[(text, gap_above)] — gap_above is the leading from the previous line.

    A new Tm at the SAME y is a font switch mid-line, not a new line: the
    italics are drawn as their own text object. Joining those as separate
    lines put a space in front of whatever followed them — "the year's fall :
    the awakening", "Tikkun HaKlali ,". Only a real change of y breaks a line,
    and runs within one are concatenated with nothing between, the spaces
    being real glyphs in this file.
    """
    out, cur, lastY, gap = [], [], None, 0.0
    def flush():
        t = ''.join(cur).strip()
        if t: out.append((t, gap))
        cur.clear()
    for m in TOKEN.finditer(st):
        if m.group(1):
            cur.append(hex2txt(m.group(1)))
        elif m.group(2):
            for h in re.findall(rb'<([0-9A-Fa-f]+)>', m.group(2)): cur.append(hex2txt(h))
        elif m.group(3):
            y = float(m.group(4))
            if lastY is not None and abs(y - lastY) < 1.0:
                lastY = y                      # same line, different font
                continue
            flush()
            gap = abs(y - lastY) if lastY is not None else 999.0
            lastY = y
    flush()
    return out

body = [s for s in streams if b'Tj' in s or b'TJ' in s]

def paragraphs():
    """Every page's lines rejoined into paragraphs, in reading order."""
    paras, buf = [], []
    for st in body[2:]:                       # pages 1-2 are the contents
        for text, gap in page_lines(st):
            if gap >= PARA_GAP and buf:
                paras.append(' '.join(buf)); buf = []
            buf.append(text)
    if buf: paras.append(' '.join(buf))
    return [re.sub(r'\s+', ' ', p).strip() for p in paras if p.strip()]

if __name__ == '__main__':
    ps = paragraphs()
    print(len(ps), 'paragraphs')
    for p in ps[:int(sys.argv[1]) if len(sys.argv) > 1 else 25]:
        print('---', p[:220])
