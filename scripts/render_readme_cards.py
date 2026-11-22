#!/usr/bin/env python3
"""
Render Vansh Kalawatia's profile README cards as animated SVGs into cards/.
Theme: Monochrome Manga Noir with Multi-Color Chromatic ASCII Avatar.
Cards:
- hero.svg (Clean, bold, multi-color defined ASCII avatar: pink ear, blue scarf, white fur, dark sunglasses)
- about.svg (Spacious bullet-point developer card: easy to scan, generous line spacing)
- heatmap.svg (Contribution graph in monochrome ink)
- title-coding-dark.svg / title-coding-light.svg (Featured Repositories title)
- repo-Phase-1-First-Real-Tools.svg
- repo-Back-end-Roadmap.svg
- repo-DSA-Leetcode-Python.svg
"""

import base64
import datetime
import json
import os
import re
from html import escape
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")
AVATAR_CLEAN = os.path.join(ROOT, "assets", "avatar_clean.png")

# Monochrome Manga Noir Palette
BG_MAIN = "#0d1117"        # Obsidian Dark
SURFACE = "#161b22"        # Panel Dark
SURFACE_LGT = "#21262d"    # Raised surface
BORDER = "#30363d"         # Steel border
TEXT_MAIN = "#f0f6fc"      # Pure white
TEXT_MUTED = "#8b949e"     # Fog grey
TEXT_SILVER = "#c9d1d9"    # Chrome silver
ACCENT = "#ffffff"         # Crisp highlight
W = 880                    # Full width

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
@media (prefers-reduced-motion: reduce){.r,.f,.p,.live,.nu{animation:none!important;opacity:1!important;transform:none!important}}
"""

def font_face(keys):
    out = []
    for k in keys:
        if k in FONT_FILES:
            fam, style, weight, fn = FONT_FILES[k]
            fpath = os.path.join(FONTS, fn)
            if os.path.exists(fpath):
                b64 = base64.b64encode(open(fpath, "rb").read()).decode()
                out.append(
                    f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                    f"src:url(data:font/woff;base64,{b64}) format('woff');font-display:swap;}}"
                )
    return "".join(out)

BOTTOM = 12

def svg(w, h, body, fonts, label, extra_css="", left=0, right=0, bottom=BOTTOM):
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w_out, h_out = w + left + right, h + bottom
    css = font_face(fonts) + BASE_CSS + extra_css
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_out:.3f}" height="{h_out}" viewBox="0 0 {w_out:.3f} {h_out}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f"<style>{css}</style>{body}</svg>"
    )

def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote cards/{name} ({len(content) // 1024} KB)")

def d(s):
    return f'style="animation-delay:{s:.2f}s"'

def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines

def text_lines(x, y, lines, lh, attrs):
    return "".join(
        f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines)
    )

# ---- 1 · GENERATE CHROMATIC MULTI-COLOR ASCII FOR AVATAR ----
def classify_avatar_pixel(r, g, b, a, chars):
    if a < 100:
        return None, " "
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    idx = int((gray / 255.0) ** 0.85 * (len(chars) - 1))
    ch = chars[idx]
    if ch == " ":
        ch = "."
        
    # 1. Pink Inner Ear tint
    if r > 170 and g < 140 and b < 165:
        return "#ff7b72", ch
        
    # 2. Denim / Cyan Bandana Scarf
    if (b > r + 12 and b > 85) or (b > g + 8 and b > 100):
        return "#58a6ff", ch
        
    # 3. Coffee Mug Rim / Brown coffee liquid
    if (r > 135 and r > b + 15 and g > 85 and b < 165) or (r > 155 and g > 110 and b < 145):
        return "#d29922", ch
        
    # 4. Black Sunglasses & Deep Ink lines
    if r < 65 and g < 65 and b < 65:
        return "#484f58", "#" if gray < 40 else "="
        
    # 5. Crisp White Fur & Glints
    if gray > 180:
        return "#ffffff", ch
    elif gray > 120:
        return "#c9d1d9", ch
    else:
        return "#8b949e", ch

def get_chromatic_cat_ascii_lines(base_x=565, base_y=54, line_h=13.2, target_w=36, target_h=25):
    if not os.path.exists(AVATAR_CLEAN):
        return []
    im = Image.open(AVATAR_CLEAN)
    resized = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    pix = list(resized.getdata())
    chars = "   ..::--==++**##%%@@"
    
    svg_lines = []
    for y in range(target_h):
        delay = 0.25 + y * 0.02
        runs = []
        cur_color = None
        cur_text = ""
        for x in range(target_w):
            r, g, b, a = pix[y * target_w + x]
            color, ch = classify_avatar_pixel(r, g, b, a, chars)
            if color != cur_color:
                if cur_text:
                    runs.append((cur_color, cur_text))
                cur_color = color
                cur_text = ch
            else:
                cur_text += ch
        if cur_text:
            runs.append((cur_color, cur_text))
            
        tspans = []
        for color, text in runs:
            escaped = escape(text)
            if color is None or text.strip() == "":
                tspans.append(escaped)
            else:
                tspans.append(f'<tspan fill="{color}">{escaped}</tspan>')
                
        svg_lines.append(
            f'<text class="f" style="animation-delay:{delay:.2f}s" xml:space="preserve" '
            f'x="{base_x}" y="{base_y + y * line_h}" font-family="{MONO}" '
            f'font-size="11" letter-spacing="1.2">{"".join(tspans)}</text>'
        )
    return svg_lines

# ---- 2 · HERO CARD (Chromatic Defined ASCII, No Text Overlap) -----------------
def hero():
    h = 380
    ascii_svg_lines = get_chromatic_cat_ascii_lines(base_x=565, base_y=54, line_h=13.2, target_w=36, target_h=25)

    body = f"""
