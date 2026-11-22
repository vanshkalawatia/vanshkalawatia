#!/usr/bin/env python3
"""
Render Vansh Kalawatia's profile README cards as animated SVGs into cards/.
Design system: "Three Worlds", matched to AVIVASHISHTA29 editorial design.
Cards:
- hero.svg
- heatmap.svg
- activity.svg
- build.svg
- brand.svg
- learn.svg
- title-coding-dark.svg
- title-coding-light.svg
- repo-cli-expense-tracker.svg
- repo-authenticated-rest-api.svg
- repo-distributed-task-queue.svg
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

# Brand tokens
PAPER = "#f3f3f1"
PAPER_DEEP = "#e2e2de"
INK = "#111111"
INK_SOFT = "#3a3a3c"
MUTED = "#6e6e73"
RULE = "#dcdcd7"
TECH = "#2f55ff"       # Blue
STUDIO = "#ef3b2d"     # Coral
LEARN = "#ffc81a"      # Gold
W = 880                # Full card width

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
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
@keyframes tilein{0%{opacity:0;transform:translateY(90px) scale(.6) rotate(-9deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}75%{transform:translateY(3px) scale(.98) rotate(-.8deg)}90%{transform:translateY(-1px) scale(1.01) rotate(.2deg)}100%{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes arrowin{0%{opacity:0;transform:translateX(-30px)}60%{opacity:1;transform:translateX(6px)}100%{opacity:1;transform:none}}
@keyframes roll{from{transform:translateY(60px)}to{transform:none}}
@keyframes sheen{0%{transform:translateX(-260px) skewX(-20deg)}22%,100%{transform:translateX(420px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.1s cubic-bezier(.2,.8,.2,1) both}
.sl{opacity:0;transform-box:fill-box;animation:slidein .6s cubic-bezier(.2,.7,.2,1) both}
.ai{opacity:0;transform-box:fill-box;animation:arrowin .7s cubic-bezier(.2,.7,.2,1) both}
.ro{transform-box:fill-box;animation:roll .8s cubic-bezier(.15,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro,.rg{animation:none!important;opacity:1!important;transform:none!important}.sh,.rg{display:none}}
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

GAP = 12
BOTTOM = 12
COL = W / 3

def svg(w, h, body, fonts, label, extra_css="", left=0, right=0, bottom=BOTTOM):
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w, h = w + left + right, h + bottom
    css = font_face(fonts) + BASE_CSS + extra_css
    if os.environ.get("STATIC"):
        css += ".r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro{animation:none!important;opacity:1!important;transform:none!important}.sh,.rg{display:none}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" '
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

# ---- Terminal SVG generator for Hero Card ----
def generate_hero_terminal():
    tw, th = 820, 840
    lines = [
        ("0.25", "$ whoami && cat ~/.identity"),
        ("0.40", "vanshkalawatia · despair0x00"),
        ("0.55", "3rd Year CSE · India"),
        ("0.70", ""),
        ("0.85", "$ python -m uvicorn app.main:api --reload"),
        ("1.00", "[INFO] Started server process [PID: 2027]"),
        ("1.15", "[INFO] Waiting for application startup."),
        ("1.30", "[INFO] Application startup complete."),
        ("1.45", "[INFO] Uvicorn running on http://127.0.0.1:8000"),
        ("1.60", ""),
        ("1.75", "$ cat ./mindset.txt"),
        ("1.90", "\"Surpassing my limits... that's all I've ever known.\""),
        ("2.05", "-- Vegeta / Guts (Berserk)"),
        ("2.20", ""),
        ("2.35", "$ ./target.sh"),
        ("2.50", ">> Summer 2027 Python Backend Internship"),
        ("2.65", ">> Stack: FastAPI · PostgreSQL · Redis · Docker"),
        ("2.80", ">> Status: Ready to interview & deploy."),
        ("2.95", "despair0x00@backend:~$ █")
    ]
    
    rows = []
    base_y = 75
    line_h = 36
    for i, (delay, txt) in enumerate(lines):
        color = "#e6edf3"
        font_weight = "400"
        if txt.startswith("$"):
            color = "#58a6ff"
            font_weight = "600"
        elif txt.startswith("[INFO]"):
            color = "#7ee787"
        elif txt.startswith(">>"):
            color = "#f0883e"
        elif txt.startswith("\""):
            color = "#d2a8ff"
        elif txt.endswith("█"):
            color = "#ff7b72"
            
        rows.append(
            f'<text class="f" style="animation-delay:{delay}s" xml:space="preserve" '
            f'x="36" y="{base_y + i * line_h}" fill="{color}" font-weight="{font_weight}" '
            f'font-size="22">{escape(txt)}</text>'
        )

    terminal_body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#111722"/>
    <stop offset="1" stop-color="#0a0d14"/>
  </linearGradient>
</defs>
<rect width="{tw}" height="{th}" rx="18" fill="url(#bg)"/>
<rect x="1" y="1" width="{tw - 2}" height="{th - 2}" rx="17" fill="none" stroke="#30363d" stroke-width="1.5"/>
<line x1="0" y1="46" x2="{tw}" y2="46" stroke="#30363d" stroke-width="1.5"/>
<circle cx="28" cy="23" r="7" fill="#ff5f56"/>
<circle cx="50" cy="23" r="7" fill="#ffbd2e"/>
<circle cx="72" cy="23" r="7" fill="#27c93f"/>
<text x="{tw / 2}" y="28" fill="#8b949e" font-size="16" font-family="{MONO}" text-anchor="middle">despair0x00@backend: ~/portfolio $ ./init.sh</text>
<g font-family="{MONO}">
{''.join(rows)}
</g>
"""
    return terminal_body

