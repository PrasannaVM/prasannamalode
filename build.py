#!/usr/bin/env python3
"""
Static site generator for prasannamalode.in

    python3 build.py

Reads  content/*.md  (front matter + markdown)
Writes articles/<id>.html, assets/articles-data.js, articles.json,
       feed.xml, sitemap.xml, assets/og/<id>.png

No third-party dependencies (Pillow is optional, used only for OG images).
"""
import datetime as dt
import html
import json
import os
import re
import sys

SITE = "https://prasannamalode.in"
AUTHOR = "Prasanna Malode"
ROLE = "Global Head — DevSecOps · Cybersecurity · IT Operations"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_V = "20260913b"  # bump to force browsers to refetch CSS/JS
CONTENT = os.path.join(HERE, "content")
ARTICLES_DIR = os.path.join(HERE, "articles")
ASSETS = os.path.join(HERE, "assets")

# Stand-alone guides that are not generated from markdown.
GUIDES = [
    dict(id="cicd-jenkins-azure-docker", kind="guide",
         title="CI/CD Pipeline: Complete Training Guide — Jenkins, Azure & Docker",
         tag="DevOps", date="2021-01-01", display_date="2021", read="Training guide",
         summary="Step-by-step guide covering CI/CD foundations, Jenkins in Docker, Azure Container Registry, AKS deployment, Jenkinsfile authoring, and troubleshooting. No prior CI/CD experience assumed.",
         file="articles/cicd-jenkins-azure-docker.html"),
    dict(id="git-hands-on-guide", kind="guide",
         title="Git Fundamentals for DevOps Engineers — Hands-On Training Guide",
         tag="DevOps", date="2010-01-01", display_date="2010", read="Training guide",
         summary="A comprehensive hands-on guide to Git for DevOps engineers: version control, architecture, branching strategies, SSH setup, and real-world workflows.",
         file="articles/Git_HandsOn_Guide.html"),
    dict(id="git-cheatsheet", kind="guide",
         title="Git Command Cheat Sheet — DevOps Quick Reference",
         tag="DevOps", date="2010-01-01", display_date="2010", read="Cheat sheet",
         summary="A searchable quick-reference covering every Git command: setup, branching, remotes, undo, tags, workflows, and troubleshooting.",
         file="articles/Git_CheatSheet.html"),
]

# ----------------------------------------------------------------------------
# Minimal Markdown → HTML (headings, paragraphs, lists, blockquotes, fenced code,
# inline code, bold, italics, links, hr). Enough for essays; deliberately small.
# ----------------------------------------------------------------------------
def inline(text):
    text = html.escape(text, quote=False)
    # code spans first so their contents are not further transformed
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append("<code>" + p[1:-1] + "</code>")
            continue
        p = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
        p = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", p)
        out.append(p)
    return "".join(out)


def md_to_html(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, i, n = [], 0, len(lines)
    para = []

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(s.strip() for s in para)) + "</p>")
            para.clear()

    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            flush_para(); i += 1; continue
        if s.startswith("```"):
            flush_para()
            lang = s[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush_para()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            i += 1; continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            flush_para(); out.append("<hr>"); i += 1; continue
        if s.startswith(">"):
            flush_para()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip()); i += 1
            out.append("<blockquote><p>" + inline(" ".join(b for b in buf if b)) + "</p></blockquote>")
            continue
        if re.match(r"^[-*+]\s+", s) or re.match(r"^\d+[.)]\s+", s):
            flush_para()
            ordered = bool(re.match(r"^\d+[.)]\s+", s))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n:
                t = lines[i].strip()
                if not t:
                    # allow a blank line inside a list only if the next line is another item
                    if i + 1 < n and (re.match(r"^[-*+]\s+", lines[i + 1].strip()) or re.match(r"^\d+[.)]\s+", lines[i + 1].strip())):
                        i += 1; continue
                    break
                mm = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)$", t)
                if not mm:
                    if items and lines[i].startswith(("  ", "\t")):
                        items[-1] += " " + t; i += 1; continue
                    break
                items.append(mm.group(1)); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(it)}</li>" for it in items) + f"</{tag}>")
            continue
        para.append(line); i += 1
    flush_para()
    return "\n".join(out)


def parse_front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2)


def read_time(md):
    words = len(re.findall(r"\w+", md))
    return f"{max(1, round(words / 220))} min read"


def nice_date(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%b %Y")


def long_date(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y")


def rfc822(iso):
    d = dt.datetime.fromisoformat(iso).replace(tzinfo=dt.timezone.utc)
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")


def slugify(s):
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))


# ----------------------------------------------------------------------------
# Templates
# ----------------------------------------------------------------------------
THEME_INIT = """<script>(function(){try{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"""

FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">"""