<defs>
  <pattern id="manga_dots" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#21262d" opacity="0.6"/>
  </pattern>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="480" y2="0">
    <stop offset="0" stop-color="{TEXT_MAIN}"/>
    <stop offset=".42" stop-color="{TEXT_MAIN}"/>
    <stop offset=".5" stop-color="#ffffff"/>
    <stop offset=".58" stop-color="{TEXT_SILVER}"/>
    <stop offset="1" stop-color="{TEXT_MAIN}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-480 0;480 0;480 0"
      keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{BG_MAIN}"/>
<rect width="{W}" height="{h}" rx="14" fill="url(#manga_dots)"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>

<!-- Left Column: Identity -->
<g class="f" {d(0)}>
  <rect class="live" x="48" y="46" width="8" height="8" rx="2" fill="{ACCENT}"/>
  <text x="66" y="54" font-family="{MONO}" font-size="11.5" letter-spacing="1.2" fill="{TEXT_MUTED}">BACKEND DEVELOPER · 3RD YEAR CSE · @despair0x00</text>
</g>

<!-- Big Bold Serif Name (Iconic & spacious) -->
<text class="r" {d(0.15)} x="46" y="174" font-family="{SERIF}" font-size="96" letter-spacing="-2" fill="{TEXT_MAIN}">Vansh</text>
<text class="r" {d(0.3)} x="46" y="264" font-family="{SERIF}" font-style="italic" font-size="96" letter-spacing="-2" fill="url(#shine)">Kalawatia</text>

<!-- Clean Footer Link -->
<g class="f" {d(0.55)}>
  <text x="48" y="336" font-family="{MONO}" font-size="13" fill="{TEXT_MAIN}">linkedin.com/in/vanshkalawatia</text>
  <text class="nu" x="290" y="336" font-family="{MONO}" font-size="13" fill="{ACCENT}">&#8599;</text>
</g>