# ---- 1 · HERO CARD -------------------------------------------------------------
def hero():
    h = 420
    terminal_content = generate_hero_terminal()
    s = 0.42
    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/>
    <stop offset=".5" stop-color="{TECH}"/><stop offset=".58" stop-color="{INK}"/>
    <stop offset="1" stop-color="{INK}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-600 0;600 0;600 0"
      keyTimes="0;.45;1" dur="7s" begin="1.6s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<g class="f" {d(0)}>
  <rect class="live" x="48" y="49" width="8" height="8" rx="2" fill="{TECH}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">PYTHON BACKEND ENGINEER · 3RD YEAR CSE</text>
</g>
<text class="r" {d(0.15)} x="44" y="186" font-family="{SERIF}" font-size="110" letter-spacing="-2.5" fill="{INK}">Vansh</text>
<text class="r" {d(0.3)} x="44" y="282" font-family="{SERIF}" font-style="italic" font-size="110" letter-spacing="-2.5" fill="url(#shine)">Kalawatia</text>
<g class="r" {d(0.55)}>
  {text_lines(48, 332, ["Building reliable, high-throughput backend services.", "Targeting Summer 2027 Backend Internship."], 26, f'font-family="{SANS}" font-size="17" fill="{INK_SOFT}"')}
</g>
<g class="f" {d(0.8)}>
  <text x="48" y="396" font-family="{MONO}" font-size="13" fill="{INK}">linkedin.com/in/vanshkalawatia</text>
  <text class="nu" x="290" y="396" font-family="{MONO}" font-size="13" fill="{TECH}">&#8599;</text>
</g>
<g transform="translate(506 34) scale({s})" class="f" {d(0.3)}>
  {terminal_content}
</g>
"""
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                          "Vansh Kalawatia. Python Backend Engineer · 3rd Year CSE. Targeting Summer 2027 Backend Internship."))

# ---- 2 · TRI TILES (BUILD / BRAND / LEARN) ------------------------------------
TILE_W, TILE_H = 880 / 3 - 8, 210

def count_up(num, word, x, y, attrs, begin, dur=1.1, frames=18):
    m = re.match(r"([\d.]+)(.*)", str(num))
    if m:
        val, suf = float(m.group(1)), m.group(2)
        dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
    else:
        val, suf, dec = 0, str(num), 0
    tail = f' <tspan font-style="italic">{escape(word)}</tspan>'
    if os.environ.get("STATIC"):
        return f'<text x="{x}" y="{y}" {attrs}>{escape(str(num))}{tail}</text>'
    out = []
    for i in range(frames + 1):
        e = 1 - (1 - i / frames) ** 3
        txt = str(num) if i == frames else f"{val * e:.{dec}f}{suf}"
        on = begin + dur * i / frames
        off = "" if i == frames else f'<set attributeName="opacity" to="0" begin="{begin + dur * (i + 1) / frames:.3f}s"/>'
        out.append(f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(txt)}{tail}'
                   f'<set attributeName="opacity" to="1" begin="{on:.3f}s"/>{off}</text>')
    return "".join(out)

def tile(name, label, color, on, num, word, blurb, delay, pos):
    lines = wrap(blurb, 34)
    blurb_svg = "".join(
        f'<text class="r" {d(delay + 0.75 + i * 0.1)} x="24" y="{150 + i * 20}" font-family="{SANS}" '
        f'font-size="14" fill="{on}" opacity=".92">{escape(l)}</text>'
        for i, l in enumerate(lines)
    )
    body = f"""
