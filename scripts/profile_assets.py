#!/usr/bin/env python3
"""
Generates every graphic used by the profile README.

  python scripts/profile_assets.py static   -> banner, contact buttons, tech-stack
  python scripts/profile_assets.py stats    -> stats card, languages card, activity chart
                                               (needs GH_TOKEN; used by the GitHub Action)
  python scripts/profile_assets.py reset    -> neutral placeholder cards (no numbers)

Only the Python standard library is used. Every image is a self-contained SVG
written into ./assets, so the README never depends on a third-party image service.
"""
import datetime as dt
import json
import math
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

USER = (
    os.environ.get("GITHUB_USER")
    or os.environ.get("GITHUB_REPOSITORY_OWNER")
    or "himanshuchandrakar465"
)

# ----------------------------------------------------------------------------
# Edit these to change what the graphics say
# ----------------------------------------------------------------------------
NAME = "Himanshu Chandrakar"
ROLE = "AI / ML Engineer"
TAGLINE = "I build LLM applications, RAG pipelines and agentic workflows."

# (category, accent colour key, [skills])
STACK = [
    ("Languages", "blue", ["Python", "SQL", "C++"]),
    ("Machine Learning", "teal", ["Scikit-learn", "Feature Engineering", "Model Evaluation"]),
    ("Deep Learning", "violet", ["TensorFlow", "Keras", "PyTorch", "CNNs", "RNNs / LSTMs",
                                 "Transformers", "GANs", "Transfer Learning"]),
    ("Generative AI", "pink", ["LangChain", "LangGraph", "LangSmith", "RAG", "Hugging Face",
                               "Prompt Engineering", "AI Agents", "Groq"]),
    ("Vector Search", "amber", ["Pinecone", "Embeddings", "Semantic Search"]),
    ("Data & Tools", "blue", ["Git", "GitHub", "Docker", "Streamlit", "Jupyter", "OpenCV",
                              "NumPy", "Pandas", "Matplotlib"]),
]

# Notebook files are Python code; count them as Python in the language chart.
LANGUAGE_ALIASES = {"Jupyter Notebook": "Python"}
LANGUAGE_EXCLUDE = set()          # e.g. {"HTML", "CSS"}
FALLBACK_LANG_COLOURS = {"Python": "#3572A5"}

# ----------------------------------------------------------------------------
# Design tokens
# ----------------------------------------------------------------------------
C = dict(
    bg0="#0A0F1E", bg1="#101D3F", card="#0F1730", line="#24304F", rule="#1B2644",
    text="#E8EEFB", sub="#B4C0DB", muted="#8190B3",
    blue="#5B8CFF", teal="#22D3B6", violet="#A78BFA", pink="#F472B6", amber="#FBBF24",
)
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body, title, desc="", defs="", style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">\n'
        f"<title>{esc(title)}</title>\n<desc>{esc(desc)}</desc>\n"
        f"<defs>{defs}</defs>\n"
        f"<style>text{{font-family:{FONT};}}{style}</style>\n"
        f"{body}\n</svg>\n"
    )


def card_bg(w, h, r=14):
    return (f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{r}" '
            f'fill="{C["card"]}" stroke="{C["line"]}"/>')


def write(name, content):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / name
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