ICONS = dict(
    sun='<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32 1.41-1.41"/></svg>',
    moon='<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    menu='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    rss='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11a9 9 0 0 1 9 9M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></svg>',
)


def nav_html(root, current):
    def item(name, label, href):
        cur = ' aria-current="page"' if current == name else ""
        return f'<li><a id="nav-{name}" href="{href}"{cur}>{label}</a></li>'
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="{root}/index.html"><span class="brand-mark" aria-hidden="true">PM</span><span>Prasanna Malode</span></a>
    <nav aria-label="Primary">
      <ul class="nav-links">
        {item('home', 'Home', root + '/index.html#/home')}
        {item('articles', 'Articles', root + '/index.html#/articles')}
        {item('tools', 'Tools', root + '/index.html#/tools')}
        {item('about', 'About', root + '/index.html#/about')}
      </ul>
    </nav>
    <div class="nav-actions">
      <a class="icon-btn" href="{root}/feed.xml" title="RSS feed" aria-label="RSS feed">{ICONS['rss']}</a>
      <button class="icon-btn theme-toggle" type="button" title="Toggle dark mode" aria-label="Toggle dark mode">{ICONS['sun']}{ICONS['moon']}</button>
      <button class="icon-btn menu-btn" type="button" aria-label="Menu" aria-expanded="false">{ICONS['menu']}</button>
    </div>
  </div>
</header>"""


def footer_html(root):
    return f"""<footer class="footer">
  <div class="wrap footer-grid">
    <div>
      <a class="brand" href="{root}/index.html"><span class="brand-mark" aria-hidden="true">PM</span><span>Prasanna Malode</span></a>
      <div style="margin-top:8px">DevSecOps · Cybersecurity · IT Operations · Bengaluru, India</div>
      <div style="margin-top:4px">© <span data-year>2026</span> Prasanna Malode. Opinions are my own.</div>
    </div>
    <div class="footer-links">
      <a href="{root}/index.html#/articles">Articles</a>
      <a href="{root}/index.html#/tools">Tools</a>
      <a href="{root}/index.html#/about">About</a>
      <a href="https://linkedin.com/in/prasannamalode" target="_blank" rel="noopener me">LinkedIn</a>
      <a href="mailto:malode.prasanna@gmail.com">Email</a>
      <a href="{root}/feed.xml">RSS</a>
    </div>
  </div>
</footer>"""


def head_html(title, description, canonical, root, og_image, extra=""):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#faf8f4" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14151a" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="{root}/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}/assets/apple-touch-icon.png">
<link rel="manifest" href="{root}/manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Prasanna Malode — Articles" href="{SITE}/feed.xml">
<meta property="og:site_name" content="Prasanna Malode">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title, quote=True)}">
<meta name="twitter:description" content="{html.escape(description, quote=True)}">
<meta name="twitter:image" content="{og_image}">
{extra}
{THEME_INIT}
{FONTS}
<link rel="stylesheet" href="{root}/assets/site.css?v={ASSET_V}">"""


def article_page(a, all_essays, series_map):
    root = ".."
    url = f"{SITE}/{a['file']}"
    og = f"{SITE}/assets/og/{a['id']}.png"
    idx = [e["id"] for e in all_essays].index(a["id"])
    newer = all_essays[idx - 1] if idx > 0 else None
    older = all_essays[idx + 1] if idx + 1 < len(all_essays) else None

    ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["summary"],
        "datePublished": a["date"], "dateModified": a.get("updated", a["date"]),
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/index.html#/about", "jobTitle": ROLE},
        "publisher": {"@type": "Person", "name": AUTHOR},
        "mainEntityOfPage": url, "image": og, "keywords": a["tag"],
    }
    if a.get("series"):
        ld["isPartOf"] = {"@type": "CreativeWorkSeries", "name": a["series"]}
    extra = '<meta property="og:type" content="article">\n' \
            f'<meta property="article:published_time" content="{a["date"]}">\n' \
            f'<meta property="article:author" content="{AUTHOR}">\n' \
            f'<meta property="article:section" content="{html.escape(a["tag"], quote=True)}">\n' \
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'

    series_html = ""
    if a.get("series"):
        parts = series_map[a["series"]]
        items = "".join(
            f'<li class="{"current" if p["id"] == a["id"] else ""}"><a href="{root}/{p["file"]}">{html.escape(p["title"])}</a></li>'
            for p in parts)
        series_html = f"""<aside class="series-box" aria-label="Series navigation">
  <div class="eyebrow">Series · Part {a['part']} of {len(parts)}</div>
  <strong>{html.escape(a['series'])}</strong>
  <ol>{items}</ol>
</aside>"""

    def pager_link(p, cls, label):
        if not p:
            return "<span></span>"
        return f'<a class="{cls}" href="{root}/{p["file"]}"><div class="dir">{label}</div><div class="title">{html.escape(p["title"])}</div></a>'

    toc_inline = '<nav class="toc-inline" data-toc aria-label="Contents"><div class="eyebrow">In this article</div><div data-toc-list></div></nav>'
    toc_side = '<nav class="toc-side" data-toc aria-label="Contents"><div class="eyebrow">In this article</div><div data-toc-list></div></nav>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_html(a['title'] + ' — ' + AUTHOR, a['summary'], url, root, og, extra)}
