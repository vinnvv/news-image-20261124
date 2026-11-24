#!/usr/bin/env python3
"""Render the World Daily Brief front page for Tuesday 24 November 2026.
Draws a 1024x1024 newspaper image with Pillow only. Deterministic: no
randomness, no timestamps, no network. Run: python3 render.py"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 26  # page margin

INK = (16, 16, 16)
PAPER = (253, 252, 248)
RED = (166, 30, 34)
DARKRED = (140, 22, 28)
GREEN = (47, 191, 113)
DEEPGREEN = (14, 59, 46)
DARKGREEN = (7, 35, 27)
NAVY = (11, 42, 74)
DARKNAVY = (10, 16, 48)
GOLD = (212, 175, 55)
MOONY = (245, 215, 110)
GREY = (68, 68, 68)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_size(draw, text, path, max_w, start):
    size = start
    while size > 8:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, 8)


def wrap(draw, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def center(draw, y, text, f, fill, x0=0, x1=W):
    w = draw.textlength(text, font=f)
    draw.text(((x0 + x1 - w) / 2, y), text, font=f, fill=fill)
    return y + f.size


def tag(draw, x, y, text, color):
    f = font(SANS_B, 15)
    w = draw.textlength(text, font=f) + 14
    draw.rectangle([x, y, x + w, y + 22], fill=color)
    draw.text((x + 7, y + 3), text, font=f, fill=(255, 255, 255))
    return w


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def flame(draw, cx, base_y, h, wdt):
    # two-tone flame: orange outer, yellow core
    draw.polygon([(cx - wdt, base_y), (cx - wdt * 0.55, base_y - h * 0.62),
                  (cx, base_y - h), (cx + wdt * 0.55, base_y - h * 0.62),
                  (cx + wdt, base_y)], fill=(232, 90, 20))
    draw.polygon([(cx - wdt * 0.5, base_y), (cx - wdt * 0.28, base_y - h * 0.45),
                  (cx, base_y - h * 0.68), (cx + wdt * 0.28, base_y - h * 0.45),
                  (cx + wdt * 0.5, base_y)], fill=(255, 196, 0))


def draw_hero_art(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=DEEPGREEN)
    # skyline silhouette along the bottom
    heights = [58, 96, 44, 120, 70, 140, 52, 108, 66, 88, 40, 116, 60, 92]
    bw = (x1 - x0) / len(heights)
    for i, hh in enumerate(heights):
        bx = x0 + i * bw
        d.rectangle([bx + 2, y1 - hh, bx + bw - 2, y1], fill=DARKGREEN)
        for wy in range(int(y1 - hh + 10), int(y1 - 8), 18):
            for wx in range(int(bx + 7), int(bx + bw - 7), 14):
                if (i * 7 + int(wy)) % 3 == 0:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 214, 90))
    # big rising green arrow, thick shaft + head
    ax0, ay0 = x0 + 48, y1 - 52
    ax1, ay1 = x1 - 70, y0 + 78
    dx, dy = ax1 - ax0, ay1 - ay0
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    px, py = -uy, ux
    t = 15
    d.polygon([(ax0 + px * t, ay0 + py * t), (ax1 + px * t, ay1 + py * t),
               (ax1 - px * t, ay1 - py * t), (ax0 - px * t, ay0 - py * t)],
              fill=GREEN)
    # arrow head
    hx, hy = ax1 + ux * 46, ay1 + uy * 46
    d.polygon([(hx, hy),
               (ax1 + px * 34 - ux * 26, ay1 + py * 34 - uy * 26),
               (ax1 - px * 34 - ux * 26, ay1 - py * 34 - uy * 26)],
              fill=GREEN)
    # three market dots along the arrow
    for f in (0.30, 0.58, 0.86):
        cx, cy = ax0 + dx * f, ay0 + dy * f
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255),
                  outline=GREEN, width=3)


def draw_hero_text(d, x0, y0, x1, y1):
    tag(d, x0, y0 + 4, "MARKETS  ·  ASIA", RED)
    f = fit_size(d, "ASIA STOCKS", SANS_B, x1 - x0, 46)
    d.text((x0, y0 + 34), "ASIA STOCKS", font=f, fill=INK)
    d.text((x0, y0 + 84), "SOAR", font=f, fill=INK)
    cap = "Taiwan +9.1%, Korea +7.5% and Japan +4.5% as the AI rally sweeps the region."
    cf = font(SANS, 19)
    yy = y0 + 146
    for ln in wrap(d, cap, cf, x1 - x0):
        d.text((x0, yy), ln, font=cf, fill=INK)
        yy += 24
    stats = [("TAIWAN", "+9.1%"), ("KOREA", "+7.5%"), ("JAPAN", "+4.5%")]
    yy = y1 - 84
    for name, val in stats:
        lf = font(SANS_B, 21)
        d.text((x0, yy), name, font=lf, fill=INK)
        vf = font(SANS_B, 27)
        vw = d.textlength(val, font=vf)
        d.text((x1 - vw, yy - 3), val, font=vf, fill=(18, 120, 62))
        yy += 30


def art_hormuz(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    d.rectangle([x0, y0 + 58, x1, y1], fill=(18, 68, 108))
    for i in range(9):
        wx = x0 + 12 + i * 36
        d.line([wx, y0 + 64, wx + 18, y0 + 64], fill=(140, 190, 230), width=2)
    # three tankers, middle one burning; hulls sit in the water band
    def tanker(bx, bw, bh, burning):
        hy = y0 + 88
        d.rectangle([bx, hy - bh, bx + bw, hy], fill=(38, 38, 44))
        d.rectangle([bx + bw - 26, hy - bh - 16, bx + bw - 8, hy - bh],
                    fill=(38, 38, 44))
        d.rectangle([bx + 8, hy - bh - 9, bx + 22, hy - bh], fill=(38, 38, 44))
        d.line([bx, hy - bh, bx + bw, hy - bh], fill=(180, 190, 200), width=2)
        d.line([bx, hy, bx + bw, hy], fill=(180, 190, 200), width=2)
        if burning:
            deck = hy - bh
            flame(d, bx + bw // 2, deck, 20, 13)
            for (sx, sy, sr) in [(bx + bw // 2 - 14, deck - 26, 7),
                                 (bx + bw // 2 + 4, deck - 36, 9),
                                 (bx + bw // 2 + 16, deck - 44, 6)]:
                d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                          fill=(120, 120, 120))
    tanker(x0 + 12, 92, 26, False)
    tanker(x0 + 112, 100, 26, True)
    tanker(x0 + 222, 84, 24, False)
    # spiky sea mine in the open water at bottom-right, inside the box
    mx, my = x0 + 298, y0 + 91
    for a in range(8):
        ang = a * math.pi / 4
        d.line([mx + 7 * math.cos(ang), my + 7 * math.sin(ang),
                mx + 14 * math.cos(ang), my + 14 * math.sin(ang)],
               fill=(200, 200, 200), width=3)
    d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(30, 30, 34),
              outline=(200, 200, 200), width=2)


def art_moon(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=DARKNAVY)
    for (sx, sy, sr) in [(x0 + 30, y0 + 18, 2), (x0 + 90, y0 + 10, 2),
                         (x0 + 250, y0 + 22, 2), (x0 + 290, y0 + 44, 2),
                         (x0 + 60, y0 + 52, 1), (x0 + 210, y0 + 58, 1)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255))
    cx, cy, r = x0 + 118, y0 + 52, 38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MOONY)
    for (ox, oy, orr) in [(cx - 14, cy - 8, 7), (cx + 12, cy + 6, 9),
                          (cx + 4, cy - 18, 5), (cx - 4, cy + 16, 6)]:
        d.ellipse([ox - orr, oy - orr, ox + orr, oy + orr],
                  fill=(226, 190, 84))
    # tree + observatory silhouettes
    d.rectangle([x0 + 238, y0 + 66, x0 + 244, y1], fill=(4, 8, 20))
    d.polygon([(x0 + 214, y0 + 70), (x0 + 268, y0 + 70),
               (x0 + 241, y0 + 30)], fill=(4, 8, 20))
    d.pieslice([x0 + 262, y1 - 24, x0 + 306, y1], 180, 360,
               fill=(4, 8, 20))
    d.rectangle([x0 + 282, y1 - 26, x0 + 286, y1 - 12], fill=MOONY)


def art_tennis(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(46, 125, 50))
    d.rectangle([x0, y0, x1, y0 + 34], fill=(120, 120, 120))
    for i in range(10):
        d.ellipse([x0 + 16 + i * 30, y0 + 12, x0 + 24 + i * 30, y0 + 20],
                  fill=(70, 70, 70))
    d.line([x0, y0 + 78, x1, y0 + 78], fill=(255, 255, 255), width=4)
    d.line([x0 + 40, y0 + 34, x0 + 40, y1], fill=(255, 255, 255), width=3)
    d.line([x0 + 278, y0 + 34, x0 + 278, y1], fill=(255, 255, 255), width=3)
    cx, cy, r = x0 + 159, y0 + 62, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(216, 230, 74),
              outline=(255, 255, 255), width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=(255, 255, 255),
          width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 120, 240, fill=(255, 255, 255),
          width=3)


def art_krathong(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(6, 47, 51))
    d.ellipse([x0 + 252, y0 + 10, x0 + 292, y0 + 50], fill=(240, 230, 200))
    for yy in range(y0 + 58, y1, 12):
        d.line([x0, yy, x1, yy], fill=(16, 90, 96), width=2)
    # krathong: leaf boat with flowers and a candle flame
    bx, by = x0 + 159, y0 + 62
    d.polygon([(bx - 78, by), (bx - 58, by + 16), (bx + 58, by + 16),
               (bx + 78, by)], fill=(34, 110, 44))
    d.polygon([(bx - 78, by), (bx - 58, by + 16), (bx + 58, by + 16),
               (bx + 78, by)], outline=(120, 200, 90), width=2)
    for (fx, fc) in [(-52, (232, 90, 140)), (-28, (255, 196, 0)),
                     (28, (232, 90, 140)), (52, (255, 120, 160))]:
        d.ellipse([bx + fx - 8, by - 8, bx + fx + 8, by + 8], fill=fc)
    d.rectangle([bx - 2, by - 22, bx + 2, by - 4], fill=(240, 220, 180))
    flame(d, bx, by - 20, 26, 10)
    # glow + reflection
    d.ellipse([bx - 46, by + 18, bx + 46, by + 30], fill=(255, 170, 40))
    d.rectangle([bx - 3, by + 30, bx + 3, y1 - 4], fill=(200, 120, 30))


def art_eu(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(31, 56, 100))
    cx, cy, rr = x0 + 80, y0 + 42, 32
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        star(d, cx + rr * math.cos(ang), cy + rr * math.sin(ang), 7, GOLD)
    # ballot box, upper right
    d.rectangle([x0 + 196, y0 + 18, x0 + 292, y0 + 64], fill=(245, 245, 245))
    d.rectangle([x0 + 196, y0 + 18, x0 + 292, y0 + 32], fill=(200, 200, 200))
    d.rectangle([x0 + 226, y0 + 23, x0 + 262, y0 + 27], fill=(40, 40, 40))
    # euro figure, centred along the bottom of the panel
    bf = fit_size(d, "€199.7B", SANS_B, x1 - x0 - 16, 27)
    center(d, y0 + 70, "€199.7B", bf, (255, 255, 255), x0, x1)


def art_rocket(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=DARKNAVY)
    for (sx, sy, sr) in [(x0 + 24, y0 + 14, 2), (x0 + 70, y0 + 30, 1),
                         (x0 + 260, y0 + 12, 2), (x0 + 296, y0 + 40, 2),
                         (x0 + 120, y0 + 10, 1), (x0 + 200, y0 + 66, 1)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255))
    # satellite dots trailing the rocket
    for (sx, sy) in [(x0 + 250, y0 + 22), (x0 + 272, y0 + 34),
                     (x0 + 292, y0 + 18), (x0 + 232, y0 + 40)]:
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=GOLD)
        d.rectangle([sx - 7, sy - 1, sx - 3, sy + 1], fill=GOLD)
        d.rectangle([sx + 3, sy - 1, sx + 7, sy + 1], fill=GOLD)
    # rocket body, tilted 25 degrees, nose up-right
    cx, cy = x0 + 130, y0 + 62
    ang = math.radians(-25)
    ca, sa = math.cos(ang), math.sin(ang)

    def rot(px, py):
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)
    body = [rot(-52, -9), rot(28, -9), rot(52, 0), rot(28, 9), rot(-52, 9)]
    d.polygon(body, fill=(245, 245, 245))
    nose = [rot(28, -9), rot(52, 0), rot(28, 9)]
    d.polygon(nose, fill=(31, 56, 100))
    d.polygon([rot(-52, -9), rot(-34, -9), rot(-34, 9), rot(-52, 9)],
              fill=(200, 60, 40))
    tip = rot(-52, 0)
    flame(d, int(tip[0] - 14), int(tip[1] + 16), 30, 12)
    d.rectangle([x0, y1 - 8, x1, y1], fill=(20, 60, 40))


def draw_cell(d, x0, y0, x1, y1, art, tag_text, tag_color, headline,
              caption):
    art(d, x0, y0, x1, y0 + 100)
    tag(d, x0, y0 + 108, tag_text, tag_color)
    hf = font(SANS_B, 24)
    yy = y0 + 136
    for ln in wrap(d, headline, hf, x1 - x0):
        d.text((x0, yy), ln, font=hf, fill=INK)
        yy += 27
    cf = font(SANS, 16)
    yy += 2
    for ln in wrap(d, caption, cf, x1 - x0):
        d.text((x0, yy), ln, font=cf, fill=(30, 30, 30))
        yy += 20


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # masthead
    mf = font(SERIF_B, 78)
    center(d, 16, "THE WORLD", mf, INK)
    d.rectangle([M, 100, W - M, 160], fill=RED)
    df = fit_size(d, "TUESDAY 24 NOVEMBER 2026", SANS_B, W - 2 * M - 24, 54)
    center(d, 112, "TUESDAY 24 NOVEMBER 2026", df, (255, 255, 255))
    d.line([M, 168, W - M, 168], fill=INK, width=2)
    # editor's note strip (diegetic: date + breadth + readability)
    note = ("Editor's note: Seven stories from around the world, all reported "
            "on Tuesday 24 November 2026, each drawn to read at a glance.")
    nf = fit_size(d, note, SERIF_I, W - 2 * M, 19)
    center(d, 176, note, nf, GREY)
    d.line([M, 200, W - M, 200], fill=INK, width=1)
    # hero
    draw_hero_art(d, M, 208, 612, 508)
    draw_hero_text(d, 628, 208, W - M, 508)
    d.line([M, 520, W - M, 520], fill=INK, width=2)
    # supporting grid: 2 rows x 3 columns
    cols = [(M, 344), (356, 674), (686, W - M)]
    rows = [(532, 758), (770, 996)]
    cells = [
        (art_hormuz, "ENERGY  ·  MIDDLE EAST", RED,
         "TANKERS HIT MINES",
         "IRGC says three tankers caught fire in the Strait of Hormuz."),
        (art_moon, "SPACE  ·  WORLD", NAVY,
         "BEAVER SUPERMOON",
         "Full moon peaks at 14:53 UTC, first of four supermoons."),
        (art_tennis, "SPORT  ·  EUROPE", (18, 120, 62),
         "DAVIS CUP OPENS",
         "Final 8 begins in Bologna: Czechia v Canada, 16:00 CET."),
        (art_krathong, "CULTURE  ·  THAILAND", (120, 60, 140),
         "LIGHTS ON THE WATER",
         "Thailand floats krathong on the full-moon night."),
        (art_eu, "POLITICS  ·  EUROPE", (31, 56, 100),
         "EU BUDGET DEBATE",
         "MEPs debate the €199.7bn 2027 budget; vote due Wednesday."),
        (art_rocket, "SPACE  ·  AMERICAS", DARKNAVY,
         "ARIANE 6 READY",
         "36 Amazon Leo satellites due up from Kourou today."),
    ]
    for i, (art, tg, tc, hl, cp) in enumerate(cells):
        x0, x1 = cols[i % 3]
        y0, y1 = rows[i // 3]
        draw_cell(d, x0, y0, x1, y1, art, tg, tc, hl, cp)
    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
