#!/usr/bin/env python3
"""Render assets/stats.svg from the GitHub contribution calendar.

Draws the contribution calendar as a heatmap with both streaks. The hosted
cards do roughly this, but none of them show the tooltip counts or the
busiest-day line, and having it in the repository means it cannot break
because someone else's free tier ran out.

Any token works, including the GITHUB_TOKEN that Actions provides — the
calendar is public as long as "Include private contributions on my profile"
is enabled in account settings. Without that setting no token short of a
personal one can see private activity, and the numbers will be small.
Locally it falls back to `gh auth token`.
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

LANG_QUERY = """
query {
  viewer {
    repositories(first: 100, ownerAffiliations: [OWNER], isFork: false) {
      totalCount
      nodes {
        isPrivate
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
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
    return post(QUERY, {"login": login})["user"]


def post(query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()

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
    return body["data"]


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


def languages() -> tuple[list[tuple[str, int, str]], int, int]:
    """Bytes per language across every repository the token can see.

    The hosted language cards read the public REST endpoint, so they miss
    private repositories entirely. This one does not, which is the only
    reason to draw it ourselves.
    """
    data = post(LANG_QUERY)["viewer"]["repositories"]
    totals: dict[str, int] = {}
    colours: dict[str, str] = {}
    private = 0
    for repo in data["nodes"]:
        private += 1 if repo["isPrivate"] else 0
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
            colours[name] = edge["node"]["color"] or "#8b949e"

    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    top = [(name, size, colours[name]) for name, size in ranked[:8]]
    if len(ranked) > 8:
        rest = sum(size for _, size in ranked[8:])
        top.append(("Other", rest, "#6e7681"))
    return top, data["totalCount"], private


def render_languages(rows: list[tuple[str, int, str]], repos: int, private: int) -> str:
    width, bar_y, bar_h = 760, 64, 14
    total = sum(size for _, size, _ in rows) or 1
    height = bar_y + bar_h + 30 + ((len(rows) + 2) // 3) * 22

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="JetBrains Mono, ui-monospace, monospace">',
        '<style>.t{font-size:13px;fill:#c9d1d9;font-weight:600}'
        '.s{font-size:10px;fill:#6e7681}.k{font-size:11px;fill:#c9d1d9}'
        '.p{font-size:11px;fill:#8b949e}</style>',
        f'<text x="24" y="30" class="t">Languages by bytes written</text>',
        f'<text x="{width - 24}" y="30" class="s" text-anchor="end">'
        f'{repos} repositories · {private} private · all counted</text>',
    ]

    # One rounded bar built from clipped segments, so the ends stay round
    # without each segment needing its own radius.
    parts.append(f'<clipPath id="bar"><rect x="24" y="{bar_y}" width="{width - 48}" '
                 f'height="{bar_h}" rx="7"/></clipPath>')
    parts.append('<g clip-path="url(#bar)">')
    offset = 24.0
    span = width - 48
    for _, size, colour in rows:
        chunk = span * size / total
        parts.append(f'<rect x="{offset:.2f}" y="{bar_y}" width="{chunk + 0.6:.2f}" '
                     f'height="{bar_h}" fill="{colour}"/>')
        offset += chunk
    parts.append("</g>")

    for index, (name, size, colour) in enumerate(rows):
        column, row = index % 3, index // 3
        x = 24 + column * ((width - 48) // 3)
        y = bar_y + bar_h + 32 + row * 22
        share = 100 * size / total
        parts.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{colour}"/>')
        parts.append(f'<text x="{x + 18}" y="{y}" class="k">{name}</text>')
        parts.append(f'<text x="{x + 18 + len(name) * 7 + 10}" y="{y}" class="p">'
                     f'{share:.1f}%</text>')

    parts.append("</svg>")
    return "\n".join(parts) + "\n"



PIN_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    name description stargazerCount forkCount
    primaryLanguage { name color }
  }
}
"""

CARD_W, CARD_H = 278, 116


def wrap(text: str, width: int, lines: int) -> list[str]:
    out, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            out.append(current)
            current = word
            if len(out) == lines:
                break
        else:
            current = candidate
    if len(out) < lines and current:
        out.append(current)
    if len(out) == lines and current not in out:
        out[-1] = out[-1][: width - 1].rstrip() + "…"
    return out


def render_pin(repo: dict) -> str:
    """A repository card in the shape github-readme-stats draws, but ours.

    The hosted instance answers 503 more often than not, and a profile that
    depends on someone else's free tier is a profile with broken images.
    """
    language = repo.get("primaryLanguage") or {}
    body = wrap(repo.get("description") or "", 37, 3)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
        f'viewBox="0 0 {CARD_W} {CARD_H}" font-family="JetBrains Mono, ui-monospace, monospace">',
        '<style>.n{font-size:13px;font-weight:600;fill:#2f81f7}'
        '.b{font-size:10.5px;fill:#8b949e}.s{font-size:10.5px;fill:#8b949e}</style>',
        f'<rect width="{CARD_W}" height="{CARD_H}" rx="8" fill="#0d1117" stroke="#21262d"/>',
        # The little book glyph github-readme-stats uses, drawn rather than
        # embedded so the card has no external references at all.
        '<path d="M18 22h9a2 2 0 0 1 2 2v11H20a2 2 0 0 0-2 2V22z" fill="none" '
        'stroke="#58a6ff" stroke-width="1.4"/>',
        f'<text x="36" y="33" class="n">{repo["name"]}</text>',
    ]
    for index, line in enumerate(body):
        parts.append(f'<text x="18" y="{55 + index * 15}" class="b">{escape(line)}</text>')

    footer = CARD_H - 16
    x = 18
    if language.get("name"):
        parts.append(f'<circle cx="{x + 5}" cy="{footer - 4}" r="5" '
                     f'fill="{language.get("color") or "#8b949e"}"/>')
        parts.append(f'<text x="{x + 16}" y="{footer}" class="s">{language["name"]}</text>')
        x += 26 + len(language["name"]) * 6.6
    for glyph, value in (("★", repo["stargazerCount"]), ("⑂", repo["forkCount"])):
        if value:
            parts.append(f'<text x="{x:.0f}" y="{footer}" class="s">{glyph} {value}</text>')
            x += 34
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))



SKILLS = [
    ("Systems", ["Frame capture", "Hardware encoding",
                 "Audio pipelines", "Memory held to a budget"]),
    ("Desktop UI", ["Qt Quick · QML", "GTK4 · WPF",
                    "Tauri + Svelte", "Ratatui"]),
    ("Linux", ["Wayland · PipeWire", "inotify · systemd units",
               "Arch packaging"]),
    ("Windows", ["Graphics Capture", "D3D11 · Media Foundation", "WASAPI"]),
    ("Digging", ["Binary formats", "Patching packaged apps",
                 "Tracing real behaviour"]),
    ("Shipping", ["Warnings as errors", "Native CI",
                  "MSI · NSIS · AppImage · AUR"]),
]


def render_skill(title: str, items: list[str]) -> str:
    """Same footprint as a repository card, so the two grids line up."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
        f'viewBox="0 0 {CARD_W} {CARD_H}" font-family="JetBrains Mono, ui-monospace, monospace">',
        '<style>.h{font-size:12.5px;font-weight:600;fill:#2f81f7}'
        '.i{font-size:10.5px;fill:#8b949e}</style>',
        f'<rect width="{CARD_W}" height="{CARD_H}" rx="8" fill="#0d1117" stroke="#21262d"/>',
        # A short rule instead of an icon: the repository cards carry a glyph,
        # these do not need one and the page is quieter without it.
        '<rect x="18" y="22" width="18" height="2" rx="1" fill="#2f81f7"/>',
        f'<text x="18" y="44" class="h">{escape(title)}</text>',
    ]
    for index, item in enumerate(items[:4]):
        parts.append(f'<text x="18" y="{62 + index * 14}" class="i">{escape(item)}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def pins(specs: list[tuple[str, str]]) -> dict[str, str]:
    out = {}
    for owner, name in specs:
        repo = post(PIN_QUERY, {"owner": owner, "name": name})["repository"]
        out[f"pin-{name.lower()}"] = render_pin(repo)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", default="mika2go")
    parser.add_argument("--out-dir", default="assets")
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []

    user = fetch(args.login)
    days = flatten(user)
    cards = {
        "stats": render(args.login, user, days),
        "languages": render_languages(*languages()),
    }
    cards.update({
        f"skill-{title.lower().replace(' ', '-')}": render_skill(title, items)
        for title, items in SKILLS
    })
    cards.update(pins([
        ("mika2go", "Wreath"), ("mika2go", "PIDRA"), ("mika2go", "Trellis"),
        ("mika2go", "solis-browser"), ("mika2go", "dotfiles"),
        ("mika2go", "Crosshair-Hype"),
        ("drvcvt", "eddy"), ("drvcvt", "boltsnap"),
    ]))
    for name, svg in cards.items():
        target = out / f"{name}.svg"
        if target.exists() and target.read_text(encoding="utf-8") == svg:
            print(f"{name}: unchanged")
            continue
        target.write_text(svg, encoding="utf-8")
        written.append(name)
        print(f"{name}: wrote {target}")

    # GitHub proxies README images through camo, and SVG served from a
    # repository comes back as text/plain often enough that the image simply
    # does not render. PNG always does, so that is what the README points at.
    for name in written:
        source, png = out / f"{name}.svg", out / f"{name}.png"
        try:
            subprocess.run(
                ["rsvg-convert", "-b", "#0d1117", "-z", "2", "-o", str(png), str(source)],
                check=True,
            )
            print(f"{name}: wrote {png}")
        except (OSError, subprocess.CalledProcessError) as err:
            sys.exit(f"could not rasterise {source}: {err}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
