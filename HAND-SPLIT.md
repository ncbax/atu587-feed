# Hand-splitting the older issues

The December 2025 – October 2026 issues were first split by a script. Each one is being redone by hand to the same standard as `issues/2026-11/`, which is the model to copy.

## Status

| Issue | Status |
| --- | --- |
| 2026-11 | Done by hand |
| 2026-10 | Done by hand |
| 2026-09 | Done by hand |
| 2026-08 | Done by hand |
| 2026-07 | Done by hand |
| 2026-06 | Done by hand |
| 2026-05 | Done by hand |
| 2026-04 | Done by hand |
| 2026-03 | Done by hand |
| 2026-02 | Done by hand |
| 2026-01 | Done by hand |
| 2025-12 | To do (batch 4) |

## How to redo an issue

1. Work from `issues/YYYY-MM/issue.pdf`. Extract each page with `pdftotext -f N -l N issue.pdf -` and render pages to PNG (`pdftoppm -r 100 -f N -l N -png`) to check the layout: column order, which text belongs to which article, sidebars and boxes.
2. Delete the old automatically generated `NN-*.md` files in that folder (keep `issue.json` and `issue.pdf`).
3. Write one `NN-slug.md` per article, in the order they appear, in the same format as `issues/2026-11/`:
   - front matter: `title`, `author` (if any), `pages` (every page it appears on, in reading order), and `scanned: true` for text read from image pages
   - the article's full text in Markdown, with `##` subheads, lists and tables where the original has them
   - title = kicker + headline when there is one (e.g. "The President's Report: Still No Contract?")
   - join articles that continue on later pages; drop pull quotes (repeated sentences in large type), page headers/footers, "continued on page X" lines, and the cover's table of contents
   - fix words broken by the PDF ("law yers" → "lawyers", hyphenation across lines), but otherwise keep the union's wording, typos and all
4. Image-only pages (`pdftotext` gives almost nothing): render at 150–200 dpi, look at them, and transcribe them by hand with `scanned: true`. Photo pages and puzzles get a short item that says so and points to the PDF (see `issues/2026-11/21-puzzles.md`).
5. Put the standing notices (meeting schedule, CBA dates, holidays list, crisis lines, CISM, Weingarten, Oath of Obligation, letters policy, address reminder, Retirees Corner if it's only a few lines) into one last item: "Notices: Meetings, Bargaining Dates, Holidays, Hotlines, and More", noting the page for each section.
6. Check the text against the PDF: every article present, nothing duplicated, nothing cut off at a page or column break.
7. Run `pip install markdown && python3 build.py`, check that `feed.xml` parses, update the status table above, and commit with the message "Hand-split YYYY-MM". Push to `main` (GitHub Pages republishes automatically).
