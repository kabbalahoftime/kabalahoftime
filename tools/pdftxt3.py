"""Paragraph-aware text extraction from the UPDATED manuscript PDF.

A different producer from the first one. mPDF, not Chrome, which changes
three things:

  * The fonts are Type0/Identity-H, so a string in the content stream is
    two-byte CIDs, not one byte to a glyph.
  * Each font carries its own ToUnicode CMap and the CIDs collide between
    them — the same code is a different letter in the roman and the italic —
    so the maps cannot be merged. The current /Fn selects which one decodes.
  * The ToUnicode streams are not compressed, which is why a pass that only
    inflated streams found none of them.

Layout is the same shape as before: one text object per line, with further
Tm matrices at the same y where the font changes or the line is justified.
A new y is a new line; the gap between y values says paragraph or not.
"""
import re, zlib, sys

PDF = '/home/user/kabalahoftime/a-year-inside-the-day.pdf'
d = open(PDF, 'rb').read()

# ── objects ────────────────────────────────────────────────────────────────
OBJ = {}
for m in re.finditer(rb'(\d+)\s+0\s+obj\b', d):
    e = d.find(b'endobj', m.end())
    OBJ[int(m.group(1))] = d[m.end():e]

def stream_of(num):
    body = OBJ[num]
    i = body.find(b'stream')
    if i < 0: return b''
    raw = body[body.find(b'\n', i) + 1:]
    raw = raw[:raw.rfind(b'endstream')] if b'endstream' in raw else raw
    if b'/FlateDecode' in body[:i]:
        try: return zlib.decompress(raw)
        except Exception: return b''
    return raw

# ── one ToUnicode map per font resource name ───────────────────────────────
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

FONTS = {}                                  # '/F2' -> {cid: text}
for m in re.finditer(rb'/Font\s*<<(.*?)>>', d, re.S):
    for name, num in re.findall(rb'/(F\d+)\s+(\d+)\s+0\s+R', m.group(1)):
        num = int(num)
        body = OBJ.get(num, b'')
        tu = re.search(rb'/ToUnicode\s+(\d+)', body)
        if tu: FONTS['/' + name.decode()] = parse_cmap(stream_of(int(tu.group(1))))

# ── literal and hex strings ────────────────────────────────────────────────
ESC = {b'n': b'\n', b'r': b'\r', b't': b'\t', b'b': b'\b', b'f': b'\f',
       b'(': b'(', b')': b')', b'\\': b'\\'}

def unescape(s):
    out, i = bytearray(), 0
    while i < len(s):
        c = s[i:i+1]
        if c == b'\\' and i + 1 < len(s):
            nxt = s[i+1:i+2]
            if nxt in ESC: out += ESC[nxt]; i += 2; continue
            oct_ = re.match(rb'[0-7]{1,3}', s[i+1:i+4])
            if oct_: out.append(int(oct_.group(0), 8) & 0xFF); i += 1 + len(oct_.group(0)); continue
            if nxt == b'\n': i += 2; continue
            out += nxt; i += 2; continue
        out += c; i += 1
    return bytes(out)

def decode(raw, cmap):
    """Identity-H: two bytes to a CID."""
    out = []
    for i in range(0, len(raw) - 1, 2):
        cid = (raw[i] << 8) | raw[i+1]
        out.append(cmap.get(cid, '�' if cid else ''))
    return ''.join(out)

# ── one page's lines ───────────────────────────────────────────────────────
TOKEN = re.compile(
    rb'/(F\d+)\s+[\d.]+\s+Tf'                                   # 1 font
    rb'|([\d.-]+)\s+([\d.-]+)\s+Td'                             # 2,3 Td
    rb'|[\d.-]+\s+[\d.-]+\s+[\d.-]+\s+[\d.-]+\s+([\d.-]+)\s+([\d.-]+)\s+Tm'   # 4,5 Tm
    rb'|\(((?:\\.|[^\\()])*)\)\s*Tj'                            # 6 literal
    rb'|<([0-9A-Fa-f\s]*)>\s*Tj', re.S)                         # 7 hex

PARA_GAP = 15.0          # measured: ~11 inside a paragraph, 20+ between

def page_lines(st):
    out, cur, font, y, lastY, gap = [], [], None, None, None, 0.0
    def flush():
        t = ''.join(cur).strip()
        if t: out.append((t, gap))
        cur.clear()
    for m in TOKEN.finditer(st):
        if m.group(1):
            font = '/' + m.group(1).decode()
        elif m.group(3) is not None or m.group(5) is not None:
            ny = float(m.group(3) if m.group(3) is not None else m.group(5))
            if lastY is None or abs(ny - lastY) >= 0.6:
                flush()
                gap = abs(ny - lastY) if lastY is not None else 999.0
                lastY = ny
        elif m.group(6) is not None:
            cur.append(decode(unescape(m.group(6)), FONTS.get(font, {})))
        elif m.group(7) is not None:
            h = re.sub(rb'\s', b'', m.group(7))
            cur.append(decode(bytes.fromhex(h.decode()), FONTS.get(font, {})))
    flush()
    return out

PAGES = []
for num, body in OBJ.items():
    if b'/Type /Page' in body and b'/Contents' in body:
        c = re.search(rb'/Contents\s+(\d+)', body)
        if c: PAGES.append((num, int(c.group(1))))
PAGES.sort()

def paragraphs():
    paras, buf = [], []
    for _, cnum in PAGES:
        for text, gap in page_lines(stream_of(cnum)):
            if gap >= PARA_GAP and buf:
                paras.append(' '.join(buf)); buf = []
            buf.append(text)
    if buf: paras.append(' '.join(buf))
    return [re.sub(r'\s+', ' ', p).strip() for p in paras if p.strip()]

if __name__ == '__main__':
    print('fonts decoded:', {k: len(v) for k, v in FONTS.items()})
    print('pages:', len(PAGES))
    ps = paragraphs()
    print('paragraphs:', len(ps))
    for p in ps[:int(sys.argv[1]) if len(sys.argv) > 1 else 14]:
        print('---', p[:200])
