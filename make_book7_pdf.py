#!/usr/bin/env python3
"""Build a beautiful PDF for Book 7 (The Gathering of Songs) from book7_content.txt."""

import re
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, PageBreak, HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Design tokens ──────────────────────────────────────────────────────────────
GOLD   = colors.HexColor("#8B6914")
LGOLD  = colors.HexColor("#C9A84C")
DARK   = colors.HexColor("#1a1a1a")
GREY   = colors.HexColor("#555555")
PALE   = colors.HexColor("#aaaaaa")
RULE_C = colors.HexColor("#d4c49a")

PW, PH = letter
ML = MR = 1.25 * inch
MT = 1.0 * inch
MB = 0.9 * inch

# ── Canonical week titles ─────────────────────────────────────────────────────
WEEK_LIST = [
    (1,  "The Rooster is Saying"),
    (2,  "The Hen is Saying"),
    (3,  "The Dove is Saying"),
    (4,  "The Eagle is Saying"),
    (5,  "The Crane is Saying"),
    (6,  "The Songbird is Saying"),
    (7,  "The Swallow is Saying"),
    (8,  "The Swift is Saying"),
    (9,  "The Stormy Petrel is Saying"),
    (10, "The Bat is Saying"),
    (11, "The Stork is Saying"),
    (12, "The Raven is Saying"),
    (13, "The Starling is Singing"),
    (14, "The Domestic Goose is Saying"),
    (15, "The Wild Goose is Saying"),
    (16, "The Ducks are Saying"),
    (17, "The Bee-Eater is Saying"),
    (18, "The Grasshopper is Saying"),
    (19, "The Locust is Saying"),
    (20, "The Spider is Saying"),
    (21, "The Fly is Saying"),
    (22, "The Giant Sea Creatures are Saying"),
    (23, "The Leviathan is Saying"),
    (24, "The Fish are Saying"),
    (25, "The Frog is Saying"),
    (26, "The Lamb is Saying"),
    (27, "The Cow is Saying"),
    (28, "The Pig is Saying"),
    (29, "The Beast of Burden is Saying"),
    (30, "The Camel is Saying"),
    (31, "The Horse is Saying"),
    (32, "The Mule is Saying"),
    (33, "The Donkey is Saying"),
    (34, "The Ox is Saying"),
    (35, "The Wild Animals Say"),
    (36, "The Gazelle is Saying"),
    (37, "The Elephant is Saying"),
    (38, "The Lion is Saying"),
    (39, "The Bear is Saying"),
    (40, "The Wolf is Saying"),
    (41, "The Fox is Saying"),
    (42, "The Hound is Saying"),
    (43, "The Cat is Saying"),
    (44, "The Mouse is Saying"),
    (45, "The Creeping Creatures are Saying"),
    (46, "The Prolific Creeping Creatures are Saying"),
    (47, "The Snake is Saying"),
    (48, "The Scorpion is Saying"),
    (49, "The Snail is Saying"),
    (50, "The Ant is Saying"),
    (51, "The Weasel is Saying"),
    (52, "The Dogs are Saying"),
]

# ── Compiled patterns ─────────────────────────────────────────────────────────
# Matches any "Week N" line in any format ("Week 12 (Book 7):", "Week 19:", etc.)
WEEK_N_RE = re.compile(r"^\s*Week\s+(\d+)\b", re.I)

# Matches standard single-line animal headers ("The Raven is saying,")
ANIMAL_RE = re.compile(
    r"^\s*The\s+\S+(?:\s+\S+)*\s+(?:is|are)\s+(?:saying|singing|say)\b",
    re.I,
)

# Matches lines that end with "is saying" (continuation of multi-line headers)
IS_SAYING_END_RE = re.compile(r"\bis\s+saying[,:.]*\s*$", re.I)

# Lines to skip in the header zone of each section
HEADER_LINE_RE = re.compile(
    r"^(?:"
    r'B"H'
    r"|Week\s+\d+"
    r"|The\s+.+\s+(?:is|are)\s+(?:saying|singing|say)"
    r"|.+\s+(?:is|are)\s+saying[,:.]*\s*$"
    r")",
    re.I,
)

# Standalone B"H lines to skip anywhere in content
BH_ONLY_RE = re.compile(r'^B"H\s*$', re.I)


# ── Parsing ────────────────────────────────────────────────────────────────────

