# SEO Critics Studio

A web-based SEO analysis platform that crawls a website and audits its
technical and on-page SEO health, built as a B.Sc. Computer Science mini
project. See `docs/SRS_Document.md` for the full Software Requirements
Specification.

No login, no cloud, no database server — everything runs locally with a
single Python process and a SQLite file.

---

## Features

- Enter a URL and the app crawls the site's internal pages (same domain,
  configurable page limit and crawl depth).
- Analyzes each page for: title, meta description, meta robots, canonical
  URL, H1/H2 headings, word count, internal/external/broken links, image
  ALT-tag coverage, HTTPS usage, response time, and page size.
- **Additional technical signals**: mobile-friendly viewport tag,
  structured data (JSON-LD / microdata), Open Graph tags, Twitter Card
  tags, declared page language, image dimension attributes, and
  non-descriptive image filenames.
- **Site-wide keyword insights**: a deterministic word-frequency analysis
  (stopwords removed) surfaces the top keywords each page — and the
  site as a whole — appears to focus on. This is plain text statistics,
  not machine learning.
- **Rule-based recommendations**: a fixed set of threshold checks against
  the scan results (e.g. "3 pages are missing a meta description") is
  turned into a prioritized (High / Medium / Low), filterable action
  list for that specific website. This is deterministic rule-based logic,
  not an AI/ML recommendation engine — see the note in the SRS's
  "Important Requirements" section on why AI features are out of scope.
- Validates `sitemap.xml` and `robots.txt` at the site level.
- Computes an SEO score out of 100 (Metadata 20, Technical SEO 20,
  Images 15, Links 15, Sitemap 10, robots.txt 10, Performance 10) and
  classifies the site into a health level: Excellent / Good / Average /
  Poor / Critical.
- Generates downloadable reports in HTML, CSV, and Excel formats — all
  three now include the recommendations, keyword insights, and advanced
  technical signals alongside the original score breakdown and
  page-level data.
- Keeps a scan history so past audits (including their recommendations)
  can be revisited.
- **Issue Explorer**: every analyzer finding is also expressed as a
  structured, filterable issue (CRITICAL/HIGH/MEDIUM/LOW/INFO) with a
  category, affected URL, and recommendation — filterable by severity,
  category, issue type, or page.
- **Page Details drawer**: click any page (in the Pages table, Issue
  Explorer, Link Graph, Duplicates, robots.txt Inspector, or Performance
  tab) to open a full audit panel for that URL without leaving the
  dashboard.
- **Crawl Overview**: pages discovered/crawled, HTTP status distribution,
  average response time/size, and a pages-per-depth breakdown.
- **Internal Link Graph**: an original SVG visualization (plain
  JavaScript, no charting library) of the crawled site's internal
  linking — node size reflects inbound links, color reflects page
  health, and orphan pages are flagged. Click a node to open Page
  Details.
