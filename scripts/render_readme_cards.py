#!/usr/bin/env python3
"""
Render Vansh Kalawatia's profile README cards as animated SVGs into cards/.
Theme: Monochrome Manga Noir (Johan Liebert / Monster / Berserk psychological aesthetic).
Cards:
- hero.svg (With animated ASCII profile portrait on the right)
- whoami.svg (Dedicated Who Am I: Identity, Engineering, Anime Mindset)
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

# Monochrome Manga Noir Palette
BG_MAIN = "#0d1117"        # Obsidian Dark
SURFACE = "#161b22"        # Panel Dark
SURFACE_LGT = "#21262d"    # Raised surface
BORDER = "#30363d"         # Steel border
TEXT_MAIN = "#f0f6fc"      # Pure white
TEXT_MUTED = "#8b949e"     # Fog grey
TEXT_SILVER = "#c9d1d9"    # Chrome silver
ACCENT = "#ffffff"         # Crisp highlight
W = 880                    # Full card width

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

# ---- 1 · ASCII PORTRAIT GENERATOR (For Hero Card) ----
def generate_hero_ascii_portrait():
    tw, th = 820, 840
    # Detailed manga noir anime portrait in shaded ASCII
    ascii_lines = [
        "                 .:::::.                ",
        "              .:::::::::::.             ",
        "            .::::::::::::::::.          ",
        "           ::::::::::::::::::::         ",
        "          ::::::::::::::::::::::        ",
        "         :::\"\"'  '\"\"\"\"\"\"'  '\"\":::       ",
        "        ::'  .::.          .::.  '::    ",
        "       ::   ::::::        ::::::   ::   ",
        "      ::   '::::::        ::::::'   ::  ",
        "     :::    '::::'        '::::'    ::: ",
        "     :::                            ::: ",
        "     :::         ..      ..         ::: ",
        "     '::.       '::.    .::'       .::' ",
        "      '::.        '::::::'        .::'  ",
        "        '::.                    .::'    ",
        "          '::.   .--------.   .::'      ",
        "            '::.  '::::::'  .::'        ",
        "             :::'          ':::         ",
        "          .::::::::::::::::::::::.      ",
        "       .::::::::::::::::::::::::::::.   ",
        "     .::::::::::::::::::::::::::::::::. ",
        "    ::::::::::::::::::::::::::::::::::::",
        "   ::::::::::::::::::::::::::::::::::::::",
        "  ::::::::::::::::::::::::::::::::::::::::",
        "  ::::::::::::::::::::::::::::::::::::::::",
        "  ::'  ::::::::::::::::::::::::::::::  '::",
        "       '::::::::::::::::::::::::::::'   ",
        "        '::::::::::::::::::::::::::'    ",
        "         '::::::::::::::::::::::::'     ",
        "          '::::::::::::::::::::::'      "
    ]
    
    # Atmospheric manga noir ASCII rendering
    # We create a richer anime-aesthetic portrait with hair layers and intense stare
    rich_ascii = [
        "                     .---.                      ",
        "                   ./:::::\\.                    ",
        "                 ./:::::::::\\.                  ",
        "                /:::::::::::::\\                 ",
        "               /:::::__:::__:::\\                ",
        "              |:::::/  \\ /  \\:::|               ",
        "              |::::| () | () |::|               ",
        "              |:::::\\__/ \\__/:::|               ",
        "              |::::::   _   ::::|   [STATION: NOIR]",
        "              |::::::  / \\  ::::|   [ID: despair0x00]",
        "               \\:::::  \\_/  :::/    [ROLE: BACKEND DEV]",
        "                \\::::.     .::/                 ",
        "                 '\\:::=====::/'                 ",
        "                 .---|     |---.                ",
        "               /     \\     /     \\              ",
        "              |   .---'   '---.   |             ",
        "              |  /   G U T S   \\  |             ",
        "              | /   M I N D     \\ |             ",
        "              |/    S E T        \\|             ",
        "              /                   \\             ",
        "             |   .-------------.   |            ",
        "             |  /  PYTHON 3.12  \\  |            ",
        "             | /    FASTAPI      \\ |            ",
        "             |/     POSTGRES      \\|            ",
        "             '---------------------'            "
    ]

    # Let's craft an authentic high-resolution terminal ascii portrait of Vansh (despair0x00):
    ascii_portrait = [
        "                        .---.",
        "                      /       \\",
        "                     |  O   O  |       // despair0x00",
        "                 ---. \\   ^   / .---   // Python Backend",
        "                /    '. '---' .'    \\  // 3rd Year CSE",
        "               /   /\\  '-----'  /\\   \\",
        "              /   /  \\         /  \\   \\",
        "             /   /    |       |    \\   \\",
        "            /___/     |_______|     \\___\\",
        "             | |      |       |      | |",
        "             | |      |   *   |      | |",
        "             | |      |_______|      | |",
        "            /   \\     |       |     /   \\",
        "           |     |    |_______|    |     |",
        "           |_____|                 |_____|"
    ]

    # High fidelity stylized character matrix
    matrix_art = [
        "                _.._                   ",
        "              .' .-'`                  ",
        "             /  /                      ",
        "            |  |      .---.            ",
        "            |  |     /  .  \\   [AURA]  ",
        "             \\  \\   |  /|\\  |  GUTS    ",
        "              '._'--'  \\|/  /  JOHAN   ",
        "                 `---.     <   VEGETA  ",
        "                     |  _   \\          ",
        "                     | (_)  |          ",
        "                     \\      /          ",
        "                      `'--'`           ",
        "                 .---.     .---.       ",
        "                /     \\___/     \\      ",
        "               |  ===  ___  ===  |     ",
        "               |      [___]      |     ",
        "               |   PYTHON  CORE  |     ",
        "               |   FASTAPI ASYNC |     ",
        "                \\_______________/      "
    ]

    # We will format this into a gorgeous manga console panel
    terminal_header = [
        ("0.20", "┌──────────────────────────────────────────────┐"),
        ("0.25", "│  AVATAR SPECIFICATION // DESPAIR0X00         │"),
        ("0.30", "├──────────────────────────────────────────────┤"),
    ]

    # Clean, crisp pixel-aligned ASCII silhouette
    lines_art = [
        "│           .-----------------------.          │",
        "│          /  .-------------------.  \\         │",
        "│         |  /                     \\  |        │",
        "│         | |   _..._       _..._   | |        │",
        "│         | |  / _   \\     /   _ \\  | |        │",
        "│         | | | (_)   |   |   (_) | | |        │",
        "│         | |  \\_____/  _  \\_____/  | |        │",
        "│         | |          (_)          | |        │",
        "│         | |     .-----------.     | |        │",
        "│         | |      \\         /      | |        │",
        "│         |  \\      '-------'      /  |        │",
        "│          \\  '-------------------'  /         │",
        "│           '-----------------------'          │",
        "├──────────────────────────────────────────────┤",
        "│  IDENTITY : Vansh Kalawatia (@despair0x00)   │",
        "│  CORE     : Python · FastAPI · PostgreSQL    │",
        "│  MINDSET  : \"Surpass limits.\" (Vegeta / Guts)│",
        "│  TARGET   : Summer 2027 Backend Internship   │",
        "└──────────────────────────────────────────────┘"
    ]

    rows = []
    base_y = 70
    line_h = 38
    full_spec = terminal_header + [(f"{0.35 + i * 0.04:.2f}", l) for i, l in enumerate(lines_art)]
    
    for i, (delay, txt) in enumerate(full_spec):
        color = TEXT_MAIN
        if "IDENTITY" in txt or "AVATAR" in txt:
            color = "#ffffff"
        elif "CORE" in txt:
            color = TEXT_SILVER
        elif "MINDSET" in txt:
            color = "#a5d6ff"
        elif "TARGET" in txt:
            color = "#7ee787"
        elif "│" in txt or "┌" in txt or "└" in txt or "├" in txt:
            color = BORDER if ("." in txt or "_" in txt or "(" in txt) else "#58a6ff"

        rows.append(
            f'<text class="f" style="animation-delay:{delay}s" xml:space="preserve" '
            f'x="36" y="{base_y + i * line_h}" fill="{color}" font-weight="500" '
            f'font-size="21">{escape(txt)}</text>'
        )

    terminal_body = f"""