# ----------------------------------------------------------------------------
# Text measuring (approximate; the chips keep generous padding)
# ----------------------------------------------------------------------------
def text_width(s, size, weight=500):
    try:
        from PIL import ImageFont
        for p in ("/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            if os.path.exists(p):
                f = ImageFont.truetype(p, 100)
                scale = 1.0 if "FreeSans" in p else 0.9
                return f.getlength(s) / 100 * size * scale
    except Exception:
        pass
    return len(s) * size * 0.56


# ----------------------------------------------------------------------------
# STATIC ASSETS
# ----------------------------------------------------------------------------
def banner():
    W, H = 830, 240
    layers, xs = [3, 5, 5, 3], [590, 660, 730, 800]
    gaps = {3: 50, 5: 34}
    pos = []
    for n, x in zip(layers, xs):
        pos.append([(x, 120 + (i - (n - 1) / 2) * gaps[n]) for i in range(n)])

    edges = []
    for a, b in zip(pos, pos[1:]):
        for (x1, y1) in a:
            for (x2, y2) in b:
                edges.append(f'<line x1="{x1}" y1="{y1:.1f}" x2="{x2}" y2="{y2:.1f}"/>')
    glows, nodes = [], []
    for li, layer in enumerate(pos):
        colour = C["teal"] if li == len(pos) - 1 else C["blue"]
        for (x, y) in layer:
            glows.append(f'<circle class="g" style="animation-delay:{li*0.45:.2f}s" '
                         f'cx="{x}" cy="{y:.1f}" r="12" fill="{colour}"/>')
            nodes.append(f'<circle cx="{x}" cy="{y:.1f}" r="5" fill="{C["bg0"]}" '
                         f'stroke="{colour}" stroke-width="1.8"/>')

    defs = f"""
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{C['bg0']}"/><stop offset="1" stop-color="{C['bg1']}"/>
</linearGradient>
<radialGradient id="halo" cx="0.84" cy="0.5" r="0.5">
  <stop offset="0" stop-color="{C['blue']}" stop-opacity="0.26"/>
  <stop offset="1" stop-color="{C['blue']}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="ac" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{C['blue']}"/><stop offset="1" stop-color="{C['teal']}"/>
</linearGradient>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>"""
    style = (".g{opacity:0;animation:fp 4.8s ease-in-out infinite}"
             "@keyframes fp{0%{opacity:0}9%{opacity:.55}26%{opacity:0}100%{opacity:0}}"
             "@media (prefers-reduced-motion:reduce){.g{animation:none;opacity:.14}}")
    body = f"""
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#halo)"/>
  <g stroke="{C['blue']}" stroke-opacity="0.17" stroke-width="1">{''.join(edges)}</g>
  {''.join(glows)}
  {''.join(nodes)}
</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{C['line']}"/>
<rect x="56" y="60" width="40" height="4" rx="2" fill="url(#ac)"/>
<text x="56" y="116" font-size="40" font-weight="700" fill="{C['text']}" letter-spacing="-0.6">{esc(NAME)}</text>
<text x="56" y="156" font-size="22" font-weight="600" fill="url(#ac)">{esc(ROLE)}</text>
<text x="56" y="190" font-size="15" fill="{C['sub']}">{esc(TAGLINE)}</text>"""
    write("banner.svg", svg(W, H, body, f"{NAME}, {ROLE}", TAGLINE, defs, style))


GITHUB_MARK = ("M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49"
               "-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 "
               "1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59"
               ".82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 "
               "1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 "
               "3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42"
               "-3.58-8-8-8z")


def buttons():
    H = 40
    icons = {
        "email": (
            f'<rect x="1.5" y="3" width="13" height="10" rx="2" fill="none" stroke="{C["teal"]}" stroke-width="1.5"/>'
            f'<path d="M2.2 4.6 8 9l5.8-4.4" fill="none" stroke="{C["teal"]}" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'),
        "linkedin": (
            f'<rect width="16" height="16" rx="3.2" fill="{C["blue"]}"/>'
            f'<text x="8" y="12.2" font-size="10.5" font-weight="800" text-anchor="middle" '
            f'fill="{C["bg0"]}">in</text>'),
        "github": f'<path d="{GITHUB_MARK}" fill="{C["text"]}"/>',
    }
    labels = {"email": "Email", "linkedin": "LinkedIn", "github": "GitHub"}
    for key, icon in icons.items():
        W = round(20 + 16 + 10 + text_width(labels[key], 14) * 1.08 + 22)
        body = (f'{card_bg(W, H, 10)}<g transform="translate(20 12)">{icon}</g>'
                f'<text x="46" y="25" font-size="14" font-weight="600" fill="{C["text"]}">{labels[key]}</text>')
        write(f"btn-{key}.svg", svg(W, H, body, labels[key]))


def tech_stack():
    W, PAD, LABEL_W = 830, 28, 140
    x0, x_max = PAD + LABEL_W, W - PAD
    chip_h, gap_x, gap_y, cat_gap = 30, 8, 8, 20
    y = PAD
    parts, total = [], 0
    names = []
    for ci, (cat, colour, skills) in enumerate(STACK):
        names.append(f"{cat}: {', '.join(skills)}")
        if ci:
            parts.append(f'<line x1="{PAD}" y1="{y - cat_gap/2:.1f}" x2="{W-PAD}" y2="{y - cat_gap/2:.1f}" '
                         f'stroke="{C["rule"]}"/>')
        parts.append(f'<text x="{PAD}" y="{y + 20}" font-size="14" font-weight="600" fill="{C["sub"]}">{esc(cat)}</text>')
        x = x0
        for s in skills:
            w = text_width(s, 13.5) + 38
            if x + w > x_max:
                x, y = x0, y + chip_h + gap_y
            parts.append(
                f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{chip_h}" rx="8" fill="#131E3D" stroke="{C["line"]}"/>'
                f'<circle cx="{x+15:.1f}" cy="{y+chip_h/2}" r="3.5" fill="{C[colour]}"/>'
                f'<text x="{x+27:.1f}" y="{y+19.5}" font-size="13.5" font-weight="500" fill="{C["text"]}">{esc(s)}</text>')
            x += w + gap_x
        y += chip_h + cat_gap
    H = int(y - cat_gap + PAD)
    body = card_bg(W, H, 16) + "".join(parts)
    write("tech-stack.svg", svg(W, H, body, "Tech stack", "; ".join(names)))


# ----------------------------------------------------------------------------
# LIVE STATS
# ----------------------------------------------------------------------------
QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def gql(token):
    payload = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                "https://api.github.com/graphql", data=payload,
                headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                         "User-Agent": "profile-assets"})
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.load(r)
            if data.get("errors"):
                raise RuntimeError(data["errors"])
            return data["data"]["user"]
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"GitHub API request failed: {last}")


