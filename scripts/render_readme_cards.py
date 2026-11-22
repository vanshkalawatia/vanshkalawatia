#!/usr/bin/env python3
"""
Render Vansh Kalawatia's profile README cards as animated SVGs into cards/.
Design system: Golden Ratio (phi = 1.618) with exact vertical rhythm and zero text collisions.
Cards:
- hero.svg (Golden section split: 544px Left / 336px Right)
- identity.svg (Tile 01: The Engineer, 3rd Year CSE)
- stack.svg (Tile 02: The Architecture, FastAPI & Python)
- mindset.svg (Tile 03: The Philosophy, Stoic Grit)
- whoami.svg (Spacious full-width card with zero overlapping text)
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

# Grid layout tokens matching AVIVASHISHTA29
W = 880                    # Full width

# Tri-Card tiles: width = 285.333 (880/3 - 8), height = 205 (generous vertical rhythm)
TILE_W = 285.333
TILE_H = 205

# Repo cards: width = 285.333, height = 176
REPO_W = 285.333
REPO_H = 176

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

# ---- 1 · GENERATE REFINED CAT ASCII (36 chars x 25 lines) ----
def get_cat_ascii_lines(target_w=36, target_h=25):
    if not os.path.exists(AVATAR_CLEAN):
        return []
    im = Image.open(AVATAR_CLEAN)
    resized = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    pix = list(resized.getdata())
    chars = "   ..::--==++**##%%@@"
    lines = []
    for r in range(target_h):
        row = ""
        for c in range(target_w):
            r_val, g_val, b_val, a_val = pix[r * target_w + c]
            if a_val < 100:
                row += " "
            else:
                gray = int(0.299 * r_val + 0.587 * g_val + 0.114 * b_val)
                idx = int((gray / 255.0) ** 0.85 * (len(chars) - 1))
                row += chars[idx]
        lines.append(row.rstrip())
    return lines

# ---- 2 · HERO CARD (Golden Section: 544px Left / 336px Right) -----------------
def hero():
    h = 420
    ascii_rows = get_cat_ascii_lines(36, 25)
    
    ascii_svg_lines = []
    base_x = 574
    base_y = 66
    line_h = 13.5
    for i, line_str in enumerate(ascii_rows):
        delay = 0.25 + i * 0.02
        color = "#ffffff" if (5 <= i <= 16) else "#c9d1d9"
        ascii_svg_lines.append(
            f'<text class="f" style="animation-delay:{delay:.2f}s" xml:space="preserve" '
            f'x="{base_x}" y="{base_y + i * line_h}" fill="{color}" font-family="{MONO}" '
            f'font-size="11" letter-spacing="1.2">{escape(line_str)}</text>'
        )

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

<!-- Left Column (0 - 544px) -->
<g class="f" {d(0)}>
  <rect class="live" x="48" y="46" width="8" height="8" rx="2" fill="{ACCENT}"/>
  <text x="66" y="54" font-family="{MONO}" font-size="11.5" letter-spacing="1.2" fill="{TEXT_MUTED}">PYTHON BACKEND ENGINEER · 3RD YEAR CSE · @despair0x00</text>
</g>

<text class="r" {d(0.15)} x="46" y="174" font-family="{SERIF}" font-size="92" letter-spacing="-2" fill="{TEXT_MAIN}">Vansh</text>
<text class="r" {d(0.3)} x="46" y="260" font-family="{SERIF}" font-style="italic" font-size="92" letter-spacing="-2" fill="url(#shine)">Kalawatia</text>

<g class="r" {d(0.55)}>
  {text_lines(48, 314, ["Specializing in high-throughput backends & async APIs.", "Targeting Summer 2027 Python Backend Internship."], 25, f'font-family="{SANS}" font-size="15.5" fill="{TEXT_SILVER}"')}
</g>

<g class="f" {d(0.8)}>
  <text x="48" y="388" font-family="{MONO}" font-size="12.5" fill="{TEXT_MAIN}">linkedin.com/in/vanshkalawatia</text>
  <text class="nu" x="282" y="388" font-family="{MONO}" font-size="12.5" fill="{ACCENT}">&#8599;</text>
</g>

<!-- Right Column (544 - 880px) -->
<g class="f" {d(0.2)}>
{''.join(ascii_svg_lines)}
</g>
"""
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                          "Vansh Kalawatia · despair0x00. Python Backend Engineer. Targeting Summer 2027 Internship."))

# ---- 3 · THREE IDENTITY TILES (ZERO COLLISION, 40px+ BREATHING ROOM) ---------
def identity_tile(name, tag, big_serif, italic_tail, blurb_lines, meta, delay, pos):
    # Generous vertical coordinates:
    # Tag: y = 34
    # Big Serif: y = 76
    # Blurb: y = 108 + i * 20 (line 0 = 108, line 1 = 128)
    # Meta: y = 180 (gap to line 1 is 52px!)
    blurb_svg = "".join(
        f'<text x="22" y="{108 + i * 20}" font-family="{SANS}" font-size="13" fill="{TEXT_SILVER}">{escape(l)}</text>'
        for i, l in enumerate(blurb_lines)
    )
    body = f"""
<rect width="{TILE_W}" height="{TILE_H}" rx="14" fill="{SURFACE}"/>
<rect x="0.75" y="0.75" width="{TILE_W - 1.5}" height="{TILE_H - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
<g class="r" {d(delay)}>
  <text x="22" y="34" font-family="{MONO}" font-size="11" letter-spacing="1.2" fill="{TEXT_MUTED}">{escape(tag)}</text>
  <text x="{TILE_W - 28}" y="34" font-family="{MONO}" font-size="12" fill="{ACCENT}">↗</text>
  <text x="20" y="76" font-family="{SERIF}" font-size="34" fill="{TEXT_MAIN}">{escape(big_serif)} <tspan font-style="italic" fill="{TEXT_SILVER}">{escape(italic_tail)}</tspan></text>
  {blurb_svg}
  <text x="22" y="180" font-family="{MONO}" font-size="11" fill="{TEXT_MUTED}">{escape(meta)}</text>
</g>
"""
    write(f"{name}.svg", svg(TILE_W, TILE_H, body, ["serif", "serif-i", "sans", "mono"],
                             f"{tag}: {big_serif} {italic_tail}. {' '.join(blurb_lines)}",
                             left=4 * pos, right=8 - 4 * pos))