</head>
<body data-root="{root}">
<div class="progress" aria-hidden="true"></div>
{nav_html(root, 'articles')}
<main id="main">
  <article>
    <header class="article-head">
      <div class="wrap-read fade-up">
        <a class="tag" href="{root}/index.html#/articles?tag={html.escape(a['tag'], quote=True)}">{html.escape(a['tag'])}</a>
        <h1>{html.escape(a['title'])}</h1>
        <div class="meta">
          <img class="avatar" src="{root}/assets/photo-sm.jpg" alt="" width="26" height="26">
          <span>{AUTHOR}</span>
          <span aria-hidden="true">·</span>
          <time datetime="{a['date']}">{long_date(a['date'])}</time>
          <span aria-hidden="true">·</span>
          <span>{html.escape(a['read'])}</span>
        </div>
        <p class="lede">{html.escape(a['summary'])}</p>
      </div>
    </header>
    <div class="wrap" style="max-width:calc(var(--max-read) + 220px + 56px + 48px)">
      <div class="article-layout">
        <div>
          {series_html}
          {toc_inline}
          <div class="prose">
{a['body_html']}
          </div>
          <footer class="article-foot">
            <div class="share">
              <span class="label">Share</span>
              <button class="btn btn-secondary btn-sm" type="button" data-share="linkedin">LinkedIn</button>
              <button class="btn btn-secondary btn-sm" type="button" data-share="x">X</button>
              <button class="btn btn-secondary btn-sm" type="button" data-share="email">Email</button>
              <button class="btn btn-secondary btn-sm" type="button" data-share="copy">Copy link</button>
              <button class="btn btn-secondary btn-sm" type="button" data-share="native">Share…</button>
            </div>
            <div class="author-card">
              <img src="{root}/assets/photo-sm.jpg" alt="{AUTHOR}" width="64" height="64">
              <div>
                <div class="name">{AUTHOR}</div>
                <div class="role">{ROLE} · Bengaluru, India</div>
                <p>Two decades in release engineering, IT operations and security, now leading a 20-person global DevSecOps, cybersecurity and IT operations organisation. I write about making speed, security and reliability the same conversation. <a href="{root}/index.html#/about">More about me</a>.</p>
              </div>
            </div>
            <nav class="pager" aria-label="More articles">
              {pager_link(older, 'prev', '← Older')}
              {pager_link(newer, 'next', 'Newer →')}
            </nav>
          </footer>
        </div>
        {toc_side}
      </div>
    </div>
  </article>
</main>
{footer_html(root)}
<script src="{root}/assets/articles-data.js?v={ASSET_V}" defer></script>
<script src="{root}/assets/site.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


# ----------------------------------------------------------------------------
# OG image generation (optional, needs Pillow)
# ----------------------------------------------------------------------------
def make_og(a, out_path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return False
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (250, 248, 244))
    d = ImageDraw.Draw(im)
    # left accent band
    d.rectangle([0, 0, 18, H], fill=(26, 82, 118))

    def font(size, bold=False, serif=False):
        cands = []
        if serif:
            cands += ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
        cands += ["/usr/share/fonts/truetype/lato/Lato-Bold.ttf" if bold else "/usr/share/fonts/truetype/lato/Lato-Regular.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for c in cands:
            if os.path.exists(c):
                try:
                    return ImageFont.truetype(c, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    tag_f = font(26, bold=True)
    title_f = font(58, bold=True, serif=True)
    small_f = font(28)
    name_f = font(32, bold=True)

    x = 72
    d.text((x, 70), (a.get("tag") or "").upper(), font=tag_f, fill=(26, 82, 118))

    # wrap title
    words = a["title"].split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=title_f) > W - x - 80:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    if len(lines) > 4:
        lines = lines[:4]; lines[-1] = lines[-1].rstrip(".,") + "…"
    y = 130
    for ln in lines:
        d.text((x, y), ln, font=title_f, fill=(26, 24, 20)); y += 72

    d.line([x, H - 130, W - 80, H - 130], fill=(232, 226, 217), width=2)
    d.text((x, H - 105), AUTHOR, font=name_f, fill=(26, 24, 20))
    date_txt = a["display_date"] if "display_date" in a else nice_date(a["date"])
    d.text((x, H - 62), "prasannamalode.in" + ("  ·  " + date_txt if date_txt else ""), font=small_f, fill=(111, 105, 94))
    # photo circle
    try:
        photo = Image.open(os.path.join(ASSETS, "photo.jpg")).convert("RGB")
        s = 150
        ph = photo.resize((s, int(s * photo.height / photo.width)))
        ph = ph.crop((0, 0, s, s))
        mask = Image.new("L", (s, s), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, s - 1, s - 1], fill=255)
        im.paste(ph, (W - 80 - s, H - 130 - s - 24), mask)
    except Exception:
        pass
    im.save(out_path, optimize=True)
    return True