<defs>
  <clipPath id="card_{name}"><rect width="{TILE_W}" height="{TILE_H}" rx="14"/></clipPath>
  <clipPath id="slot_{name}"><rect x="0" y="62" width="{TILE_W}" height="62"/></clipPath>
  <linearGradient id="gl_{name}" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="ti" {d(delay)}>
  <g clip-path="url(#card_{name})">
    <rect width="{TILE_W}" height="{TILE_H}" fill="{color}"/>
    <circle class="rg" {d(delay + 0.5)} cx="{TILE_W - 40}" cy="{TILE_H - 40}" r="60" fill="none" stroke="{on}" stroke-opacity=".5" stroke-width="2"/>
    <rect class="sh" style="animation-delay:{delay + 1.4:.2f}s" x="0" y="-20" width="90" height="{TILE_H + 40}" fill="url(#gl_{name})" transform="translate(-260 0)"/>
  </g>
  <text class="sl" {d(delay + 0.35)} x="24" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{on}">{label}</text>
  <g class="ai" {d(delay + 0.5)}><text class="n" style="animation-delay:{delay + 1.3:.2f}s" x="250" y="38" font-family="{MONO}" font-size="14" fill="{on}">&#8594;</text></g>
  <g clip-path="url(#slot_{name})"><g class="ro" {d(delay + 0.45)}>
    {count_up(num, word, 22, 112, f'font-family="{SERIF}" font-size="44" fill="{on}"', delay + 0.45)}
  </g></g>
  {blurb_svg}
