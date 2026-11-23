#!/usr/bin/env python3
"""Build feed.xml from the article files in issues/<YYYY-MM>/.

Each issue folder holds:
  issue.json   - title, published date, original PDF link
  issue.pdf    - a copy of the newsletter (feed items link to its pages)
  NN-slug.md   - one article each, with a small front-matter header:
                   title, author (optional), pages, scanned (optional)

Run: python3 build.py
"""
import json
import re
from datetime import datetime, timedelta
from email.utils import format_datetime
from html import escape
from pathlib import Path

import markdown

SITE = "https://ncbax.github.io/atu587-feed"
FEED_TITLE = "ATU Local 587 News Review"
FEED_DESC = "Articles from the ATU Local 587 News Review, one item per article."
MAX_ISSUES = 12  # keep the feed to the most recent year

ROOT = Path(__file__).parent


def parse_article(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError(f"{path}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')
        meta[key.strip()] = value
    pages = [int(p) for p in meta["pages"].split(",")]
    return {
        "title": meta["title"],
        "author": meta.get("author", ""),
        "pages": pages,
        "scanned": meta.get("scanned", "").lower() == "true",
        "body": m.group(2).strip(),
    }


def page_label(pages):
    if len(pages) == 1:
        return f"page {pages[0]}"
    if pages == list(range(pages[0], pages[-1] + 1)):
        return f"pages {pages[0]}–{pages[-1]}"
    return "pages " + ", ".join(map(str, pages))


def item_html(article, issue, pdf_url):
    first = article["pages"][0]
    page_link = f"{pdf_url}#page={first}"
    parts = []
    if article["scanned"]:
        parts.append(
            f'<p><em>Read from a scanned image on {page_label(article["pages"])} '
            f"of the PDF, so it may contain errors. "
            f'<a href="{escape(page_link)}">View {page_label(article["pages"])} in the PDF</a>.</em></p>'
        )
    if article["author"]:
        parts.append(f"<p><strong>By {escape(article['author'])}</strong></p>")
    parts.append(markdown.markdown(article["body"], extensions=["tables", "sane_lists"]))
    parts.append(
        f'<hr><p><small>From the {escape(issue["title"])}, {page_label(article["pages"])}. '
        f'<a href="{escape(page_link)}">Open in the PDF</a> · '
        f'<a href="{escape(issue["source_url"])}">Original file on atu587.org</a></small></p>'
    )
    return "\n".join(parts)


def build():
    issue_dirs = sorted(
        (d for d in (ROOT / "issues").iterdir() if (d / "issue.json").exists()),
        reverse=True,
    )[:MAX_ISSUES]

    items = []
    for d in issue_dirs:
        issue = json.loads((d / "issue.json").read_text(encoding="utf-8"))
        published = datetime.fromisoformat(issue["published"])
        pdf_url = f"{SITE}/issues/{d.name}/issue.pdf"
        for i, path in enumerate(sorted(d.glob("[0-9][0-9]-*.md"))):
            art = parse_article(path)
            # Readers sort newest first, so give earlier articles later times
            # to keep the newsletter's own order at the top of the list.
            date = published - timedelta(minutes=i)
            items.append(
                f"""    <item>
      <title>{escape(art["title"])}</title>
      <link>{escape(f"{pdf_url}#page={art['pages'][0]}")}</link>
      <guid isPermaLink="false">atu587-{d.name}-{path.stem}</guid>
      <pubDate>{format_datetime(date)}</pubDate>
{f"      <dc:creator>{escape(art['author'])}</dc:creator>" if art["author"] else ""}
      <category>{escape(issue["title"])}</category>
      <content:encoded><![CDATA[{item_html(art, issue, pdf_url).replace("]]>", "]]]]><![CDATA[>")}]]></content:encoded>
    </item>"""
            )

    now = format_datetime(datetime.now().astimezone())
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{FEED_TITLE}</title>
    <link>{SITE}/</link>
    <description>{FEED_DESC}</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"Wrote feed.xml with {len(items)} items from {len(issue_dirs)} issue(s).")


CSS = """
:root { color-scheme: light; }
body { font-family: Georgia, "Times New Roman", serif; line-height: 1.55; color: #1a1a1a;
       max-width: 42rem; margin: 0 auto; padding: 1.5rem 1rem 4rem; }
h1, h2, h3, nav, .meta, .back, .crumbs, table { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
h1 { font-size: 1.8rem; line-height: 1.2; margin: .5rem 0 .25rem; }
h2.article-title { font-size: 1.4rem; line-height: 1.25; margin: 0 0 .25rem; }
article h2, article h3 { font-size: 1.1rem; margin: 1.5rem 0 .5rem; }
a { color: #0b5394; }
.crumbs { font-size: .9rem; margin: 0; }
.meta { font-size: .85rem; color: #555; margin: 0 0 1rem; }
.note { font-size: .9rem; color: #555; font-style: italic; }
nav.toc { background: #f4f4f4; border-radius: 6px; padding: .75rem 1rem; margin: 1.5rem 0 2rem; }
nav.toc h2 { font-size: 1rem; margin: 0 0 .5rem; }
nav.toc ol { margin: 0; padding-left: 1.5rem; }
nav.toc li { margin: .2rem 0; }
article { border-top: 1px solid #ddd; padding-top: 1.5rem; margin-top: 2rem; }
table { border-collapse: collapse; font-size: .9rem; margin: 1rem 0; display: block; overflow-x: auto; max-width: 100%; }
body { overflow-wrap: anywhere; }
img { max-width: 100%; }
th, td { border: 1px solid #ccc; padding: .3rem .5rem; text-align: left; vertical-align: top; }
blockquote { border-left: 3px solid #ccc; margin-left: 0; padding-left: 1rem; color: #333; }
.back { font-size: .85rem; margin-top: 1rem; }
.issues { list-style: none; padding: 0; }
.issues li { margin: .6rem 0; }
.issues .count { color: #555; font-size: .85rem; }
@media print {
  body { max-width: none; padding: 0; font-size: 11pt; color: #000; }
  a { color: #000; text-decoration: none; }
  .back, .crumbs, .pdf-link, .print-hide { display: none; }
  nav.toc { background: none; border: 1px solid #999; }
  article { page-break-before: always; border-top: none; margin-top: 0; }
  article:first-of-type { page-break-before: auto; }
  h2, h3 { page-break-after: avoid; }
  table { display: table; }
  table, blockquote { page-break-inside: avoid; }
  @page { margin: 2cm; }
}
"""


def html_page(title, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="alternate" type="application/rss+xml" title="{FEED_TITLE}" href="../feed.xml">
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def build_archive():
    """Write archive/index.html plus one archive/YYYY-MM.html per issue."""
    out = ROOT / "archive"
    out.mkdir(exist_ok=True)
    issue_dirs = sorted(
        (d for d in (ROOT / "issues").iterdir() if (d / "issue.json").exists()),
        reverse=True,
    )
    listing = []
    for d in issue_dirs:
        issue = json.loads((d / "issue.json").read_text(encoding="utf-8"))
        pdf = f"../issues/{d.name}/issue.pdf"
        arts = [(p.stem, parse_article(p)) for p in sorted(d.glob("[0-9][0-9]-*.md"))]
        toc = "\n".join(f'<li><a href="#{a_id}">{escape(a["title"])}</a></li>' for a_id, a in arts)
        sections = []
        for a_id, a in arts:
            label = page_label(a["pages"]).capitalize()
            first = a["pages"][0]
            meta = []
            if a["author"]:
                meta.append(f"By {escape(a['author'])}")
            meta.append(f'{label} · <a class="pdf-link" href="{pdf}#page={first}">Open in the PDF</a>')
            note = ""
            if a["scanned"]:
                note = (f'<p class="note">Read from a scanned image on {page_label(a["pages"])} '
                        f"of the PDF, so it may contain errors.</p>")
            body = markdown.markdown(a["body"], extensions=["tables", "sane_lists"])
            sections.append(f"""<article id="{a_id}">
<h2 class="article-title">{escape(a["title"])}</h2>
<p class="meta">{" · ".join(meta)}</p>
{note}
{body}
<p class="back"><a href="#top">Back to top</a></p>
</article>""")
        page = f"""<header id="top">
<p class="crumbs"><a href="index.html">All issues</a></p>
<h1>{escape(issue["title"])}</h1>
<p class="meta">ATU Local 587 · {len(arts)} items · <a class="pdf-link" href="{pdf}">Full PDF</a> · <a class="pdf-link" href="{escape(issue["source_url"])}">Original on atu587.org</a></p>
</header>
<nav class="toc">
<h2>In this issue</h2>
<ol>
{toc}
</ol>
</nav>
{chr(10).join(sections)}
"""
        (out / f"{d.name}.html").write_text(html_page(f"{issue['title']} · ATU Local 587", page), encoding="utf-8")
        listing.append(f'<li><a href="{d.name}.html">{escape(issue["title"])}</a> '
                       f'<span class="count">· {len(arts)} items</span></li>')

    index = f"""<header id="top">
<p class="crumbs"><a href="../">Feed</a></p>
<h1>ATU Local 587 News Review archive</h1>
<p class="meta">Every issue, split into articles. Also available as an <a href="../feed.xml">RSS feed</a>.</p>
</header>
<ul class="issues">
{chr(10).join(listing)}
</ul>
"""
    (out / "index.html").write_text(html_page("ATU Local 587 News Review archive", index), encoding="utf-8")
    print(f"Wrote archive with {len(issue_dirs)} issue page(s).")


if __name__ == "__main__":
    build()
    build_archive()