def summarise(user):
    repos = user["repositories"]["nodes"]
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]

    sizes, colours = {}, {}
    for repo in repos:
        for e in repo["languages"]["edges"]:
            raw = e["node"]["name"]
            name = LANGUAGE_ALIASES.get(raw, raw)
            if name in LANGUAGE_EXCLUDE:
                continue
            sizes[name] = sizes.get(name, 0) + e["size"]
            if raw == name and e["node"]["color"]:
                colours[name] = e["node"]["color"]
    for name in sizes:
        colours.setdefault(name, FALLBACK_LANG_COLOURS.get(name, "#8190B3"))
    total = sum(sizes.values()) or 1
    langs = [(n, b / total * 100, colours[n]) for n, b in sorted(sizes.items(), key=lambda kv: -kv[1])]

    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i == 0:          # today may simply not have a contribution yet
            continue
        else:
            break

    weekly = []
    for w in cal["weeks"]:
        weekly.append((w["contributionDays"][0]["date"], sum(d["contributionCount"] for d in w["contributionDays"])))

    return dict(
        contributions=cal["totalContributions"], commits=cc["totalCommitContributions"],
        prs=cc["totalPullRequestContributions"], repos=user["repositories"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in repos), followers=user["followers"]["totalCount"],
        current=current, longest=longest, langs=langs, weekly=weekly,
    )


