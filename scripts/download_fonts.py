#!/usr/bin/env python3
import os
import urllib.request

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

FONTS = [
    "serif-400.woff",
    "serif-italic.woff",
    "geist-400.woff",
    "geist-600.woff",
    "geistmono-400.woff"
]

base_url = "https://raw.githubusercontent.com/AVIVASHISHTA29/AVIVASHISHTA29/main/fonts/"

for f in FONTS:
    path = os.path.join(FONTS_DIR, f)
    if not os.path.exists(path):
        print(f"Downloading {f}...")
        url = base_url + f
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(path, "wb") as out:
            out.write(resp.read())
        print(f"Saved {f} ({os.path.getsize(path)} bytes)")
    else:
        print(f"Already exists: {f}")
