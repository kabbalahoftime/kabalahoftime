#!/usr/bin/env python3
"""Fetch all 52 Book 7 blog posts and compile into a PDF."""

import time
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

WEEKS = [
    (1,  "The Rooster is Saying",              "https://www.kabbalahoftime.com/2026/05/week-1-book-7-rooster-is-saying.html"),
    (2,  "The Hen is Saying",                  "https://www.kabbalahoftime.com/2026/05/week-2-book-7-hen-is-saying.html"),
    (3,  "The Dove is Saying",                 "https://www.kabbalahoftime.com/2026/05/week-3-book-7-dove-is-saying.html"),
    (4,  "The Eagle is Saying",                "https://www.kabbalahoftime.com/2026/05/week-4-book-7-eagle-is-saying.html"),
    (5,  "The Crane is Saying",                "https://www.kabbalahoftime.com/2026/05/week-5-book-7-crane-is-saying.html"),
    (6,  "The Songbird is Saying",             "https://www.kabbalahoftime.com/2026/05/week-6-book-7-songbird-is-saying.html"),
    (7,  "The Swallow is Saying",              "https://www.kabbalahoftime.com/2026/05/week-7-book-7-swallow-is-saying.html"),
    (8,  "The Swift is Saying",                "https://www.kabbalahoftime.com/2025/11/week-8-book-7-swift-is-saying"),
    (9,  "The Stormy Petrel is Saying",        "https://www.kabbalahoftime.com/2026/05/week-9-book-7-stormy-petrel-is-saying.html"),
    (10, "The Bat is Saying",                  "https://www.kabbalahoftime.com/2026/05/week-10-book-7-bat-is-saying.html"),
    (11, "The Stork is Saying",                "https://www.kabbalahoftime.com/2026/05/week-11-book-7-stork-is-saying.html"),
    (12, "The Raven is Saying",                "https://www.kabbalahoftime.com/2020/12/week-12-book-7-raven-is-saying.html"),
    (13, "The Starling is Singing",            "https://www.kabbalahoftime.com/2020/12/week-13-book-7-starling-is-singing.html"),
    (14, "The Domestic Goose is Saying",       "https://www.kabbalahoftime.com/2020/12/week-14-book-7-domestic-goose-is-saying.html"),
    (15, "The Wild Goose is Saying",           "https://www.kabbalahoftime.com/2026/05/week-15-book-7-wild-goose-is-saying.html"),
    (16, "The Ducks are Saying",               "https://www.kabbalahoftime.com/2026/05/week-16-book-7-ducks-are-saying.html"),
    (17, "The Bee-Eater is Saying",            "https://www.kabbalahoftime.com/2026/05/week-17-book-7-bee-eater-is-saying.html"),
    (18, "The Grasshopper is Saying",          "https://www.kabbalahoftime.com/2022/01/week-18-grasshopper-is-saying-book-7.html"),
    (19, "The Locust is Saying",               "https://www.kabbalahoftime.com/2021/01/week-19-locust-is-saying-book-7.html"),
    (20, "The Spider is Saying",               "https://www.kabbalahoftime.com/2021/01/week-20-book-7-spider-is-saying.html"),
    (21, "The Ant is Saying",                  "https://www.kabbalahoftime.com/2014/01/week-21-to-keep-things-in-perspective.html"),
    (22, "The Giant Sea Creatures are Saying", "https://www.kabbalahoftime.com/2021/02/week-22-book-7-giant-sea-creatures-are.html"),
    (23, "The Leviathan is Saying",            "https://www.kabbalahoftime.com/2016/03/the-leviathan-is-saying.html"),
    (24, "The Fish are Saying",                "https://www.kabbalahoftime.com/2016/03/the-fish-are-saying.html"),
    (25, "The Frog is Saying",                 "https://www.kabbalahoftime.com/2016/03/the-frog-is-saying-songs-for-week-25.html"),
    (26, "The Lamb is Saying",                 "https://www.kabbalahoftime.com/2016/04/the-lamb-is-saying-songs-for-week-26.html"),
    (27, "The Cow is Saying",                  "https://www.kabbalahoftime.com/2016/04/the-cow-is-saying-songs-for-week-27.html"),
    (28, "The Pig is Saying",                  "https://www.kabbalahoftime.com/2016/04/the-pig-is-saying-songs-for-week-28.html"),
    (29, "The Beast of Burden is Saying",      "https://www.kabbalahoftime.com/2016/04/the-beast-of-burden-is-saying-songs-for.html"),
    (30, "The Camel is Saying",                "https://www.kabbalahoftime.com/2016/04/the-camel-is-saying-songs-for-week-30.html"),
    (31, "The Horse is Saying",                "https://www.kabbalahoftime.com/2016/05/the-horse-is-saying-songs-for-week-31.html"),
    (32, "The Mule is Saying",                 "https://www.kabbalahoftime.com/2016/05/the-mule-is-saying.html"),
    (33, "The Donkey is Saying",               "https://www.kabbalahoftime.com/2016/05/the-donkey-is-saying-songs-for-week-33.html"),
    (34, "The Ox is Saying",                   "https://www.kabbalahoftime.com/2016/05/the-ox-is-saying-songs-for-week-34.html"),
    (35, "The Wild Animals Say",               "https://www.kabbalahoftime.com/2016/06/the-wild-animals-say-songs-for-week-35.html"),
    (36, "The Gazelle is Saying",              "https://www.kabbalahoftime.com/2017/06/the-gazelle-is-saying.html"),
    (37, "The Elephant is Saying",             "https://www.kabbalahoftime.com/2017/06/the-elephant-is-saying.html"),
    (38, "The Lion is Saying",                 "https://www.kabbalahoftime.com/2017/06/the-lion-is-saying.html"),
    (39, "The Bear is Saying",                 "https://www.kabbalahoftime.com/2017/06/week-39-bear-is-saying.html"),
    (40, "The Wolf is Saying",                 "https://www.kabbalahoftime.com/2016/07/the-wolf-is-saying.html"),
    (41, "The Fox is Saying",                  "https://www.kabbalahoftime.com/2017/07/the-fox-is-saying.html"),
    (42, "The Hound is Saying",                "https://www.kabbalahoftime.com/2017/07/the-hound-is-saying.html"),
    (43, "The Cat is Saying",                  "https://www.kabbalahoftime.com/2017/07/the-cat-is-saying.html"),
    (44, "The Mouse is Saying",                "https://www.kabbalahoftime.com/2017/07/the-mouse-is-saying.html"),
    (45, "The Creeping Creatures are Saying",  "https://www.kabbalahoftime.com/2020/08/week-45-creeping-creatures-are-saying.html"),
    (46, "The Prolific Creeping Creatures",    "https://www.kabbalahoftime.com/2013/08/week-46-book-7-prolific-creeping.html"),
    (47, "The Snake is Saying",                "https://www.kabbalahoftime.com/2013/03/week-47-book-7-snake-is-saying.html"),
    (48, "The Scorpion is Saying",             "https://www.kabbalahoftime.com/2017/08/the-scorpion-is-saying.html"),
    (49, "The Snail is Saying",                "https://www.kabbalahoftime.com/2026/05/week-49-book-7-snail-is-saying.html"),
    (50, "The Ant is Saying",                  "https://www.kabbalahoftime.com/2026/05/week-50-book-7-ant-is-saying.html"),
    (51, "The Weasel is Saying",               "https://www.kabbalahoftime.com/2021/08/week-51-book-7-wiesel-is-saying.html"),
    (52, "The Dogs are Saying",                "https://www.kabbalahoftime.com/2026/05/week-52-book-7-dogs-are-saying.html"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; KoT-PDF-builder/1.0)"
}