<defs>
  <linearGradient id="avatar_bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#161b22"/>
    <stop offset="1" stop-color="#090d13"/>
  </linearGradient>
</defs>
<rect width="{tw}" height="{th}" rx="18" fill="url(#avatar_bg)"/>
<rect x="1" y="1" width="{tw - 2}" height="{th - 2}" rx="17" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
<line x1="0" y1="46" x2="{tw}" y2="46" stroke="{BORDER}" stroke-width="1.5"/>
<circle cx="28" cy="23" r="6.5" fill="#484f58"/>
<circle cx="48" cy="23" r="6.5" fill="#6e7681"/>
<circle cx="68" cy="23" r="6.5" fill="#8b949e"/>
<text x="{tw / 2}" y="28" fill="{TEXT_MUTED}" font-size="15" font-family="{MONO}" text-anchor="middle">despair0x00@noir: ~/avatar $ ./render_ascii.sh</text>
<g font-family="{MONO}">
{''.join(rows)}
</g>
"""
    return terminal_body

# ---- 2 · HERO CARD (With ASCII Portrait) ---------------------------------------
def hero():
    h = 420
    ascii_portrait_svg = generate_hero_ascii_portrait()
    s = 0.42
    body = f"""
<defs>
  <pattern id="manga_dots" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#21262d" opacity="0.6"/>
  </pattern>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" stop-color="{TEXT_MAIN}"/>
    <stop offset=".42" stop-color="{TEXT_MAIN}"/>
    <stop offset=".5" stop-color="#ffffff"/>
    <stop offset=".58" stop-color="{TEXT_SILVER}"/>
    <stop offset="1" stop-color="{TEXT_MAIN}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-600 0;600 0;600 0"
      keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{BG_MAIN}"/>