def stats_card(d):
    W, H = 407, 252
    ph = d is None
    v = (lambda k: "–") if ph else (lambda k: f"{d[k]:,}")
    cols = [24, 148, 272]
    out = [card_bg(W, H),
           f'<text x="24" y="36" font-size="15" font-weight="600" fill="{C["text"]}">GitHub at a glance</text>']

    def group(label, y_label, y_num, items):
        out.append(f'<text x="24" y="{y_label}" font-size="11.5" fill="{C["muted"]}">{label}</text>')
        for x, (text, key) in zip(cols, items):
            out.append(f'<text x="{x}" y="{y_num}" font-size="28" font-weight="700" fill="{C["text"]}">{v(key)}</text>'
                       f'<text x="{x}" y="{y_num+20}" font-size="12" fill="{C["sub"]}">{text}</text>')

    group("Last 12 months", 62, 94, [("Contributions", "contributions"), ("Commits", "commits"),
                                     ("Pull requests", "prs")])
    group("All time", 140, 172, [("Public repos", "repos"), ("Stars earned", "stars"), ("Followers", "followers")])
    out.append(f'<line x1="24" y1="204" x2="{W-24}" y2="204" stroke="{C["rule"]}"/>')

    def streak(x, key, label):
        val = "–" if ph else f"{d[key]} day{'s' if d[key] != 1 else ''}"
        out.append(f'<text x="{x}" y="230" font-size="14"><tspan font-weight="700" fill="{C["teal"]}">{val}</tspan>'
                   f'<tspan dx="7" font-size="12" fill="{C["sub"]}">{label}</tspan></text>')

    streak(24, "current", "current streak")
    streak(214, "longest", "longest in 12 mo")
    if ph:
        out.append(f'<text x="{W-24}" y="36" text-anchor="end" font-size="11" fill="{C["muted"]}">updates automatically</text>')
    write("stats.svg", svg(W, H, "".join(out), "GitHub at a glance",
                           "Contributions, commits, pull requests, repositories, stars, followers and streaks."))