- **Duplicate content detection**: groups of pages sharing an exact
  title, meta description, or canonical target, plus a deterministic
  "similar content" heuristic based on shared top-keywords (not AI —
  the app doesn't store raw page text).
- **Sitemap vs. crawl coverage**: compares the site's declared
  `sitemap.xml` URLs against what was actually crawled — shown
  objectively as "sitemap only," "crawled only," and "in both."
- **robots.txt Inspector**: parses `User-agent` groups and
  `Disallow`/`Allow` rules, and flags any crawled page that appears to
  be blocked. Uses a clearly-scoped simplified parser (not a full
  RFC 9309 implementation — see the in-app scope note).
- **Performance dashboard**: fastest/slowest/largest pages and
  configurable response-time/size thresholds, using this app's own
  request measurements (not Core Web Vitals, which it doesn't measure).
- **Scan Comparison**: pick any two past scans of the same (or
  different) site and compare overall/category scores and see exactly
  which issues are new, fixed, or unchanged between them.
- **PDF export** (via ReportLab) alongside the existing HTML/CSV/Excel
  reports, with a score summary, category breakdown, crawl stats, top
  issues, and recommendations.
- Improved **Pages table**: search, column sorting, quick filters (200 /
  3xx / 4xx / 5xx / missing title / missing description / broken links /
  missing ALT / slow / large), and pagination.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript (SVG for the link graph — no charting library) |
| Backend | Python 3, FastAPI |
| Database | SQLite |
| Crawling / Parsing | requests, BeautifulSoup4, lxml |
| Reports | openpyxl (Excel), Python `csv`, HTML templating, ReportLab (PDF) |

---

## API Reference

**Existing (unchanged response shape, only additive fields):**

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/scan` | Run a new crawl + full analysis |
| GET | `/api/report/{website_id}` | Full bundle (website, latest report, all pages) |
| GET | `/api/history` | Recent scan history |
| GET | `/api/download/{website_id}/{fmt}` | Download `html`, `csv`, `excel`, or `pdf` |

**New:**

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/issues/{website_id}` | Structured issues; filter by `severity`, `category`, `issue_type`, `page` |
| GET | `/api/page/{website_id}/{page_id}` | Full Page Details (page row + its issues) |
| GET | `/api/crawl/{website_id}` | Crawl Overview stats |
| GET | `/api/link-graph/{website_id}` | Internal link graph nodes/edges |
| GET | `/api/duplicates/{website_id}` | Duplicate title/description/canonical groups + similar-content pairs |
| GET | `/api/sitemap/{website_id}` | Sitemap-vs-crawl coverage |
| GET | `/api/robots/{website_id}` | Parsed robots.txt + blocked-page check |
| GET | `/api/performance/{website_id}` | Response-time/size stats, with `response_threshold_ms` / `size_threshold_kb` query params |
| GET | `/api/compare/{website_id_1}/{website_id_2}` | Compare two scans (score deltas + new/fixed/unchanged issues) |
| POST | `/api/download/{website_id}/pdf` | Explicit PDF download alias (same as the GET route with `fmt=pdf`) |

---

## Project Structure

```
seo-critics-studio/
├── backend/
│   ├── main.py                     # FastAPI app + API endpoints
│   ├── crawler/website_crawler.py  # BFS website crawler (+ redirect chains)
│   ├── analyzers/                  # 10 analyzer modules incl. issue_engine.py
│   ├── scoring/score_calculator.py # 100-point scoring engine
│   ├── recommendations/            # Rule-based recommendation engine
│   ├── reports/                    # HTML / CSV / Excel / PDF report generators
│   ├── database/                   # SQLite schema + data-access helpers
│   └── requirements.txt
├── frontend/
│   ├── index.html                  # Dashboard (single page, tabbed results + drawer)
│   ├── css/style.css
│   └── js/dashboard.js
├── reports_output/                 # Generated reports land here (html/csv/excel/pdf)
└── docs/SRS_Document.md            # Full SRS
```

---

## Database Schema Changes

All changes are **additive and backward-compatible** — existing scan
history is never deleted or altered. `database/db_connection.py` applies
idempotent migrations (`ALTER TABLE ... ADD COLUMN` only if the column
doesn't already exist) on every startup, so an existing `seo_critics.db`
file picks up the new columns automatically.

- **`Pages`** — added `crawl_depth`, `redirect_count`, `redirect_chain`,
  `is_indexable` (on top of the columns already added in the previous
  upgrade).
- **`Reports`** — added `sitemap_urls_json`, `robots_meta_json`,
  `crawl_stats_json`, `pdf_report_path`.
- **`Issues`** *(new table)* — one row per structured issue instance
  (severity, category, affected URL, recommendation, evidence).
- **`PageLinks`** *(new table)* — internal link edges (source URL →
  target URL, broken flag), used by the Internal Link Graph.

---

## Setup & Run

**Requirements:** Python 3.9+

```bash
cd backend
pip install -r requirements.txt

# Run the server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open **http://localhost:8000** in your browser. The dashboard is
served directly by the backend — there is no separate frontend server.

The SQLite database file is created automatically on first run at
`backend/database/seo_critics.db`.

---

## How It Works

1. You enter a URL on the dashboard and click **Run Audit**.
2. The crawler (`crawler/website_crawler.py`) fetches the root page and
   follows same-domain links breadth-first, up to your configured page
   limit and depth.
3. Each fetched page is parsed with BeautifulSoup4 and passed through the
   analyzer modules (metadata, technical SEO, links, images).
4. `sitemap_analyzer.py` and `robots_analyzer.py` check the site-level
   `sitemap.xml` and `robots.txt`.
5. `score_calculator.py` combines all findings into a 100-point score and
   a health level.
6. Everything is saved to SQLite, and HTML/CSV/Excel reports are written
   to `reports_output/`.
7. The dashboard renders the score, category breakdown, sitemap/robots
   checks, and a page-by-page findings table, with download links for
   each report format.

---

## Notes

- The crawler respects same-domain boundaries only; it does not render
  JavaScript, so single-page applications will show limited content.
- Some websites block automated crawlers (bot-detection, rate limiting),
  which will show up as non-200 status codes or empty page content —
  this is expected behavior for an educational crawler, not a bug.
- Broken-link checking is capped per page to keep scan times reasonable
  for a mini project (see `MAX_LINKS_TO_CHECK` in
  `analyzers/internal_link_analyzer.py`).

## Known Limitations (by design, for an educational scope)

- **robots.txt parser** is simplified: it supports multiple `User-agent`
  groups, `Disallow`/`Allow`, a trailing `*` wildcard, and a trailing `$`
  end-anchor — but not mid-pattern wildcards, `crawl-delay`, or the full
  RFC 9309 precedence rules. This is stated in-app wherever robots.txt
  data is shown.
- **"Similar content" detection** uses keyword-overlap (4+ shared
  top-keywords), not full-text similarity — the app doesn't store raw
  page text, to keep the database lightweight. This is a deterministic
  heuristic, not AI.
- **Redirect loop detection** flags a URL that repeats within a single
  page's captured redirect chain; it does not perform a separate
  crawl to exhaustively probe for loops beyond what `requests` already
  followed.
- **Link Graph** uses a deterministic circular layout (not a physics/force
  simulation) so it renders instantly and never freezes the browser,
  even at 50+ pages; graphs beyond 60 pages are capped to the
  most-linked pages plus the root, with a note shown in the UI.
- **Performance dashboard** reflects this app's own request/response
  timing — it does not measure browser-based Core Web Vitals (LCP, CLS,
  INP), which would require a real browser rendering engine.
- **"Pages discovered" vs "pages crawled"** are reported as equal: the
  crawler stops queueing new links once the configured page limit is
  hit, so there's no separate "discovered but not yet crawled" count to
  show.
- **PDF export** requires a fresh scan to be present — scans made before
  this upgrade won't have a PDF until they're re-run (the app degrades
  gracefully with a clear message rather than erroring).
