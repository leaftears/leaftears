#!/usr/bin/env python3
"""Render assets/stats.svg from the GitHub contribution calendar.

The hosted streak cards query GitHub with their own token, so they only ever
see public contributions. This one runs with a token of ours, which means
private repositories are included — that is the whole reason it exists.

Needs a token with `read:user`. Locally it falls back to `gh auth token`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com/graphql"

# No from/to: contributionsCollection already defaults to the last twelve
# months, and passing an explicit window makes GitHub recompute it, which on a
# busy account answers with 503 often enough to be a problem.
QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""

# GitHub's own palette, so the card does not fight the profile page.
EMPTY = "#161b22"
LEVELS = ["#0e2f52", "#15477d", "#1c5fa8", "#2f81f7"]
TEXT = "#c9d1d9"
MUTED = "#8b949e"
DIM = "#6e7681"
LINE = "#30363d"
ACCENT = "#2f81f7"

CELL = 11
GAP = 3
STEP = CELL + GAP


def token() -> str:
    for name in ("STATS_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        if value := os.environ.get(name):
            return value
    try:
        return subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sys.exit("no token: set STATS_TOKEN or log in with gh")


def fetch(login: str) -> dict:
    payload = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()

    request = urllib.request.Request(
        API,
        data=payload,
        headers={
            "Authorization": f"bearer {token()}",
            "Content-Type": "application/json",
            "User-Agent": "mika2go-stats",
        },
    )
    # 502/503 from the GraphQL endpoint is common on accounts with a lot of
    # contribution data and clears on its own, so retry rather than fail the
    # scheduled run.
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = json.load(response)
            break
        except urllib.error.HTTPError as err:
            if err.code in (502, 503, 504) and attempt < 4:
                time.sleep(5 * (attempt + 1))
                continue
            sys.exit(f"github returned {err.code}: {err.read().decode()[:200]}")
        except urllib.error.URLError as err:
            if attempt < 4:
                time.sleep(5 * (attempt + 1))
                continue
            sys.exit(f"could not reach github: {err}")

    if "errors" in body:
        sys.exit(f"graphql: {body['errors']}")
    return body["data"]["user"]


def flatten(user: dict) -> list[tuple[dt.date, int]]:
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [
        (dt.date.fromisoformat(day["date"]), day["contributionCount"])
        for week in weeks
        for day in week["contributionDays"]
    ]


def streaks(days: list[tuple[dt.date, int]]) -> tuple[dict, dict]:
    """Current and longest run of consecutive days with at least one contribution.

    Today is excluded from breaking the current streak: at 09:00 you have not
    necessarily committed yet, and a card that reads zero every morning is
    useless.
    """
    today = dt.date.today()
    best = {"length": 0, "start": None, "end": None}
    run_start = None
    run_length = 0

    for date, count in days:
        if count > 0:
            run_start = run_start or date
            run_length += 1
            if run_length > best["length"]:
                best = {"length": run_length, "start": run_start, "end": date}
        else:
            run_start, run_length = None, 0

    lookup = dict(days)
    cursor = today
    if lookup.get(cursor, 0) == 0:
        cursor -= dt.timedelta(days=1)
    current = {"length": 0, "start": None, "end": cursor}
    while lookup.get(cursor, 0) > 0:
        current["length"] += 1
        current["start"] = cursor
        cursor -= dt.timedelta(days=1)

    return current, best


def level(count: int, peak: int) -> str:
    if count <= 0:
        return EMPTY
    # Quartiles of the observed maximum rather than fixed thresholds, so the
    # card stays readable whether a busy day is 5 commits or 60.
    for index, bound in enumerate((0.15, 0.35, 0.65)):
        if count <= max(1, round(peak * bound)):
            return LEVELS[index]
    return LEVELS[3]


def human(date: dt.date | None) -> str:
    return date.strftime("%-d %b %Y") if date else "—"


def render(login: str, user: dict, days: list[tuple[dt.date, int]]) -> str:
    total = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    current, best = streaks(days)
    active = sum(1 for _, count in days if count > 0)
    peak = max((count for _, count in days), default=0)
    busiest = max(days, key=lambda d: d[1])[0] if days else None

    weeks = (len(days) + 6) // 7
    grid_w = weeks * STEP - GAP
    width = 760
    left = (width - grid_w) // 2
    top = 132

    parts: list[str] = []
    add = parts.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{top + 7 * STEP + 46}" '
        f'viewBox="0 0 {width} {top + 7 * STEP + 46}" font-family="JetBrains Mono, ui-monospace, monospace">')
    add('<style>.n{font-size:30px;font-weight:600;fill:#c9d1d9}'
        '.l{font-size:11px;fill:#8b949e;letter-spacing:.08em}'
        '.d{font-size:10px;fill:#6e7681}'
        '.m{font-size:9px;fill:#6e7681}</style>')

    columns = [
        (str(total), "CONTRIBUTIONS", f"last 365 days · {active} active days"),
        (str(current["length"]), "CURRENT STREAK",
         f"{human(current['start'])} → {human(current['end'])}" if current["length"] else "no streak"),
        (str(best["length"]), "LONGEST STREAK",
         f"{human(best['start'])} → {human(best['end'])}" if best["length"] else "—"),
    ]
    for index, (value, label, detail) in enumerate(columns):
        centre = width * (2 * index + 1) // 6
        fill = ACCENT if index == 1 else TEXT
        add(f'<text x="{centre}" y="52" class="n" fill="{fill}" text-anchor="middle">{value}</text>')
        add(f'<text x="{centre}" y="76" class="l" text-anchor="middle">{label}</text>')
        add(f'<text x="{centre}" y="95" class="d" text-anchor="middle">{detail}</text>')
        if index:
            x = width * index // 3
            add(f'<line x1="{x}" y1="26" x2="{x}" y2="86" stroke="{LINE}"/>')

    add(f'<line x1="{left}" y1="112" x2="{left + grid_w}" y2="112" stroke="{LINE}"/>')

    seen_months: set[str] = set()
    for index, (date, count) in enumerate(days):
        column, row = divmod(index, 7)
        x = left + column * STEP
        y = top + row * STEP
        add(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{level(count, peak)}"><title>{date} · {count}</title></rect>')
        key = date.strftime("%Y-%m")
        if date.day <= 7 and key not in seen_months:
            seen_months.add(key)
            add(f'<text x="{x}" y="{top - 8}" class="m">{date.strftime("%b")}</text>')

    footer = top + 7 * STEP + 20
    if busiest:
        add(f'<text x="{left}" y="{footer}" class="d">busiest day {human(busiest)} · {peak} contributions</text>')
    add(f'<text x="{left + grid_w}" y="{footer}" class="d" text-anchor="end">'
        f'includes private repositories</text>')

    legend_x = left + grid_w - 132
    add(f'<text x="{legend_x - 8}" y="{footer + 20}" class="m" text-anchor="end">less</text>')
    for index, colour in enumerate([EMPTY, *LEVELS]):
        add(f'<rect x="{legend_x + index * 15}" y="{footer + 11}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{colour}"/>')
    add(f'<text x="{legend_x + 5 * 15 + 2}" y="{footer + 20}" class="m">more</text>')

    add("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", default="mika2go")
    parser.add_argument("--out", default="assets/stats.svg")
    args = parser.parse_args()

    user = fetch(args.login)
    days = flatten(user)
    svg = render(args.login, user, days)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    previous = out.read_text(encoding="utf-8") if out.exists() else ""
    if previous == svg:
        print("unchanged")
        return 0
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out} ({len(svg)} bytes, {len(days)} days)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
