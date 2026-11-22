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


if __name__ == "__main__":
    build()