</g>
"""
    write(f"{name}.svg", svg(TILE_W, TILE_H, body, ["serif", "serif-i", "sans", "mono"],
                             f"{label}: {num} {word}. {blurb}", left=4 * pos, right=8 - 4 * pos))

# ---- 3 · ACTIVITY (MONTHLY BARS) ------------------------------------------------
def activity(data):
    h = 340
    monthly = data["monthly"][-12:]
    best = max(monthly[:-1] or monthly, key=lambda m: m["total"])
    top = best["total"] if best["total"] > 0 else 100
    x0, x1, base, maxh, gap = 40, 600, 292, 140, 10
    bw = (x1 - x0 - gap * (len(monthly) - 1)) / len(monthly)
    bars = []
    for i, m in enumerate(monthly):
        partial = i == len(monthly) - 1
        is_best = m is best
        bh = max(6, round(m["total"] / top * maxh))
        x = x0 + i * (bw + gap)
        fill = TECH if is_best else ("#c9c9c4" if partial else INK)
        try:
            label = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        except Exception:
            label = m["month"][-2:]
        bars.append(
            f'<rect class="g" style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x:.1f}" y="{base - bh}" '
            f'width="{bw:.1f}" height="{bh}" rx="4" fill="{fill}"><title>{label}: {m["total"]:,}</title></rect>'
            f'<text class="f" style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
        )
        if is_best:
            bars.append(
                f'<text class="p" style="animation-delay:3.2s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TECH}">{m["total"]:,}</text>'
            )
    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    streak_note = "current streak, and the longest" if cs >= ls else f"current streak, longest {ls}"
    total_days = len(data["days"])
    stats = [
        (f'{cs} <tspan font-style="italic">days</tspan>', streak_note),
        (f'{data["active_days"]}<tspan fill="#8e8e93"> / {total_days}</tspan>', "days with a commit"),
        (f'{data["best_day"]["count"]}', "on the busiest day"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 104 + i * 92
        side.append(
            f'<g class="r" {d(2.6 + i * 0.15)}>'
            f'<text x="650" y="{y}" font-family="{SERIF}" font-size="40" fill="{INK}">{big}</text>'
            f'<text x="650" y="{y + 24}" font-family="{SANS}" font-size="13" fill="{MUTED}">{small}</text></g>'
        )
        if i < 2:
            side.append(f'<rect class="f" {d(2.6)} x="650" y="{y + 44}" width="190" height="1" fill="{RULE}"/>')
    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="f" {d(1.9)} x="40" y="58" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r" {d(2.0)} x="38" y="114" font-family="{SERIF}" font-size="52" fill="{INK}">{data["total_contributions"]:,} <tspan font-style="italic">contributions</tspan></text>
{''.join(bars)}
{''.join(side)}
"""
    write("activity.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                              f'{data["total_contributions"]:,} contributions in the last year, {cs}-day streak'))

# ---- 4 · BLUE CONTRIBUTION GRAPH (HEATMAP) -------------------------------------
BLUE = [PAPER_DEEP, "#c8d3ff", "#94a8ff", "#6280ff", TECH, "#1a3be0"]

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
        delay = 1.0 + col * 0.03 + row * 0.02
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="3" fill="{BLUE[level_for(c)]}">'
            f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>'
        )
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">{m}</text>'
        for col, m in months if col < ncols - 8
    )
    legend_x = right - len(BLUE) * 14
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{gy + 7 * step + 6}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(BLUE)
    )
    h = gy + 7 * step + 44
    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="r" {d(0.8)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{INK}">Every day, <tspan font-style="italic" fill="{TECH}">in blue</tspan></text>
<text class="f" {d(0.8)} x="{right}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(2.4)}>{labels}
<text x="{legend_x - 8}" y="{gy + 7 * step + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">less</text>
{legend}
<text x="{legend_x + len(BLUE) * 14 + 2}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">more</text></g>
"""
    write("heatmap.svg", svg(W, h, body, ["serif", "serif-i", "mono"],
                             f'Contribution graph: {data["total_contributions"]:,} contributions in the last year'))

# ---- 5 · REPO CARDS -------------------------------------------------------------
REPO_W, REPO_H = 880 / 3 - 8, 176

REPOS = [
    ("cli-expense-tracker", "High-performance CLI tool to track, categorize, and export personal finances with SQLite.", "Python", TECH, "live"),
    ("authenticated-rest-api", "Production-ready async REST API with JWT, OAuth2, rate limiting, and PostgreSQL.", "FastAPI", STUDIO, "live"),
    ("distributed-task-queue", "Asynchronous background task processing pipeline built with Redis, Celery & Docker.", "Docker", LEARN, "live"),
]

def repo_card(i, name, desc, lang, color, meta_tag):
    delay = 4.6 + i * 0.12
    meta = f"{lang}  ·  {meta_tag}"
    body = f"""
<rect width="{REPO_W}" height="{REPO_H}" rx="14" fill="{PAPER}"/>
<g class="r" {d(delay)}>
  <rect x="24" y="30" width="8" height="8" rx="2" fill="{color}"/>
  <text x="40" y="39" font-family="{SANS}" font-weight="600" font-size="18" fill="{INK}">{escape(name)}</text>
  {text_lines(24, 72, wrap(desc, 34), 21, f'font-family="{SANS}" font-size="14" fill="{INK_SOFT}"')}
  <text x="24" y="{REPO_H - 24}" font-family="{MONO}" font-size="12" fill="{MUTED}">{escape(meta)}</text>
</g>
"""
    write(f"repo-{name}.svg", svg(REPO_W, REPO_H, body, ["sans", "sans-b", "mono"], f"{name}: {desc}",
                                  left=4 * i, right=8 - 4 * i))

# ---- 6 · SECTION TITLES --------------------------------------------------------
def section_title(text, italic, theme):
    fg = "#e6edf3" if theme == "dark" else INK
    body = (
        f'<text class="r" {d(4.4)} x="2" y="46" font-family="{SERIF}" font-size="34" fill="{fg}">{escape(text)} '
        f'<tspan font-style="italic">{escape(italic)}</tspan></text>'
    )
    write(f"title-coding-{theme}.svg", svg(W, 64, body, ["serif", "serif-i"], f"{text} {italic}", bottom=0))

if __name__ == "__main__":
    data = json.load(open(DATA, "r", encoding="utf-8"))
    hero()
    tile("build", "BUILD", TECH, "#ffffff", "3", "projects",
         "Production-ready backend services, REST APIs, and CLI tooling with Python.", 3.1, 0)
    tile("brand", "STACK", STUDIO, "#ffffff", "99.9", "% uptime",
         "PostgreSQL, Redis, Docker, Linux, and asynchronous concurrency.", 3.35, 1)
    tile("learn", "TARGET", LEARN, INK, "2027", "internship",
         "Daily katas, system design, and building in public at @despair0x00.", 3.6, 2)
    activity(data)
    heatmap(data)
    for i, (name, desc, lang, color, meta_tag) in enumerate(REPOS):
        repo_card(i, name, desc, lang, color, meta_tag)
    section_title("What I'm", "coding", "dark")
    section_title("What I'm", "coding", "light")
    print("Done rendering all profile cards!")
