#!/usr/bin/env python3
"""Render a one-page visual summary of Friday 20 November 2026.

The canvas is a broadsheet front page: a heavy masthead that names the
date in full, one dominant lead panel for Russia's overnight barrage
of Kyiv, and seven smaller panels covering the Gulf, Washington,
markets, climate, European borders, tech and the EU-UK summit.
Everything is drawn with Pillow primitives only -- no photographs
and no external image assets.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (18, 18, 20)
MUTED = (92, 88, 80)
RULE = (18, 18, 20)
RED = (178, 34, 40)
BLUE = (28, 74, 140)
TEAL = (14, 116, 110)
GOLD = (196, 138, 18)
GREEN = (38, 110, 52)
PURPLE = (94, 52, 140)
ORANGE = (214, 96, 20)
PANEL = (255, 254, 248)
PANEL_ALT = (238, 233, 218)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SANS_B = str(FONT_DIR / "DejaVuSans-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, font, fill, max_w, leading=4):
    for line in wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + leading
    return y


def panel(draw, box, accent):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=PANEL, outline=INK, width=2)
    draw.rectangle([x0, y0, x1, y0 + 7], fill=accent)


def headline(draw, x, y, text, size, max_w, fill=INK):
    return text_block(draw, x, y, text, f(SANS_B, size), fill, max_w, leading=2)


def subline(draw, x, y, text, size, max_w):
    return text_block(draw, x, y, text, f(SANS, size), MUTED, max_w, leading=3)


def kicker(draw, x, y, text, colour):
    draw.text((x, y), text, font=f(SANS_B, 15), fill=colour)
    return y + 21


# ---------------------------------------------------------------- icons
def icon_blast(draw, cx, cy):
    """Explosion burst over a city skyline."""
    for dx, w in ((-44, 34), (-14, 40), (20, 36)):
        draw.rectangle([cx + dx, cy + 6, cx + dx + w, cy + 26], fill=INK)
    draw.rectangle([cx - 52, cy + 26, cx + 52, cy + 30], fill=INK, width=2)
    # burst star
    pts = []
    for i in range(12):
        r = 34 if i % 2 == 0 else 16
        import math
        a = math.pi * i / 6
        pts.append((cx + r * math.cos(a), cy - 6 + r * math.sin(a)))
    draw.polygon(pts, fill=ORANGE)
    draw.ellipse([cx - 9, cy - 15, cx + 9, cy + 3], fill=RED)


def icon_tower(draw, cx, cy):
    """A tall skyscraper with a missile scar across its top floors."""
    draw.rectangle([cx - 22, cy - 34, cx + 22, cy + 30], fill=BLUE)
    for row in range(4):
        for col in range(3):
            x = cx - 16 + col * 12
            y = cy - 26 + row * 14
            draw.rectangle([x, y, x + 7, y + 8], fill=(255, 255, 255))
    # broken windows on the top two floors
    for x in (cx - 16, cx - 4, cx + 8):
        draw.rectangle([x, cy - 26, x + 7, cy - 18], fill=INK)
    draw.line([cx - 30, cy - 40, cx + 30, cy - 22], fill=RED, width=5)
    draw.polygon([(cx + 26, cy - 44), (cx + 38, cy - 26), (cx + 28, cy - 20)],
                 fill=RED)


def icon_hourglass(draw, cx, cy):
    draw.polygon([(cx - 22, cy - 28), (cx + 22, cy - 28), (cx, cy)],
                 outline=INK, width=3)
    draw.polygon([(cx - 22, cy + 28), (cx + 22, cy + 28), (cx, cy)],
                 outline=INK, width=3)
    draw.rectangle([cx - 26, cy - 32, cx + 26, cy - 28], fill=INK)
    draw.rectangle([cx - 26, cy + 28, cx + 26, cy + 32], fill=INK)
    draw.polygon([(cx - 10, cy + 6), (cx + 10, cy + 6), (cx + 5, cy + 24),
                  (cx - 5, cy + 24)], fill=GOLD)


def icon_chart_down(draw, cx, cy):
    draw.line([cx - 38, cy + 28, cx + 40, cy + 28], fill=INK, width=3)
    draw.line([cx - 38, cy + 28, cx - 38, cy - 28], fill=INK, width=3)
    pts = [(cx - 32, cy - 18), (cx - 12, cy - 4), (cx + 6, cy - 10),
           (cx + 30, cy + 18)]
    draw.line(pts, fill=RED, width=5)
    draw.polygon([(cx + 30, cy + 18), (cx + 18, cy + 14), (cx + 26, cy + 4)],
                 fill=RED)
    draw.text((cx - 34, cy - 34), "-4.8%", font=f(SANS_B, 15), fill=RED)


def icon_draft(draw, cx, cy):
    draw.rectangle([cx - 26, cy - 30, cx + 26, cy + 30], fill=(255, 255, 255),
                   outline=INK, width=3)
    for i, y in enumerate((-16, -4, 8)):
        draw.line([cx - 18, cy + y, cx + 18, cy + y], fill=MUTED, width=2)
    # crossed-out leaf
    draw.ellipse([cx - 8, cy + 14, cx + 8, cy + 26], fill=GREEN)
    draw.line([cx - 12, cy + 10, cx + 12, cy + 30], fill=RED, width=4)
    draw.line([cx + 12, cy + 10, cx - 12, cy + 30], fill=RED, width=4)


def icon_border(draw, cx, cy):
    """A fence line with a closed gate and a flag."""
    for x in range(cx - 44, cx + 45, 11):
        draw.line([x, cy - 20, x, cy + 28], fill=INK, width=3)
    draw.line([cx - 48, cy - 14, cx + 48, cy - 14], fill=INK, width=3)
    draw.line([cx - 48, cy + 10, cx + 48, cy + 10], fill=INK, width=3)
    draw.line([cx, cy - 34, cx, cy + 28], fill=INK, width=3)
    draw.rectangle([cx, cy - 34, cx + 22, cy - 20], fill=BLUE)
    draw.text((cx + 4, cy - 33), "EU", font=f(SANS_B, 10), fill=(255, 255, 255))


def icon_cyber(draw, cx, cy):
    """A shield crossed out, with a plug below."""
    draw.polygon([(cx, cy - 30), (cx + 26, cy - 18), (cx + 26, cy + 4),
                  (cx, cy + 28), (cx - 26, cy + 4), (cx - 26, cy - 18)],
                 outline=INK, width=3)
    draw.line([cx - 16, cy - 16, cx + 16, cy + 14], fill=RED, width=4)
    draw.line([cx + 16, cy - 16, cx - 16, cy + 14], fill=RED, width=4)
    draw.rectangle([cx - 8, cy + 34, cx + 8, cy + 40], fill=INK)


def icon_flags(draw, cx, cy):
    """EU and UK flags on two poles over a table line."""
    draw.line([cx - 34, cy - 26, cx - 34, cy + 24], fill=INK, width=3)
    draw.line([cx + 14, cy - 26, cx + 14, cy + 24], fill=INK, width=3)
    draw.rectangle([cx - 34, cy - 26, cx - 14, cy - 12], fill=BLUE)
    for dx, dy in ((-29, -22), (-24, -16), (-19, -22)):
        draw.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                     fill=(255, 220, 60))
    draw.rectangle([cx + 14, cy - 26, cx + 34, cy - 12], fill=(255, 255, 255),
                   outline=INK, width=2)
    draw.line([cx + 14, cy - 19, cx + 34, cy - 19], fill=RED, width=3)
    draw.line([cx + 24, cy - 26, cx + 24, cy - 12], fill=RED, width=3)
    draw.line([cx - 52, cy + 24, cx + 52, cy + 24], fill=INK, width=4)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 148], fill=INK)
    d.text((36, 14), "THE WORLD IN ONE IMAGE  ·  GLOBAL FRONT PAGE",
           font=f(SANS_B, 19), fill=(240, 220, 150))
    d.text((34, 40), "FRIDAY", font=f(SERIF_B, 54), fill=(255, 255, 255))
    d.text((34, 98), "20 NOVEMBER 2026", font=f(SERIF_B, 40), fill=(255, 96, 96))
    d.text((700, 52), "ONE DAY.", font=f(SERIF_B, 30), fill=(255, 255, 255))
    d.text((700, 88), "EIGHT STORIES.", font=f(SERIF_B, 30), fill=(255, 255, 255))
    d.rectangle([0, 148, W, 156], fill=RED)

    # Lead story: Kyiv barrage --------------------------------------
    panel(d, [24, 168, 636, 452], RED)
    y = kicker(d, 44, 182, "LEAD  ·  KYIV, UKRAINE  ·  WAR", RED)
    y = headline(d, 44, y, "RUSSIA'S KYIV BARRAGE KILLS 8", 31, 470)
    y = subline(d, 44, y + 4,
                "Over 400 drones and 110 missiles hit the capital; "
                "embassies and a cathedral damaged.", 17, 470)
    icon_blast(d, 556, 250)
    # three toll chips fill the lead panel and name the scale
    for i, chip in enumerate(("400+ DRONES", "110+ MISSILES", "8 KILLED")):
        cx0 = 44 + i * 190
        d.rectangle([cx0, 352, cx0 + 178, 388], fill=PANEL_ALT, outline=INK, width=2)
        d.text((cx0 + 10, 362), chip, font=f(SANS_B, 15), fill=INK)
    d.text((44, 408), "RUSSIA HITS BACK AFTER CRIMEA BRIDGE ATTACKS",
           font=f(SANS_B, 14), fill=MUTED)

    # Houthi Riyadh --------------------------------------------------
    panel(d, [652, 168, 1000, 306], ORANGE)
    y = kicker(d, 670, 180, "MIDDLE EAST  ·  RIYADH", ORANGE)
    y = headline(d, 670, y, "HOUTHI MISSILE HITS RIYADH SKYSCRAPER", 19, 205)
    subline(d, 670, y + 2, "Windows blown out on eight floors of the PIF tower.", 14, 205)
    icon_tower(d, 940, 248)

    # Trump / Iran ---------------------------------------------------
    panel(d, [652, 318, 1000, 452], BLUE)
    y = kicker(d, 670, 330, "WASHINGTON  ·  IRAN WAR", BLUE)
    y = headline(d, 670, y, "TRUMP: NO IRAN DECISION UNTIL 2027", 19, 205)
    subline(d, 670, y + 2, "Senate blocks war-powers measure 51-48.", 14, 205)
    icon_hourglass(d, 940, 398)

    # Markets --------------------------------------------------------
    panel(d, [24, 464, 336, 686], GREEN)
    y = kicker(d, 42, 478, "MARKETS  ·  TOKYO & NEW YORK", GREEN)
    y = headline(d, 42, y, "AI SELL-OFF: NIKKEI -4.8%, KOSPI -4.7%", 22, 272)
    y = subline(d, 42, y + 3,
                "S&P 500 falls 2%, its fifth straight loss, a day after "
                "Anthropic's record IPO.", 16, 272)
    icon_chart_down(d, 180, 640)

    # COP31 ----------------------------------------------------------
    panel(d, [348, 464, 660, 686], TEAL)
    y = kicker(d, 366, 478, "CLIMATE  ·  COP31, ANTALYA", TEAL)
    y = headline(d, 366, y, "COP31 DRAFT DROPS FOSSIL-FUEL PHASE-OUT", 22, 272)
    y = subline(d, 366, y + 3,
                "Talks go into overtime as nations quarrel over fuels.", 16, 190)
    icon_draft(d, 592, 606)

    # Estonia / Poland -----------------------------------------------
    panel(d, [672, 464, 1000, 686], RED)
    y = kicker(d, 690, 478, "EUROPE  ·  BORDERS", RED)
    y = headline(d, 690, y, "ESTONIA TO SHUT RUSSIA BORDER FOR 6 MONTHS", 22, 272)
    y = subline(d, 690, y + 3,
                "Russia violates Poland's airspace with three objects.", 16, 272)
    icon_border(d, 836, 650)

    # White House cyber chief ----------------------------------------
    panel(d, [24, 698, 500, 918], PURPLE)
    y = kicker(d, 42, 712, "WASHINGTON  ·  TECH", PURPLE)
    y = headline(d, 42, y, "WHITE HOUSE FIRES CYBER CHIEF", 22, 330)
    y = subline(d, 42, y + 3,
                "Sean Cairncross dismissed after a week of tech outages.", 16, 330)
    icon_cyber(d, 424, 838)

    # EU-UK summit ---------------------------------------------------
    panel(d, [512, 698, 1000, 918], GOLD)
    y = kicker(d, 530, 712, "EUROPE  ·  BRUSSELS", GOLD)
    y = headline(d, 530, y, "EU AND UK SEAL FOOD AND YOUTH DEALS", 24, 330)
    y = subline(d, 530, y + 3,
                "Second Brussels summit deepens the renewed partnership.", 16, 330)
    icon_flags(d, 918, 838)

    # Footer ---------------------------------------------------------
    d.rectangle([0, 932, W, 1024], fill=INK)
    d.text((36, 946), "FRIDAY 20 NOVEMBER 2026 -- THE DAY IN ONE IMAGE",
           font=f(SANS_B, 20), fill=(255, 255, 255))
    d.text((36, 976),
           "Kyiv barrage  ·  Riyadh missile  ·  Iran decision delayed  ·  "
           "AI sell-off  ·  COP31  ·  Borders  ·  Cyber chief  ·  EU-UK",
           font=f(SANS, 16), fill=(220, 214, 195))
    return img


if __name__ == "__main__":
    out = Path(__file__).with_name("entry.png")
    build().save(out, format="PNG", optimize=True)
    print(out, out.stat().st_size)