<!-- Right Column: Chromatic Multi-Color ASCII Portrait -->
<g class="f" {d(0.2)}>
{''.join(ascii_svg_lines)}
</g>
"""
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                          "Vansh Kalawatia · despair0x00. Backend Developer · 3rd Year CSE."))

# ---- 3 · SPACIOUS BULLET-POINT "ABOUT ME" CARD (about.svg) --------------------
def about_me():
    h = 320
    points = [
        ("0.30", 146, "Background", "3rd-year B.Tech CSE student (India) · Targeting Summer 2027 Backend Internship"),
        ("0.40", 182, "Engineering", "Building scalable REST APIs, async worker pipelines & CLI tools in Python & FastAPI"),
        ("0.50", 218, "Tech Stack", "Python 3.12 · FastAPI · PostgreSQL · Redis · Docker · Linux · Git"),
        ("0.60", 254, "Algorithms", "Daily problem solving with Data Structures & Algorithms on LeetCode (Python)"),
        ("0.70", 290, "Handles", "GitHub: @vanshkalawatia · Secondary alias: @despair0x00"),
    ]
    
    point_svgs = []
    for delay, y, label, desc in points:
        point_svgs.append(
            f'<g class="r" {d(float(delay))}>'
            f'<text x="48" y="{y}" font-family="{MONO}" font-size="13" fill="#58a6ff">&#9657;</text>'
            f'<text x="68" y="{y}" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{TEXT_MUTED}">{escape(label.upper())}</text>'
            f'<text x="180" y="{y}" font-family="{MONO}" font-size="12" fill="{BORDER}">:</text>'
            f'<text x="198" y="{y}" font-family="{SANS}" font-size="14.5" fill="{TEXT_MAIN}">{escape(desc)}</text>'
            f'</g>'
        )

    body = f"""
<defs>
  <pattern id="about_grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#21262d" stroke-width="0.5" opacity="0.35"/>
  </pattern>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{BG_MAIN}"/>
<rect width="{W}" height="{h}" rx="14" fill="url(#about_grid)"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>

<!-- Top Metadata Pill -->
<g class="f" {d(0.1)}>
  <rect class="live" x="48" y="36" width="7" height="7" rx="2" fill="{ACCENT}"/>
  <text x="64" y="43" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{TEXT_MUTED}">ABOUT ME // WHO I AM &amp; WHAT I DO</text>
</g>

<!-- Big Editorial Title -->
<text class="r" {d(0.2)} x="46" y="86" font-family="{SERIF}" font-size="36" fill="{TEXT_MAIN}">Who I Am <tspan font-style="italic" fill="{TEXT_SILVER}">&amp; What I Do</tspan></text>

<!-- Divider Line -->
<line x1="48" y1="108" x2="{W - 48}" y2="108" stroke="{BORDER}" stroke-width="1"/>

<!-- Spacious Bullet Points (36px vertical stride) -->
{''.join(point_svgs)}
"""
    write("about.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                           "Who I Am & What I Do. Vansh Kalawatia - Backend Developer."))

# ---- 4 · HEATMAP (Monochrome Manga Noir) ---------------------------------------
NOIR_LEVELS = ["#161b22", "#2d333b", "#444c56", "#768390", "#adbac7", "#f0f6fc"]

def level_for(c):
    return 0 if c == 0 else 1 if c <= 3 else 2 if c <= 6 else 3 if c <= 10 else 4 if c <= 15 else 5

def heatmap(data):
    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7
    cell, step, gx, gy = 12, 15, 44, 96
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))
        c = day["count"]
        delay = 0.8 + col * 0.02 + row * 0.015
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="3" fill="{NOIR_LEVELS[level_for(c)]}">'
            f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>'
        )
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{TEXT_MUTED}">{m}</text>'
        for col, m in months if col < ncols - 8
    )
    legend_x = right - len(NOIR_LEVELS) * 14
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{gy + 7 * step + 6}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(NOIR_LEVELS)
    )
    h = gy + 7 * step + 44
    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{BG_MAIN}"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
<text class="r" {d(0.5)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{TEXT_MAIN}">Every day, <tspan font-style="italic" fill="{ACCENT}">in ink</tspan></text>
<text class="f" {d(0.5)} x="{right}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{TEXT_MUTED}">COMMITS &amp; CODE · REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(1.8)}>{labels}
<text x="{legend_x - 8}" y="{gy + 7 * step + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{TEXT_MUTED}">less</text>
{legend}
<text x="{legend_x + len(NOIR_LEVELS) * 14 + 2}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{TEXT_MUTED}">more</text></g>
"""
    write("heatmap.svg", svg(W, h, body, ["serif", "serif-i", "mono"],
                             f'Contribution graph in noir: {data["total_contributions"]:,} contributions in the last year'))