# ---- 4 · FULL-WIDTH "WHO AM I" (Zero Overlap) ----------------------------------
def whoami():
    h = 320
    body = f"""
<defs>
  <pattern id="whoami_grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#21262d" stroke-width="0.5" opacity="0.35"/>
  </pattern>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{BG_MAIN}"/>
<rect width="{W}" height="{h}" rx="14" fill="url(#whoami_grid)"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>

<!-- Top Metadata Pill -->
<g class="f" {d(0.1)}>
  <rect class="live" x="48" y="36" width="7" height="7" rx="2" fill="{ACCENT}"/>
  <text x="64" y="43" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{TEXT_MUTED}">WHO I AM // IDENTITY, ARCHITECTURE &amp; MINDSET</text>
</g>

<!-- Big Editorial Title -->
<text class="r" {d(0.2)} x="46" y="86" font-family="{SERIF}" font-size="37" fill="{TEXT_MAIN}">The Engineer <tspan font-style="italic" fill="{TEXT_SILVER}">&amp; The Philosophy</tspan></text>

<!-- Golden Divider Line -->
<line x1="48" y1="108" x2="{W - 48}" y2="108" stroke="{BORDER}" stroke-width="1"/>

<!-- Background & Goal (Full width) -->
<g class="r" {d(0.35)}>
  <text x="48" y="142" font-family="{MONO}" font-size="11.5" letter-spacing="1.5" fill="#58a6ff">// 01 · BACKGROUND &amp; GOAL</text>
  <text x="48" y="172" font-family="{SANS}" font-size="14.5" fill="{TEXT_MAIN}">3rd-year B.Tech CSE undergrad in India targeting a <tspan font-weight="600" fill="#ffffff">Summer 2027</tspan> Python Backend Internship.</text>
  <text x="48" y="196" font-family="{SANS}" font-size="13.5" fill="{TEXT_MUTED}">Architecting high-throughput REST APIs, asynchronous worker pipelines, and scalable database systems.</text>
</g>

<!-- Stack & Mindset (Spacious separate bands) -->
<g class="r" {d(0.5)}>
  <text x="48" y="240" font-family="{MONO}" font-size="11.5" letter-spacing="1.5" fill="#c9d1d9">// 02 · ARCHITECTURE</text>
  <text x="48" y="268" font-family="{MONO}" font-size="12" fill="{TEXT_MAIN}">Python 3.12 · FastAPI · PostgreSQL · Redis · Docker · Linux</text>
</g>

<g class="r" {d(0.6)}>
  <text x="495" y="240" font-family="{MONO}" font-size="11.5" letter-spacing="1.5" fill="#7ee787">// 03 · THE MINDSET</text>
  <text x="495" y="268" font-family="{SERIF}" font-style="italic" font-size="18" fill="{TEXT_MAIN}">"Surpassing my limits... that's all I've ever known."</text>
  <text x="495" y="292" font-family="{MONO}" font-size="11" fill="{TEXT_MUTED}">— Vegeta / Guts (Berserk) · Methodical, disciplined grit</text>
</g>
"""
    write("whoami.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                            "Who Am I: Identity, Engineering, Background and Philosophy of Vansh Kalawatia."))

# ---- 5 · HEATMAP (Monochrome Manga Noir) ---------------------------------------
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

# ---- 6 · REPOSITORY CARDS ------------------------------------------------------
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

# ---- 7 · SECTION TITLES --------------------------------------------------------
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
    identity_tile("identity", "01 // THE ENGINEER", "3rd Year", "CSE",
                  ["Targeting Summer 2027 Python", "Backend Internship. Scalable async APIs."],
                  "India · @despair0x00", 0.35, 0)
    identity_tile("stack", "02 // ARCHITECTURE", "FastAPI", "& Python",
                  ["PostgreSQL, Redis & Docker pipelines.", "High-concurrency async microservices."],
                  "Async APIs · 99.9% Uptime", 0.45, 1)
    identity_tile("mindset", "03 // PHILOSOPHY", "Stoic", "Grit",
                  ["\"Surpassing my limits...\"", "Relentless consistency & stoic focus."],
                  "Vegeta · Guts (Berserk)", 0.55, 2)
    whoami()
    heatmap(data)
    for i, (name, desc, lang, color, meta_tag) in enumerate(REAL_REPOS):
        repo_card(i, name, desc, lang, color, meta_tag)
    section_title("Featured", "repositories", "dark")
    section_title("Featured", "repositories", "light")
    print("Done rendering all cards with clean vertical spacing!")