def languages_card(d):
    W, H = 407, 252
    ph = d is None or not d["langs"]
    langs = [] if ph else d["langs"]
    top = langs[:8]
    if len(langs) > 8:
        top[-1] = ("Other", sum(p for _, p, _ in langs[7:]), "#8190B3")
    out = [card_bg(W, H),
           f'<text x="24" y="36" font-size="15" font-weight="600" fill="{C["text"]}">Top languages</text>']
    bar_x, bar_w, bar_y = 24, W - 48, 54
    clip = f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" rx="5"/></clipPath>'
    out.append(clip)
    out.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" rx="5" fill="{C["rule"]}"/>')
    if ph:
        msg = "Filled in by the first workflow run" if d is None else "No language data yet"
        out.append(f'<text x="{W/2}" y="150" text-anchor="middle" font-size="13" fill="{C["muted"]}">{msg}</text>')
    else:
        x = bar_x
        segs = []
        for _, pct, col in top:
            w = bar_w * pct / sum(p for _, p, _ in top)
            segs.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w + 0.6:.2f}" height="10" fill="{col}"/>')
            x += w
        out.append(f'<g clip-path="url(#bar)">{"".join(segs)}</g>')
        col_x, col_w = [24, 210], 173
        for i, (name, pct, col) in enumerate(top):
            cx = col_x[i % 2]
            cy = 108 + (i // 2) * 36
            label = name if len(name) <= 14 else name[:13] + "…"
            out.append(f'<circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{col}"/>'
                       f'<text x="{cx+17}" y="{cy}" font-size="13" font-weight="500" fill="{C["text"]}">{esc(label)}</text>'
                       f'<text x="{cx+col_w}" y="{cy}" text-anchor="end" font-size="12" fill="{C["sub"]}">'
                       f'{pct:.1f}%</text>')
    out.append(f'<text x="24" y="{H-20}" font-size="11" fill="{C["muted"]}">By code size · public repositories, forks excluded</text>')
    write("languages.svg", svg(W, H, "".join(out), "Top languages",
                               "Share of code by language across public repositories."))


def smooth_path(pts):
    n = len(pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    dx = [xs[i + 1] - xs[i] for i in range(n - 1)]
    m = [(ys[i + 1] - ys[i]) / dx[i] for i in range(n - 1)]
    t = [0.0] * n
    t[0], t[-1] = m[0], m[-1]
    for i in range(1, n - 1):
        t[i] = 0 if m[i - 1] * m[i] <= 0 else (m[i - 1] + m[i]) / 2
    for i in range(n - 1):
        if m[i] == 0:
            t[i] = t[i + 1] = 0
        else:
            a, b = t[i] / m[i], t[i + 1] / m[i]
            s = a * a + b * b
            if s > 9:
                tau = 3 / math.sqrt(s)
                t[i], t[i + 1] = tau * a * m[i], tau * b * m[i]
    d = f"M{xs[0]:.1f},{ys[0]:.1f}"
    for i in range(n - 1):
        h = dx[i]
        d += (f" C{xs[i]+h/3:.1f},{ys[i]+t[i]*h/3:.1f} {xs[i+1]-h/3:.1f},{ys[i+1]-t[i+1]*h/3:.1f} "
              f"{xs[i+1]:.1f},{ys[i+1]:.1f}")
    return d


def activity_chart(d):
    W, H = 830, 252
    L, R, T, B = 52, W - 28, 76, 196      # plot box
    out = [card_bg(W, H, 16),
           f'<text x="28" y="38" font-size="15" font-weight="600" fill="{C["text"]}">Contribution activity</text>']
    defs = (f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{C["blue"]}" stop-opacity="0.38"/>'
            f'<stop offset="1" stop-color="{C["blue"]}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{C["blue"]}"/><stop offset="1" stop-color="{C["teal"]}"/></linearGradient>')
    ph = d is None
    weekly = [("", 0)] * 53 if ph else d["weekly"]
    peak = max((c for _, c in weekly), default=0)
    step = 5 if peak > 10 else 2 if peak > 4 else 1
    ymax = max(step * 2, math.ceil(peak / step) * step)
    if ymax % 2:
        ymax += 1
    for frac in (0, 0.5, 1):
        y = B - (B - T) * frac
        dash = "" if frac == 0 else 'stroke-dasharray="3 5"'
        out.append(f'<line x1="{L}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" stroke="{C["rule"]}" {dash}/>'
                   f'<text x="{L-10}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="{C["muted"]}">{int(ymax*frac)}</text>')

    n = len(weekly)
    pts = [(L + (R - L) * i / (n - 1), B - (B - T) * c / ymax) for i, (_, c) in enumerate(weekly)]
    if ph:
        out.append(f'<text x="{(L+R)/2}" y="{(T+B)/2+4}" text-anchor="middle" font-size="13" fill="{C["muted"]}">'
                   f'Chart appears after the first workflow run</text>')
    else:
        line = smooth_path(pts)
        out.append(f'<path d="{line} L{pts[-1][0]:.1f},{B} L{pts[0][0]:.1f},{B} Z" fill="url(#area)"/>'
                   f'<path d="{line}" fill="none" stroke="url(#ln)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="8" fill="{C["teal"]}" fill-opacity="0.22"/>'
                   f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.8" fill="{C["teal"]}"/>')
        # month labels
        last_m, last_x = None, -99
        for i, (date, _) in enumerate(weekly):
            m = date[5:7]
            if m != last_m:
                if pts[i][0] - last_x > 36:
                    name = dt.date.fromisoformat(date).strftime("%b")
                    out.append(f'<text x="{pts[i][0]:.1f}" y="{B+22}" font-size="11" fill="{C["muted"]}">{name}</text>')
                    last_x = pts[i][0]
                last_m = m
        total = f'{d["contributions"]:,}'
        out.append(f'<text x="{W-28}" y="38" text-anchor="end" font-size="13" fill="{C["sub"]}">'
                   f'<tspan font-weight="700" font-size="15" fill="{C["text"]}">{total}</tspan>'
                   f'<tspan dx="6">contributions in the last 12 months</tspan></text>')
    out.append(f'<text x="28" y="58" font-size="11.5" fill="{C["muted"]}">Weekly total</text>')
    write("activity.svg", svg(W, H, "".join(out), "Contribution activity",
                              "Weekly contributions over the last 12 months.", defs))


def placeholder_snake():
    for name, dark in (("snake.svg", False), ("snake-dark.svg", True)):
        W, H = 830, 150
        body = (card_bg(W, H, 16) +
                f'<text x="{W/2}" y="{H/2+5}" text-anchor="middle" font-size="13" fill="{C["muted"]}">'
                f'Contribution snake is generated by the first workflow run</text>')
        write(name, svg(W, H, body, "Contribution snake"))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "static"
    if cmd == "static":
        banner(); buttons(); tech_stack()
    elif cmd == "reset":
        stats_card(None); languages_card(None); activity_chart(None); placeholder_snake()
    elif cmd == "stats":
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("Set GH_TOKEN (the workflow does this automatically).")
        data = summarise(gql(token))
        stats_card(data); languages_card(data); activity_chart(data)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
