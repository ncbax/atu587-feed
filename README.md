# ATU Local 587 News Review feed

An RSS feed of the ATU Local 587 *News Review*, one item per article.

**Subscribe:** https://ncbax.github.io/atu587-feed/feed.xml

## How it's organized

- `issues/YYYY-MM/` holds one issue: `issue.json` (title, date, original link), `issue.pdf` (a copy of the newsletter), and one `NN-slug.md` file per article.
- `build.py` turns those files into `feed.xml`. Run `pip install markdown` and then `python3 build.py`.
- Articles that came from scanned pages are marked `scanned: true` and link to their page in the PDF.

## Adding a new issue

1. Put the PDF's link in `inbox/url.txt` (or use **Actions → Fetch newsletter PDF → Run workflow**). GitHub downloads it into `inbox/`.
2. Split it into article files in a new `issues/YYYY-MM/` folder, move the PDF there as `issue.pdf`, and run `build.py`.
3. Commit. GitHub Pages publishes the updated feed within a minute or two.

The feed keeps the most recent 12 issues.