# ---- 5 · REPOSITORY CARDS ------------------------------------------------------
REPO_W, REPO_H = 285.333, 176

REAL_REPOS = [
    ("Phase-1-First-Real-Tools", "Production CLI tools with persistent storage, JSON, file I/O & API integration.", "Python", "#ffffff", "active"),
    ("Back-end-Roadmap", "Backend developer roadmap 2026: APIs, PostgreSQL, Redis, Docker & system design.", "System Design", "#c9d1d9", "active"),
    ("DSA-Leetcode-Python", "Algorithmic mastery, data structures & daily LeetCode interview patterns.", "Python", "#8b949e", "active"),
]

def repo_card(i, name, desc, lang, tag_color, meta_tag):
    delay = 1.6 + i * 0.12
    meta = f"{lang}  ·  {meta_tag}"
    body = f"""
<rect width="{REPO_W}" height="{REPO_H}" rx="14" fill="{SURFACE}"/>
<rect x="0.75" y="0.75" width="{REPO_W - 1.5}" height="{REPO_H - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
<g class="r" {d(delay)}>
  <rect x="22" y="30" width="8" height="8" rx="2" fill="{tag_color}"/>
  <text x="38" y="39" font-family="{SANS}" font-weight="600" font-size="15.5" fill="{TEXT_MAIN}">{escape(name)}</text>
  {text_lines(22, 72, wrap(desc, 32), 20, f'font-family="{SANS}" font-size="13" fill="{TEXT_SILVER}"')}
  <text x="22" y="{REPO_H - 22}" font-family="{MONO}" font-size="11" fill="{TEXT_MUTED}">{escape(meta)}</text>
  <text x="{REPO_W - 28}" y="{REPO_H - 22}" font-family="{MONO}" font-size="13" fill="{ACCENT}">↗</text>
</g>
"""
    write(f"repo-{name}.svg", svg(REPO_W, REPO_H, body, ["sans", "sans-b", "mono"], f"{name}: {desc}",
                                  left=4 * i, right=8 - 4 * i))

# ---- 6 · SECTION TITLES --------------------------------------------------------
def section_title(text, italic, theme):
    fg = TEXT_MAIN if theme == "dark" else "#111111"
    body = (
        f'<text class="r" {d(1.4)} x="2" y="46" font-family="{SERIF}" font-size="37" fill="{fg}">{escape(text)} '
        f'<tspan font-style="italic">{escape(italic)}</tspan></text>'
    )
    write(f"title-coding-{theme}.svg", svg(W, 64, body, ["serif", "serif-i"], f"{text} {italic}", bottom=0))

if __name__ == "__main__":
    data = json.load(open(DATA, "r", encoding="utf-8"))
    hero()
    about_me()
    heatmap(data)
    for i, (name, desc, lang, color, meta_tag) in enumerate(REAL_REPOS):
        repo_card(i, name, desc, lang, color, meta_tag)
    section_title("Featured", "repositories", "dark")
    section_title("Featured", "repositories", "light")
    print("Done rendering all cards with Chromatic ASCII Avatar!")