GOLD = colors.HexColor("#B8860B")
DARK = colors.HexColor("#1a1a1a")
RULE = colors.HexColor("#ccbbaa")


def fetch_post(url):
    """Fetch a Blogger post and return (post_title, paragraphs_list)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}")
        return None, []

    soup = BeautifulSoup(r.text, "html.parser")

    # Blogger post body selector
    body = (
        soup.find("div", class_="post-body")
        or soup.find("div", class_="entry-content")
        or soup.find("article")
    )
    if not body:
        print(f"  WARNING: no post body found for {url}")
        return None, []

    # Post title
    title_el = soup.find("h3", class_="post-title") or soup.find("h1", class_="post-title")
    title = title_el.get_text(strip=True) if title_el else None

    # Collect text blocks, preserving structure
    paras = []
    for el in body.find_all(["p", "h1", "h2", "h3", "h4", "blockquote", "div"], recursive=False):
        text = el.get_text(separator=" ", strip=True)
        if text:
            tag = el.name
            if tag in ("h1", "h2", "h3", "h4"):
                paras.append(("heading", text))
            elif tag == "blockquote":
                paras.append(("quote", text))
            else:
                paras.append(("body", text))

    # Fallback: if nothing found via direct children, get all text
    if not paras:
        raw = body.get_text(separator="\n", strip=True)
        for line in raw.split("\n"):
            line = line.strip()
            if line:
                paras.append(("body", line))

    return title, paras


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=1.1 * inch,
        rightMargin=1.1 * inch,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch,
        title="Kabbalah of Time — Book 7: The Gathering of Songs",
        author="www.kabbalahoftime.com",
    )

    styles = getSampleStyleSheet()

    # Custom styles
    cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=22,
        leading=28,
        textColor=GOLD,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    cover_sub = ParagraphStyle(
        "CoverSub",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=14,
        leading=18,
        textColor=DARK,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    cover_url = ParagraphStyle(
        "CoverUrl",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
    )
    week_header = ParagraphStyle(
        "WeekHeader",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=15,
        leading=20,
        textColor=GOLD,
        spaceAfter=2,
        spaceBefore=4,
    )
    post_title_style = ParagraphStyle(
        "PostTitle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#555555"),
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15,
        textColor=DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "SubHeading",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=11,
        leading=15,
        textColor=DARK,
        spaceBefore=6,
        spaceAfter=4,
    )
    quote_style = ParagraphStyle(
        "QuoteStyle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#333333"),
        leftIndent=24,
        rightIndent=24,
        spaceAfter=6,
    )
    url_style = ParagraphStyle(
        "UrlStyle",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#888888"),
        spaceAfter=4,
    )

    story = []

    # ── Cover page ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("Kabbalah of Time", cover_title))
    story.append(Paragraph("Book 7: The Gathering of Songs", cover_sub))
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="60%", thickness=1, color=GOLD, hAlign="CENTER"))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("52 Weeks · Perek Shirah", cover_sub))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("www.kabbalahoftime.com", cover_url))
    story.append(PageBreak())

    # ── Weeks ────────────────────────────────────────────────────────────────
    for week_num, theme, url in WEEKS:
        print(f"Fetching week {week_num:2d}: {theme} …")
        post_title, paras = fetch_post(url)
        time.sleep(0.4)  # polite crawl rate

        story.append(Paragraph(f"Week {week_num} — {theme}", week_header))
        story.append(HRFlowable(width="100%", thickness=0.5, color=RULE))
        story.append(Spacer(1, 4))

        if post_title and post_title.lower() != theme.lower():
            story.append(Paragraph(post_title, post_title_style))

        if not paras:
            story.append(Paragraph("(Content could not be retrieved — see original post.)", body_style))
        else:
            for kind, text in paras:
                # Escape XML special chars for ReportLab
                text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if kind == "heading":
                    story.append(Paragraph(text, heading_style))
                elif kind == "quote":
                    story.append(Paragraph(text, quote_style))
                else:
                    story.append(Paragraph(text, body_style))

        story.append(Spacer(1, 4))
        story.append(Paragraph(url, url_style))
        story.append(PageBreak())

    print("Building PDF …")
    doc.build(story)
    print(f"Done → {output_path}")


if __name__ == "__main__":
    build_pdf("/home/user/kabalahoftime/book7_gathering_of_songs.pdf")