def find_sections(lines):
    """
    Return sorted list of (line_idx_0based, week_num) for all 52 sections.

    Strategy:
    - Explicit: any line starting with "Week N" → week_num from the label
    - Implicit: animal-name lines (and two-line headers like Wild Goose)
      that are not within 10 lines of an explicit Week N line
    - Implicit sections are assigned the week numbers missing from explicit,
      in sequential order (the file presents sections in order).
    """
    # Pass 1: find explicit "Week N" lines and mark nearby lines as claimed
    explicit = {}      # week_num → line_idx
    claimed  = set()

    for i, raw in enumerate(lines):
        m = WEEK_N_RE.match(raw.strip())
        if m:
            wn = int(m.group(1))
            if wn not in explicit:
                explicit[wn] = i
            for offset in range(0, 10):
                claimed.add(i + offset)

    # Pass 2: find implicit section starts (not claimed)
    implicit = []

    for i, raw in enumerate(lines):
        if i in claimed:
            continue
        s = raw.strip()
        if ANIMAL_RE.match(s):
            implicit.append(i)
        elif IS_SAYING_END_RE.search(s):
            # Multi-line header: "is saying" ends this line but the animal
            # description was on the previous line (e.g. Wild Goose).
            if i > 0 and (i - 1) not in claimed:
                prev = lines[i - 1].strip()
                if re.match(r"^The\s+", prev, re.I):
                    implicit.append(i - 1)

    # Assign missing week numbers to implicit sections in file order
    missing = sorted(set(range(1, 53)) - set(explicit.keys()))
    implicit_sorted = sorted(set(implicit))

    if len(implicit_sorted) != len(missing):
        print(f"WARNING: {len(implicit_sorted)} implicit sections but "
              f"{len(missing)} missing week numbers: {missing}")

    result = list(explicit.items())          # (week_num, line_idx) pairs
    result = [(li, wn) for wn, li in result] # swap to (line_idx, week_num)
    for j, li in enumerate(implicit_sorted):
        if j < len(missing):
            result.append((li, missing[j]))

    return sorted(result, key=lambda x: x[0])


def extract_stanzas(lines, start, end):
    """
    From lines[start:end] find the content start (skipping the section header)
    then collect stanzas (groups of non-blank lines separated by blank lines).
    """
    # Locate content start: skip header lines at top of section
    content_start = start
    for i in range(start, min(start + 12, end)):
        s = lines[i].strip()
        if not s:
            continue
        if HEADER_LINE_RE.match(s):
            content_start = i + 1
        else:
            # First non-header line.  Check whether the next non-blank line
            # is an "is saying" continuation (two-line header, e.g. Wild Goose).
            found_continuation = False
            for j in range(i + 1, min(i + 4, end)):
                ns = lines[j].strip()
                if ns and IS_SAYING_END_RE.search(ns):
                    content_start = j + 1
                    found_continuation = True
                    break
                elif ns:
                    break
            if not found_continuation:
                content_start = i
            break

    # Collect stanzas
    stanzas = []
    current = []
    for raw in lines[content_start:end]:
        s = raw.strip()
        if not s:
            if current:
                stanzas.append(current)
                current = []
        elif BH_ONLY_RE.match(s):
            continue  # skip standalone B"H within content
        else:
            current.append(s)
    if current:
        stanzas.append(current)

    return stanzas