# ----------------------------------------------------------------------------
def main():
    essays = []
    for fn in sorted(os.listdir(CONTENT)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(CONTENT, fn), encoding="utf-8").read()
        meta, body = parse_front_matter(raw)
        a = dict(meta)
        a["id"] = a.get("id") or slugify(fn[:-3])
        a["kind"] = "essay"
        a["file"] = f"articles/{a['id']}.html"
        a["read"] = a.get("read") or read_time(body)
        a["display_date"] = nice_date(a["date"])
        if "part" in a:
            a["part"] = int(a["part"])
        if "featured" in a:
            a["featured"] = str(a["featured"]).lower() in ("true", "yes", "1")
        a["body_md"] = body
        essays.append(a)
    essays.sort(key=lambda x: (x["date"], x.get("part", 0)), reverse=True)

    series_map = {}
    for a in essays:
        if a.get("series"):
            series_map.setdefault(a["series"], []).append(a)
    for k in series_map:
        series_map[k].sort(key=lambda x: x.get("part", 0))

    os.makedirs(ARTICLES_DIR, exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "og"), exist_ok=True)
    for a in essays:
        a["body_html"] = md_to_html(a["body_md"])
        with open(os.path.join(HERE, a["file"]), "w", encoding="utf-8") as f:
            f.write(article_page(a, essays, series_map))
        make_og(a, os.path.join(ASSETS, "og", a["id"] + ".png"))
    make_og(dict(title="DevSecOps, cybersecurity and IT leadership, written from the inside.", tag="prasannamalode.in", date="2026-01-01", display_date=""),
            os.path.join(ASSETS, "og", "site.png"))

    public_keys = ["id", "kind", "title", "tag", "date", "display_date", "read", "summary", "file", "series", "part", "featured"]
    data = [{k: a[k] for k in public_keys if k in a} for a in essays] + \
           [{k: g[k] for k in public_keys if k in g} for g in GUIDES]
    with open(os.path.join(ASSETS, "articles-data.js"), "w", encoding="utf-8") as f:
        f.write("/* generated by build.py — do not edit by hand */\nwindow.ARTICLES = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    with open(os.path.join(HERE, "articles.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # RSS
    items = []
    for a in essays:
        items.append(f"""  <item>
    <title>{html.escape(a['title'])}</title>
    <link>{SITE}/{a['file']}</link>
    <guid isPermaLink="true">{SITE}/{a['file']}</guid>
    <pubDate>{rfc822(a['date'])}</pubDate>
    <category>{html.escape(a['tag'])}</category>
    <description>{html.escape(a['summary'])}</description>
    <content:encoded><![CDATA[{a['body_html']}]]></content:encoded>
  </item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
  <title>Prasanna Malode — Articles</title>
  <link>{SITE}/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>DevSecOps transformation, cybersecurity leadership, AI governance and building high-performing engineering teams.</description>
  <language>en</language>
  <lastBuildDate>{rfc822(essays[0]['date']) if essays else ''}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""
    open(os.path.join(HERE, "feed.xml"), "w", encoding="utf-8").write(rss)

    # Sitemap
    today = dt.date.today().isoformat()
    urls = [(f"{SITE}/", today, "1.0")]
    urls += [(f"{SITE}/{a['file']}", a["date"], "0.8") for a in essays]
    urls += [(f"{SITE}/{g['file']}", g["date"], "0.6") for g in GUIDES]
    tools_dir = os.path.join(HERE, "tools")
    if os.path.isdir(tools_dir):
        for fn in sorted(os.listdir(tools_dir)):
            if fn.endswith(".html"):
                urls.append((f"{SITE}/tools/{fn}", today, "0.7"))
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, mod, pri in urls:
        sm += f"  <url><loc>{loc}</loc><lastmod>{mod}</lastmod><priority>{pri}</priority></url>\n"
    sm += "</urlset>\n"
    open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8").write(sm)

    print(f"built {len(essays)} essays, {len(GUIDES)} guides, {len(urls)} sitemap urls")


if __name__ == "__main__":
    sys.exit(main())
