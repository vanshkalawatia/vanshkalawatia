#!/usr/bin/env python3
"""
Fetch real GitHub contribution activity for Vansh Kalawatia directly from GitHub.
Parses the live SVG / HTML contribution grid from https://github.com/users/<user>/contributions.
"""

import datetime
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
OUT_PATH = os.path.join(DATA_DIR, "contributions.json")

# Support primary account or multiple accounts
DEFAULT_USER = "vanshkalawatia"

def fetch_user_contributions(username):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8")
    
    # 1. Parse tooltip map: tool-tip for="ID">COUNT contribution... on DATE</tool-tip>
    tooltips = {}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>', html, re.S):
        tooltips[m.group(1)] = m.group(2).strip()

    # 2. Parse calendar days
    days = {}
    for td in re.finditer(r'<td\s+([^>]*ContributionCalendar-day[^>]*)>', html):
        attrs = td.group(1)
        date_m = re.search(r'data-date="([^"]+)"', attrs)
        level_m = re.search(r'data-level="([^"]+)"', attrs)
        id_m = re.search(r'id="([^"]+)"', attrs)
        
        if date_m:
            d_date = date_m.group(1)
            d_level = int(level_m.group(1)) if level_m else 0
            d_id = id_m.group(1) if id_m else ""
            
            tip = tooltips.get(d_id, "")
            count = 0
            if tip:
                cnt_m = re.match(r'(\d+)', tip)
                if cnt_m:
                    count = int(cnt_m.group(1))
                elif "no contribution" in tip.lower():
                    count = 0
                else:
                    count = d_level
            else:
                count = d_level
            days[d_date] = {"date": d_date, "count": count, "level": d_level}

    return days

def fetch_and_save():
    raw_users = os.environ.get("GH_PROFILE_USER", DEFAULT_USER)
    users = [u.strip() for u in raw_users.split(",") if u.strip()]
    if not users:
        users = [DEFAULT_USER]
        
    print(f"Fetching real GitHub ink for user(s): {', '.join(users)}...")
    
    merged_days = {}
    for user in users:
        try:
            user_days = fetch_user_contributions(user)
            print(f"  Fetched {len(user_days)} days for @{user} ({sum(d['count'] for d in user_days.values())} contributions)")
            for d_date, data in user_days.items():
                if d_date not in merged_days:
                    merged_days[d_date] = {"date": d_date, "count": data["count"], "level": data["level"]}
                else:
                    merged_days[d_date]["count"] += data["count"]
                    merged_days[d_date]["level"] = max(merged_days[d_date]["level"], data["level"])
        except Exception as e:
            print(f"  Error fetching ink for @{user}: {e}")

    # If successfully fetched
    if merged_days:
        days = sorted(merged_days.values(), key=lambda d: d["date"])
        total = sum(d["count"] for d in days)
        active = sum(1 for d in days if d["count"] > 0)
        best = max(days, key=lambda d: d["count"]) if days else {"count": 0, "date": ""}

        # Streaks
        curr_streak = 0
        longest_streak = 0
        temp_streak = 0
        for d in days:
            if d["count"] > 0:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0
        for d in reversed(days):
            if d["count"] > 0:
                curr_streak += 1
            else:
                break

        # Monthly aggregation
        monthly_dict = {}
        for d in days:
            m = d["date"][:7]
            monthly_dict[m] = monthly_dict.get(m, 0) + d["count"]
        monthly = [{"month": m, "total": tot} for m, tot in sorted(monthly_dict.items())]

        res = {
            "username": ", ".join(users),
            "generated_at": datetime.datetime.now().isoformat(),
            "total_contributions": total,
            "active_days": active,
            "current_streak": {"length": curr_streak},
            "longest_streak": {"length": longest_streak},
            "best_day": {"count": best["count"], "date": best["date"]},
            "monthly": monthly,
            "days": days
        }

        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"SUCCESS: Saved {OUT_PATH} with {total} real contributions over {len(days)} days ({active} active days).")
        return res
    else:
        print("Warning: Network fetch failed. Checking for existing contributions.json cache...")
        if os.path.exists(OUT_PATH):
            print(f"Using cached {OUT_PATH}")
            return json.load(open(OUT_PATH, "r", encoding="utf-8"))
        else:
            raise RuntimeError("No contribution data could be fetched and no local cache exists.")

if __name__ == "__main__":
    fetch_and_save()