def parse_weeks(path):
    """Return list of (week_num, canonical_title, stanzas) for all 52 weeks."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    sections = find_sections(lines)

    result = []
    for idx, (start, week_num) in enumerate(sections):
        end = sections[idx + 1][0] if idx + 1 < len(sections) else len(lines)
        title = WEEK_LIST[week_num - 1][1]
        stanzas = extract_stanzas(lines, start, end)
        result.append((week_num, title, stanzas))

    return result


# ── PDF rendering ──────────────────────────────────────────────────────────────

def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Italic", 8.5)
    canvas.setFillColor(PALE)
    canvas.drawCentredString(PW / 2, 0.45 * inch, str(canvas.getPageNumber()))
    canvas.setFont("Times-Roman", 7.5)
    canvas.setFillColor(PALE)
    canvas.drawString(ML, 0.45 * inch,
                      "Kabbalah of Time  ·  Book 7: The Gathering of Songs")
    canvas.drawRightString(PW - MR, 0.45 * inch, "www.kabbalahoftime.com")
    canvas.restoreState()


def _no_footer(canvas, doc):
    pass


def sanitize(text):
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def build_pdf(content_path, output_path):
    doc = BaseDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
        title="Kabbalah of Time — Book 7: The Gathering of Songs",
        author="www.kabbalahoftime.com",
    )
    body_frame = Frame(ML, MB, PW - ML - MR, PH - MT - MB, id="body")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[body_frame], onPage=_no_footer),
        PageTemplate(id="main",  frames=[body_frame], onPage=_footer),
    ])

    # ── Styles ─────────────────────────────────────────────────────────────────
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    cover_title = S("CoverTitle",
        fontName="Times-Bold",   fontSize=26, leading=34,
        textColor=GOLD, alignment=TA_CENTER, spaceAfter=6)

    cover_sub = S("CoverSub",
        fontName="Times-Italic", fontSize=14, leading=20,
        textColor=DARK, alignment=TA_CENTER, spaceAfter=6)

    cover_desc = S("CoverDesc",
        fontName="Times-Roman",  fontSize=11, leading=17,
        textColor=GREY, alignment=TA_CENTER, spaceAfter=4)

    cover_url = S("CoverUrl",
        fontName="Times-Roman",  fontSize=9, leading=13,
        textColor=PALE, alignment=TA_CENTER)

    bh_style = S("BH",
        fontName="Times-Italic", fontSize=9, leading=14,
        textColor=LGOLD, alignment=TA_CENTER, spaceAfter=2)

    week_label = S("WeekLabel",
        fontName="Times-Roman",  fontSize=8.5, leading=12,
        textColor=LGOLD, alignment=TA_CENTER,
        spaceBefore=0, spaceAfter=4,
        letterSpacing=3)

    week_title = S("WeekTitle",
        fontName="Times-Bold",   fontSize=19, leading=26,
        textColor=GOLD, alignment=TA_CENTER, spaceAfter=10)

    stanza_style = S("Stanza",
        fontName="Times-Roman",  fontSize=10.5, leading=17,
        textColor=DARK, alignment=TA_LEFT,
        leftIndent=0.1 * inch, spaceAfter=10)

    missing_style = S("Missing",
        fontName="Times-Italic", fontSize=10, leading=14,
        textColor=PALE, alignment=TA_CENTER)

    # ── Cover page ─────────────────────────────────────────────────────────────
    story = []
    story.append(Spacer(1, 1.6 * inch))
    story.append(Paragraph('B"H', bh_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="55%", thickness=0.8, color=RULE_C,
                             hAlign="CENTER"))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Kabbalah of Time", cover_title))
    story.append(Paragraph("Book 7", cover_sub))
    story.append(Paragraph("The Gathering of Songs", cover_sub))
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="55%", thickness=0.8, color=RULE_C,
                             hAlign="CENTER"))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(
        "For each week, all the verses of the songs in Books 1–6,<br/>"
        "rearranged and combined into a single song.",
        cover_desc))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("52 Weeks  ·  Perek Shirah", cover_desc))
    story.append(Spacer(1, 0.6 * inch))
    story.append(Paragraph("www.kabbalahoftime.com", cover_url))

    # Switch to main template (footer on every subsequent page)
    story.append(PageBreak())

    # ── Week sections ──────────────────────────────────────────────────────────
    weeks = parse_weeks(content_path)
    print(f"Parsed {len(weeks)} week sections.")
    for wn, title, stanzas in weeks:
        print(f"  Week {wn:2d}: {title}  ({len(stanzas)} stanzas)")

    for week_num, title, stanzas in weeks:
        story.append(PageBreak())
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph('B"H', bh_style))
        story.append(Spacer(1, 0.05 * inch))
        story.append(Paragraph(f"WEEK  {week_num}", week_label))
        story.append(Paragraph(title, week_title))
        story.append(HRFlowable(
            width="80%", thickness=0.7, color=RULE_C,
            hAlign="CENTER", spaceAfter=14))

        if not stanzas:
            story.append(Paragraph(
                "(Content not yet available — see www.kabbalahoftime.com)",
                missing_style))
        else:
            for stanza_lines in stanzas:
                text = "<br/>".join(sanitize(ln) for ln in stanza_lines)
                story.append(KeepTogether([
                    Paragraph(text, stanza_style),
                    Spacer(1, 2),
                ]))

    print("Building PDF …")
    doc.build(story)
    print(f"Done → {output_path}")


if __name__ == "__main__":
    build_pdf(
        "/home/user/kabalahoftime/book7_content.txt",
        "/home/user/kabalahoftime/book7_gathering_of_songs.pdf",
    )