<rect width="{W}" height="{h}" rx="14" fill="url(#manga_dots)"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>

<g class="f" {d(0)}>
  <rect class="live" x="48" y="49" width="8" height="8" rx="2" fill="{ACCENT}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{TEXT_MUTED}">PYTHON BACKEND ENGINEER · 3RD YEAR CSE · @despair0x00</text>
</g>
<text class="r" {d(0.15)} x="44" y="186" font-family="{SERIF}" font-size="110" letter-spacing="-2.5" fill="{TEXT_MAIN}">Vansh</text>
<text class="r" {d(0.3)} x="44" y="282" font-family="{SERIF}" font-style="italic" font-size="110" letter-spacing="-2.5" fill="url(#shine)">Kalawatia</text>
<g class="r" {d(0.55)}>
  {text_lines(48, 332, ["Specializing in high-throughput backends & async APIs.", "Targeting Summer 2027 Python Backend Internship."], 26, f'font-family="{SANS}" font-size="17" fill="{TEXT_SILVER}"')}
</g>
<g class="f" {d(0.8)}>
  <text x="48" y="396" font-family="{MONO}" font-size="13" fill="{TEXT_MAIN}">linkedin.com/in/vanshkalawatia</text>
  <text class="nu" x="290" y="396" font-family="{MONO}" font-size="13" fill="{ACCENT}">&#8599;</text>
</g>
<g transform="translate(506 34) scale({s})" class="f" {d(0.3)}>
  {ascii_portrait_svg}
</g>
"""
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                          "Vansh Kalawatia · despair0x00. Python Backend Engineer. Targeting Summer 2027 Internship."))

# ---- 3 · DEDICATED "WHO AM I" CARD (whoami.svg) --------------------------------
def whoami():
    h = 280
    body = f"""
<defs>
  <pattern id="whoami_grid" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#21262d" stroke-width="0.5" opacity="0.4"/>
  </pattern>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{BG_MAIN}"/>
<rect width="{W}" height="{h}" rx="14" fill="url(#whoami_grid)"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="13.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>

<!-- Top Metadata Pill -->
<g class="f" {d(0.1)}>
  <rect class="live" x="42" y="34" width="7" height="7" rx="2" fill="{ACCENT}"/>
  <text x="58" y="41" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{TEXT_MUTED}">WHO I AM // IDENTITY, ARCHITECTURE &amp; MINDSET</text>
</g>

<!-- Big Editorial Title -->
<text class="r" {d(0.25)} x="40" y="86" font-family="{SERIF}" font-size="38" fill="{TEXT_MAIN}">The Engineer <tspan font-style="italic" fill="{TEXT_SILVER}">&amp; The Philosophy</tspan></text>

<!-- Divider Line -->
<line x1="42" y1="108" x2="{W - 42}" y2="108" stroke="{BORDER}" stroke-width="1"/>

<!-- Left Column: The Engineer -->
<g class="r" {d(0.4)}>
  <text x="42" y="136" font-family="{MONO}" font-size="12" letter-spacing="1" fill="#58a6ff">// BACKGROUND &amp; FOCUS</text>
  <text x="42" y="164" font-family="{SANS}" font-size="14.5" fill="{TEXT_MAIN}">3rd-year B.Tech CSE undergrad in India targeting a <tspan font-weight="600">Summer 2027</tspan></text>
  <text x="42" y="188" font-family="{SANS}" font-size="14.5" fill="{TEXT_MAIN}">Python Backend Engineering Internship.</text>
  <text x="42" y="222" font-family="{MONO}" font-size="12" fill="{TEXT_MUTED}">STACK : <tspan fill="{TEXT_SILVER}">Python 3.12 · FastAPI · PostgreSQL · Redis · Docker · Linux</tspan></text>
  <text x="42" y="244" font-family="{MONO}" font-size="12" fill="{TEXT_MUTED}">ALIAS : <tspan fill="{TEXT_MAIN}">vanshkalawatia</tspan> &nbsp;·&nbsp; SIDE QUEST: <tspan fill="{TEXT_MAIN}">@despair0x00</tspan></text>
</g>

<!-- Center Vertical Separator -->
<line x1="510" y1="120" x2="510" y2="256" stroke="{BORDER}" stroke-width="1" stroke-dasharray="3 3"/>

<!-- Right Column: The Philosophy & Anime Taste -->
<g class="r" {d(0.55)}>
  <text x="540" y="136" font-family="{MONO}" font-size="12" letter-spacing="1" fill="#7ee787">// MINDSET &amp; INSPIRATION</text>
  
  <!-- Stoic Anime Quote Container -->
  <rect x="540" y="152" width="298" height="66" rx="8" fill="{SURFACE}"/>
  <rect x="540.75" y="152.75" width="296.5" height="64.5" rx="7.25" fill="none" stroke="{BORDER}" stroke-width="1"/>
  
  <text x="554" y="177" font-family="{SANS}" font-style="italic" font-size="13" fill="{TEXT_MAIN}">"Surpassing my limits... that's all I've ever</text>
  <text x="554" y="196" font-family="{SANS}" font-style="italic" font-size="13" fill="{TEXT_MAIN}">known."</text>
  <text x="618" y="196" font-family="{MONO}" font-size="11" fill="{TEXT_MUTED}">— Vegeta / Guts (Berserk)</text>
  
  <text x="540" y="244" font-family="{MONO}" font-size="11.5" fill="{TEXT_MUTED}">VIBE  : <tspan fill="{TEXT_SILVER}">Guts · Johan Liebert · Aizen · Methodical Grit</tspan></text>
</g>
"""
    write("whoami.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                            "Who Am I: Identity, Engineering, Background and Philosophy of Vansh Kalawatia."))

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
REPO_W, REPO_H = 880 / 3 - 8, 176

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
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{tag_color}"/>
  <text x="40" y="39" font-family="{SANS}" font-weight="600" font-size="16" fill="{TEXT_MAIN}">{escape(name)}</text>
  {text_lines(24, 72, wrap(desc, 32), 21, f'font-family="{SANS}" font-size="13.5" fill="{TEXT_SILVER}"')}
  <text x="24" y="{REPO_H - 24}" font-family="{MONO}" font-size="12" fill="{TEXT_MUTED}">{escape(meta)}</text>
  <text x="{REPO_W - 28}" y="{REPO_H - 24}" font-family="{MONO}" font-size="14" fill="{ACCENT}">↗</text>
</g>
"""
    write(f"repo-{name}.svg", svg(REPO_W, REPO_H, body, ["sans", "sans-b", "mono"], f"{name}: {desc}",
                                  left=4 * i, right=8 - 4 * i))

# ---- 6 · SECTION TITLES --------------------------------------------------------
def section_title(text, italic, theme):
    fg = TEXT_MAIN if theme == "dark" else "#111111"
    body = (
        f'<text class="r" {d(1.4)} x="2" y="46" font-family="{SERIF}" font-size="34" fill="{fg}">{escape(text)} '
        f'<tspan font-style="italic">{escape(italic)}</tspan></text>'
    )
    write(f"title-coding-{theme}.svg", svg(W, 64, body, ["serif", "serif-i"], f"{text} {italic}", bottom=0))

if __name__ == "__main__":
    data = json.load(open(DATA, "r", encoding="utf-8"))
    hero()
    whoami()
    heatmap(data)
    for i, (name, desc, lang, color, meta_tag) in enumerate(REAL_REPOS):
        repo_card(i, name, desc, lang, color, meta_tag)
    section_title("Featured", "repositories", "dark")
    section_title("Featured", "repositories", "light")
    print("Done rendering all cards!")
