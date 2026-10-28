"""
main.py

FastAPI application entry point for SEO Critics Studio.
Serves the frontend dashboard and exposes REST endpoints to run scans,
fetch reports, view scan history, and download generated report files.

This version extends the original scan/report/history/download API with
a set of crawler-console features (Issue Explorer, Page Details, Crawl
Overview, Internal Link Graph, Duplicate detection, Sitemap Coverage,
robots.txt Inspector, Performance dashboard, Scan Comparison, and PDF
export) while keeping every original endpoint and response field intact.
"""

import os
import json
from collections import Counter
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup

from database.db_connection import init_db
from database import models

from crawler.website_crawler import crawl_website, normalize_url
from analyzers.url_analyzer import analyze_url
from analyzers.metadata_analyzer import analyze_metadata
from analyzers.technical_seo_analyzer import analyze_technical
from analyzers.internal_link_analyzer import analyze_links
from analyzers.image_seo_analyzer import analyze_images
from analyzers.sitemap_analyzer import analyze_sitemap
from analyzers.robots_analyzer import analyze_robots, is_path_blocked
from analyzers.advanced_seo_analyzer import analyze_advanced
from analyzers.keyword_analyzer import analyze_keywords, merge_site_keywords
from analyzers.issue_engine import generate_issues, sort_issues, duplicate_groups

from scoring.score_calculator import compute_score

from recommendations.recommendation_engine import generate_recommendations

from reports.html_report_generator import generate_html_report
from reports.csv_report_generator import generate_csv_report
from reports.excel_report_generator import generate_excel_report
from reports.pdf_report_generator import generate_pdf_report

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = FastAPI(title="SEO Critics Studio", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    url: str
    max_pages: int = 10
    max_depth: int = 2


# ---------------------------------------------------------------------------
# Frontend routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ---------------------------------------------------------------------------
# Internal helpers (scan-time aggregation — not exposed as endpoints)
# ---------------------------------------------------------------------------

def _compute_crawl_stats(analyzed_pages: list) -> dict:
    """Aggregate crawl-level statistics from the already-analyzed pages.
    No additional HTTP requests are made — this is pure aggregation over
    data the crawler/analyzers already collected in this same scan."""
    total = len(analyzed_pages)
    status_2xx = sum(1 for p in analyzed_pages if p["status_code"] and 200 <= p["status_code"] < 300)
    status_3xx = sum(1 for p in analyzed_pages if p["status_code"] and 300 <= p["status_code"] < 400)
    status_4xx = sum(1 for p in analyzed_pages if p["status_code"] and 400 <= p["status_code"] < 500)
    status_5xx_or_failed = sum(
        1 for p in analyzed_pages if not p["status_code"] or p["status_code"] >= 500
    )
    response_times = [p["response_time_ms"] for p in analyzed_pages if p.get("response_time_ms")]
    sizes = [p["page_size_kb"] for p in analyzed_pages if p.get("page_size_kb")]
    depths = [p.get("crawl_depth", 0) for p in analyzed_pages]

    depth_distribution = Counter(depths)

    return {
        "pages_discovered": total,
        "pages_crawled": total,
        "status_2xx": status_2xx,
        "status_3xx": status_3xx,
        "status_4xx": status_4xx,
        "status_5xx_or_failed": status_5xx_or_failed,
        "avg_response_time_ms": round(sum(response_times) / len(response_times), 1) if response_times else 0,
        "avg_page_size_kb": round(sum(sizes) / len(sizes), 1) if sizes else 0,
        "max_depth": max(depths) if depths else 0,
        "depth_distribution": {str(d): c for d, c in sorted(depth_distribution.items())},
        "note": "'Pages discovered' equals 'pages crawled' in this design — the crawler "
                "stops queueing new links once the configured page limit is reached, so "
                "no separately-discovered-but-unqueued count is tracked.",
    }


def _node_health(status_code, severity_counts: dict) -> str:
    if not status_code or status_code >= 400:
        return "bad"
    if severity_counts.get("CRITICAL") or severity_counts.get("HIGH"):
        return "warn"
    if status_code >= 300:
        return "warn"
    return "good"


# ---------------------------------------------------------------------------
# Core scan endpoint (existing behavior preserved; new steps appended)
# ---------------------------------------------------------------------------

@app.post("/api/scan")
def run_scan(request: ScanRequest):
    root_url = request.url.strip()
    if not root_url.startswith(("http://", "https://")):
        root_url = "https://" + root_url

    parsed = urlparse(root_url)
    hostname = parsed.netloc.split(":")[0]
    if not parsed.netloc or " " in parsed.netloc or ("." not in hostname and hostname != "localhost"):
        raise HTTPException(status_code=400, detail="Please enter a valid website URL, e.g. example.com")

    max_pages = max(1, min(request.max_pages, 50))
    max_depth = max(0, min(request.max_depth, 4))

    # 1. Crawl
    try:
        crawled_pages, domain = crawl_website(root_url, max_pages=max_pages, max_depth=max_depth)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {exc}")

    if not crawled_pages:
        raise HTTPException(status_code=422, detail="No pages could be crawled for this URL.")

    # Map of already-crawled URLs -> status codes, reused by link analyzer
    crawled_status_map = {normalize_url(p["url"]): p["status_code"] for p in crawled_pages}

    # 2. Site-level checks
    sitemap_data = analyze_sitemap(root_url)
    robots_data = analyze_robots(root_url)

    # 3. Analyze each page
    analyzed_pages = []
    link_edges = []  # (source_url -> target_url) pairs for the internal link graph

    for page in crawled_pages:
        url_info = analyze_url(page)
        redirect_chain = page.get("redirect_chain", [])

        if not page.get("html"):
            analyzed_pages.append({
                "page_url": page["url"],
                "status_code": page["status_code"],
                "title": None, "meta_description": None, "meta_robots": None,
                "canonical_url": None, "h1_count": 0, "h2_count": 0, "word_count": 0,
                "internal_links": 0, "external_links": 0, "broken_links": 0,
                "image_count": 0, "images_missing_alt": 0,
                "is_https": url_info["is_https"], "page_size_kb": url_info["page_size_kb"],
                "response_time_ms": url_info["response_time_ms"], "page_score": 0,
                "has_viewport": False, "has_structured_data": False,
                "has_open_graph": False, "has_twitter_card": False, "html_lang": "",
                "images_missing_dimensions": 0, "non_descriptive_images": 0,
                "top_keywords": [],
                "crawl_depth": page.get("depth", 0),
                "redirect_count": page.get("redirect_count", 0),
                "redirect_chain": redirect_chain,
                "is_indexable": False,
            })
            continue

        soup = BeautifulSoup(page["html"], "lxml")

        metadata = analyze_metadata(soup)
        technical = analyze_technical(page["html"], soup)
        links = analyze_links(soup, page["url"], domain, crawled_status_map)
        images = analyze_images(soup)
        advanced = analyze_advanced(soup)
        keywords = analyze_keywords(soup)

        is_indexable = bool(
            url_info["status_code"] == 200
            and "noindex" not in (metadata["meta_robots"] or "").lower()
        )

        analyzed_pages.append({
            "page_url": page["url"],
            "status_code": url_info["status_code"],
            "title": metadata["title"],
            "meta_description": metadata["meta_description"],
            "meta_robots": metadata["meta_robots"],
            "canonical_url": technical["canonical"],
            "h1_count": technical["h1_count"],
            "h2_count": technical["h2_count"],
            "word_count": technical["word_count"],
            "internal_links": links["internal_links"],
            "external_links": links["external_links"],
            "broken_links": links["broken_links"],
            "image_count": images["image_count"],
            "images_missing_alt": images["images_missing_alt"],
            "is_https": url_info["is_https"],
            "page_size_kb": url_info["page_size_kb"],
            "response_time_ms": url_info["response_time_ms"],
            "page_score": None,  # per-page score not persisted separately; overall score is site-level
            "has_viewport": advanced["has_viewport"],
            "has_structured_data": advanced["has_structured_data"],
            "has_open_graph": advanced["has_open_graph"],
            "has_twitter_card": advanced["has_twitter_card"],
            "html_lang": advanced["html_lang"],
            "images_missing_dimensions": images["images_missing_dimensions"],
            "non_descriptive_images": images["non_descriptive_images"],
            "top_keywords": keywords["top_keywords"],
            "crawl_depth": page.get("depth", 0),
            "redirect_count": page.get("redirect_count", 0),
            "redirect_chain": redirect_chain,
            "is_indexable": is_indexable,
        })

        broken_targets = set(links.get("broken_link_targets", []))
        for target in links.get("internal_link_targets", []):
            link_edges.append({
                "source": page["url"],
                "target": target,
                "is_broken": target in broken_targets,
            })

    # 4. Score
    scores = compute_score(analyzed_pages, sitemap_data, robots_data)

    # 5. Site-wide keyword rollup + rule-based recommendations + issues + crawl stats
    site_keywords = merge_site_keywords([p["top_keywords"] for p in analyzed_pages])
    recommendations = generate_recommendations(analyzed_pages, sitemap_data, robots_data)
    issues = sort_issues(generate_issues(analyzed_pages, sitemap_data, robots_data))
    crawl_stats = _compute_crawl_stats(analyzed_pages)

    issue_count_by_url = Counter(i["affected_url"] for i in issues if i.get("affected_url"))
    for page in analyzed_pages:
        page["issue_count"] = issue_count_by_url.get(page["page_url"], 0)

    advanced_checks_summary = {
        "pages_with_viewport": sum(1 for p in analyzed_pages if p["has_viewport"]),
        "pages_with_structured_data": sum(1 for p in analyzed_pages if p["has_structured_data"]),
        "pages_with_open_graph": sum(1 for p in analyzed_pages if p["has_open_graph"]),
        "pages_with_twitter_card": sum(1 for p in analyzed_pages if p["has_twitter_card"]),
        "pages_with_lang": sum(1 for p in analyzed_pages if p["html_lang"]),
        "total_pages": len(analyzed_pages),
    }

    # 6. Persist to database
    website_id = models.insert_website(root_url, domain)
    for page in analyzed_pages:
        page_id = models.insert_page(website_id, {
            "url": page["page_url"], "status_code": page["status_code"],
            "title": page["title"], "meta_description": page["meta_description"],
            "meta_robots": page["meta_robots"], "canonical": page["canonical_url"],
            "h1_count": page["h1_count"], "h2_count": page["h2_count"],
            "word_count": page["word_count"], "internal_links": page["internal_links"],
            "external_links": page["external_links"], "broken_links": page["broken_links"],
            "image_count": page["image_count"], "images_missing_alt": page["images_missing_alt"],
            "is_https": page["is_https"], "page_size_kb": page["page_size_kb"],
            "response_time_ms": page["response_time_ms"], "page_score": page["page_score"],
            "has_viewport": page["has_viewport"], "has_structured_data": page["has_structured_data"],
            "has_open_graph": page["has_open_graph"], "has_twitter_card": page["has_twitter_card"],
            "html_lang": page["html_lang"],
            "images_missing_dimensions": page["images_missing_dimensions"],
            "non_descriptive_images": page["non_descriptive_images"],
            "top_keywords": json.dumps(page["top_keywords"]),
            "crawl_depth": page["crawl_depth"], "redirect_count": page["redirect_count"],
            "redirect_chain": json.dumps(page["redirect_chain"]), "is_indexable": page["is_indexable"],
        })
        page["page_id"] = page_id  # so the API response can link straight to Page Details

    models.insert_scan_history(website_id, len(analyzed_pages), "Completed")
    models.insert_issues(website_id, issues)
    models.insert_page_links(website_id, link_edges)

    website_row = {"root_url": root_url, "domain_name": domain}

    # 7. Generate reports (HTML, CSV, Excel, and PDF — all include recommendations
    #    and keyword insights; existing formats keep working unchanged)
    html_path = generate_html_report(
        website_row, scores, analyzed_pages, sitemap_data, robots_data,
        recommendations, site_keywords, advanced_checks_summary,
    )
    csv_path = generate_csv_report(domain, analyzed_pages)
    excel_path = generate_excel_report(
        website_row, scores, analyzed_pages, sitemap_data, robots_data,
        recommendations, site_keywords, advanced_checks_summary,
    )
    try:
        pdf_path = generate_pdf_report(
            website_row, scores, analyzed_pages, sitemap_data, robots_data,
            recommendations, site_keywords, advanced_checks_summary, issues, crawl_stats,
        )
    except Exception:
        pdf_path = None  # PDF export failing should never break the rest of the scan

    report_id = models.insert_report(
        website_id, scores,
        {"html": html_path, "csv": csv_path, "excel": excel_path, "pdf": pdf_path},
        recommendations, site_keywords, advanced_checks_summary,
        sitemap_data, robots_data, crawl_stats,
    )

    severity_counts = Counter(i["severity"] for i in issues)

    return {
        "website_id": website_id,
        "report_id": report_id,
        "root_url": root_url,
        "domain": domain,
        "pages_scanned": len(analyzed_pages),
        "scores": scores,
        "sitemap": sitemap_data,
        "robots": robots_data,
        "pages": analyzed_pages,
        "recommendations": recommendations,
        "site_keywords": site_keywords,
        "advanced_checks": advanced_checks_summary,
        # --- new fields (existing fields above are all unchanged) ---
        "crawl_stats": crawl_stats,
        "issue_count": len(issues),
        "issues_summary": {
            "CRITICAL": severity_counts.get("CRITICAL", 0),
            "HIGH": severity_counts.get("HIGH", 0),
            "MEDIUM": severity_counts.get("MEDIUM", 0),
            "LOW": severity_counts.get("LOW", 0),
            "INFO": severity_counts.get("INFO", 0),
        },
        "pdf_available": bool(pdf_path),
    }


# ---------------------------------------------------------------------------
# Report retrieval + history (existing, unchanged)
# ---------------------------------------------------------------------------

@app.get("/api/report/{website_id}")
def get_report(website_id: int):
    bundle = models.get_report_bundle(website_id)
    if not bundle["website"]:
        raise HTTPException(status_code=404, detail="Website not found.")
    return bundle


@app.get("/api/history")
def get_history():
    return models.get_scan_history()


@app.get("/api/download/{website_id}/{fmt}")
def download_report(website_id: int, fmt: str):
    bundle = models.get_report_bundle(website_id)
    report = bundle["report"]
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    path_map = {
        "html": report["html_report_path"],
        "csv": report["csv_report_path"],
        "excel": report["excel_report_path"],
        "pdf": report.get("pdf_report_path"),
    }
    file_path = path_map.get(fmt)
    if not file_path or not os.path.exists(file_path):
        detail = ("PDF report not available for this scan (it may predate PDF export support — "
                   "re-run the scan to generate one)." if fmt == "pdf" else "Report file not found.")
        raise HTTPException(status_code=404, detail=detail)

    return FileResponse(file_path, filename=os.path.basename(file_path))


@app.post("/api/download/{website_id}/pdf")
def download_pdf_report(website_id: int):
    """Explicit POST alias for PDF download, as requested by the API design.
    Behaves the same as GET /api/download/{website_id}/pdf."""
    return download_report(website_id, "pdf")


# ---------------------------------------------------------------------------
# NEW: Issue Explorer
# ---------------------------------------------------------------------------

@app.get("/api/issues/{website_id}")
def get_issues(
    website_id: int,
    severity: str = Query(None, description="CRITICAL | HIGH | MEDIUM | LOW | INFO"),
    category: str = Query(None),
    issue_type: str = Query(None),
    page: str = Query(None, description="Filter to issues affecting this exact page URL"),
):
    if not models.get_website(website_id):
        raise HTTPException(status_code=404, detail="Website not found.")
    return models.get_issues(website_id, severity=severity, category=category,
                              issue_type=issue_type, affected_url=page)


# ---------------------------------------------------------------------------
# NEW: Page Details
# ---------------------------------------------------------------------------

@app.get("/api/page/{website_id}/{page_id}")
def get_page_details(website_id: int, page_id: int):
    page = models.get_page_by_id(website_id, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found.")
    page_issues = models.get_issues(website_id, affected_url=page["page_url"])
    return {"page": page, "issues": page_issues}


# ---------------------------------------------------------------------------
# NEW: Crawl Overview
# ---------------------------------------------------------------------------

@app.get("/api/crawl/{website_id}")
def get_crawl_overview(website_id: int):
    report = models.get_latest_report(website_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report.get("crawl_stats", {})


# ---------------------------------------------------------------------------
# NEW: Internal Link Graph
# ---------------------------------------------------------------------------

MAX_GRAPH_NODES = 60


@app.get("/api/link-graph/{website_id}")
def get_link_graph(website_id: int):
    website = models.get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail="Website not found.")

    pages = models.get_pages(website_id)
    edges = models.get_page_links(website_id)
    all_issues = models.get_issues(website_id)

    page_urls = {p["page_url"] for p in pages}
    inbound_counts = Counter(e["target_url"] for e in edges if e["target_url"] in page_urls)

    severity_by_url = {}
    for i in all_issues:
        if i.get("affected_url"):
            severity_by_url.setdefault(i["affected_url"], Counter())[i["severity"]] += 1

    root_url = min(pages, key=lambda p: p.get("crawl_depth", 0))["page_url"] if pages else None

    truncated = len(pages) > MAX_GRAPH_NODES
    node_pages = pages
    if truncated:
        # Keep the most-linked pages plus the root, so the graph stays readable
        # and rendering stays fast even on a 50+ page crawl.
        sorted_pages = sorted(pages, key=lambda p: inbound_counts.get(p["page_url"], 0), reverse=True)
        node_pages = sorted_pages[:MAX_GRAPH_NODES]
        if root_url and root_url not in {p["page_url"] for p in node_pages}:
            node_pages = node_pages[:-1] + [next(p for p in pages if p["page_url"] == root_url)]

    node_urls = {p["page_url"] for p in node_pages}

    nodes = []
    for p in node_pages:
        sev_counts = severity_by_url.get(p["page_url"], {})
        nodes.append({
            "url": p["page_url"],
            "page_id": p["page_id"],
            "status_code": p["status_code"],
            "inbound_links": inbound_counts.get(p["page_url"], 0),
            "is_orphan": inbound_counts.get(p["page_url"], 0) == 0 and p["page_url"] != root_url,
            "health": _node_health(p["status_code"], sev_counts),
            "is_root": p["page_url"] == root_url,
        })

    graph_edges = [
        {"source": e["source_url"], "target": e["target_url"], "is_broken": bool(e["is_broken"])}
        for e in edges
        if e["source_url"] in node_urls and e["target_url"] in node_urls
    ]

    return {
        "nodes": nodes,
        "edges": graph_edges,
        "orphan_count": sum(1 for n in nodes if n["is_orphan"]),
        "truncated": truncated,
        "total_pages": len(pages),
    }


# ---------------------------------------------------------------------------
# NEW: Duplicate content / metadata
# ---------------------------------------------------------------------------

@app.get("/api/duplicates/{website_id}")
def get_duplicates(website_id: int):
    if not models.get_website(website_id):
        raise HTTPException(status_code=404, detail="Website not found.")
    pages = models.get_pages(website_id)

    def _groups(field):
        return [{"value": value, "urls": urls, "count": len(urls)}
                for value, urls in duplicate_groups(pages, field).items()]

    # Deterministic "similar content" heuristic: pages that share 4+ of their
    # top keywords. This is a keyword-overlap approximation, not full text
    # similarity — the app does not store raw page text, only computed
    # top-keyword lists, to keep the database lightweight. No AI is used.
    similar_pairs = []
    keyword_sets = {
        p["page_url"]: {kw["keyword"] for kw in (p.get("top_keywords") or [])}
        for p in pages
    }
    urls = list(keyword_sets.keys())
    for i in range(len(urls)):
        for j in range(i + 1, len(urls)):
            overlap = keyword_sets[urls[i]] & keyword_sets[urls[j]]
            if len(overlap) >= 4:
                similar_pairs.append({
                    "url_a": urls[i], "url_b": urls[j],
                    "shared_keywords": sorted(overlap),
                })

    return {
        "duplicate_titles": _groups("title"),
        "duplicate_descriptions": _groups("meta_description"),
        "duplicate_canonicals": _groups("canonical_url"),
        "similar_content_pairs": similar_pairs,
        "similarity_method_note": (
            "Similar-content pairs are found via deterministic top-keyword overlap "
            "(4+ shared keywords), not full-text similarity or AI — the app doesn't "
            "store raw page text."
        ),
    }


# ---------------------------------------------------------------------------
# NEW: Sitemap vs crawl coverage
# ---------------------------------------------------------------------------

@app.get("/api/sitemap/{website_id}")
def get_sitemap_coverage(website_id: int):
    report = models.get_latest_report(website_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    sitemap = report.get("sitemap", {})
    pages = models.get_pages(website_id)

    def _norm(u):
        try:
            return normalize_url(u)
        except Exception:
            return u

    sitemap_urls = {_norm(u) for u in sitemap.get("urls", [])}
    crawled_urls = {_norm(p["page_url"]) for p in pages}

    both = sitemap_urls & crawled_urls
    sitemap_only = sitemap_urls - crawled_urls
    crawled_only = crawled_urls - sitemap_urls

    cap = 200
    return {
        "sitemap_exists": sitemap.get("exists", False),
        "sitemap_url_count": len(sitemap_urls),
        "crawled_url_count": len(crawled_urls),
        "both_count": len(both),
        "sitemap_only_count": len(sitemap_only),
        "crawled_only_count": len(crawled_only),
        "both": sorted(both)[:cap],
        "sitemap_only": sorted(sitemap_only)[:cap],
        "crawled_only": sorted(crawled_only)[:cap],
        "note": "Sitemap URLs beyond the site's declared list may legitimately not be "
                "crawlable (e.g. paginated or filtered variants); this comparison is shown "
                "objectively without assuming either list is 'correct'.",
    }


# ---------------------------------------------------------------------------
# NEW: robots.txt inspector
# ---------------------------------------------------------------------------

@app.get("/api/robots/{website_id}")
def get_robots_inspector(website_id: int):
    report = models.get_latest_report(website_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    robots = report.get("robots", {})
    pages = models.get_pages(website_id)

    groups = robots.get("user_agent_groups", [])
    blocked = []
    for p in pages:
        path = urlparse(p["page_url"]).path or "/"
        if is_path_blocked(path, groups):
            blocked.append(p["page_url"])

    return {
        **robots,
        "blocked_crawled_pages": blocked,
        "scope_note": (
            "Simplified robots.txt parser: supports multiple User-agent groups, "
            "Disallow/Allow directives, a trailing '*' wildcard, and a trailing '$' "
            "end-anchor. It is NOT a full implementation of RFC 9309 or Google's "
            "extended robots.txt rules (e.g. mid-pattern wildcards, crawl-delay)."
        ),
    }


# ---------------------------------------------------------------------------
# NEW: Performance dashboard
# ---------------------------------------------------------------------------

@app.get("/api/performance/{website_id}")
def get_performance(
    website_id: int,
    response_threshold_ms: int = Query(1500),
    size_threshold_kb: float = Query(1500),
):
    pages = models.get_pages(website_id)
    if not pages:
        raise HTTPException(status_code=404, detail="Website not found or has no pages.")

    timed_pages = [p for p in pages if p.get("response_time_ms") is not None]
    sized_pages = [p for p in pages if p.get("page_size_kb") is not None]

    fastest = min(timed_pages, key=lambda p: p["response_time_ms"], default=None)
    slowest = max(timed_pages, key=lambda p: p["response_time_ms"], default=None)
    largest = max(sized_pages, key=lambda p: p["page_size_kb"], default=None)

    def _slim(p):
        return {"page_id": p["page_id"], "url": p["page_url"],
                "response_time_ms": p["response_time_ms"], "page_size_kb": p["page_size_kb"]}

    slow_pages = [_slim(p) for p in timed_pages if p["response_time_ms"] > response_threshold_ms]
    large_pages = [_slim(p) for p in sized_pages if p["page_size_kb"] > size_threshold_kb]

    return {
        "avg_response_time_ms": round(sum(p["response_time_ms"] for p in timed_pages) / len(timed_pages), 1) if timed_pages else 0,
        "avg_page_size_kb": round(sum(p["page_size_kb"] for p in sized_pages) / len(sized_pages), 1) if sized_pages else 0,
        "fastest_page": _slim(fastest) if fastest else None,
        "slowest_page": _slim(slowest) if slowest else None,
        "largest_page": _slim(largest) if largest else None,
        "response_threshold_ms": response_threshold_ms,
        "size_threshold_kb": size_threshold_kb,
        "pages_above_response_threshold": slow_pages,
        "pages_above_size_threshold": large_pages,
        "note": "Timing reflects this app's own request/response measurements — not "
                "browser-based Core Web Vitals, which this tool does not measure.",
    }


# ---------------------------------------------------------------------------
# NEW: Scan comparison
# ---------------------------------------------------------------------------

@app.get("/api/compare/{website_id_1}/{website_id_2}")
def compare_scans(website_id_1: int, website_id_2: int):
    website_a = models.get_website(website_id_1)
    website_b = models.get_website(website_id_2)
    report_a = models.get_latest_report(website_id_1)
    report_b = models.get_latest_report(website_id_2)
    if not website_a or not website_b or not report_a or not report_b:
        raise HTTPException(status_code=404, detail="One or both scans were not found.")

    pages_a = models.get_pages(website_id_1)
    pages_b = models.get_pages(website_id_2)
    issues_a = models.get_issues(website_id_1)
    issues_b = models.get_issues(website_id_2)

    def _issue_key(i):
        return (i["issue_type"], i.get("affected_url") or "__site__")

    keys_a = {_issue_key(i): i for i in issues_a}
    keys_b = {_issue_key(i): i for i in issues_b}

    new_issues = [i for k, i in keys_b.items() if k not in keys_a]
    fixed_issues = [i for k, i in keys_a.items() if k not in keys_b]
    unchanged_issues = [i for k, i in keys_b.items() if k in keys_a]

    category_score_map = [
        ("Metadata", "metadata_score"), ("Technical SEO", "technical_score"),
        ("Images", "images_score"), ("Links", "links_score"),
        ("Sitemap", "sitemap_score"), ("robots.txt", "robots_score"),
        ("Performance", "performance_score"),
    ]
    category_deltas = {}
    for label, key in category_score_map:
        prev = report_a.get(key) or 0
        curr = report_b.get(key) or 0
        category_deltas[label] = {"previous": prev, "current": curr, "delta": round(curr - prev, 2)}

    def _severity_counts(issues):
        c = Counter(i["severity"] for i in issues)
        return {s: c.get(s, 0) for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")}

    return {
        "previous": {
            "website_id": website_id_1, "root_url": website_a["root_url"],
            "scanned_on": report_a.get("generated_on"), "overall_score": report_a.get("overall_score"),
            "health_level": report_a.get("health_level"), "pages_scanned": len(pages_a),
            "issue_counts": _severity_counts(issues_a),
        },
        "current": {
            "website_id": website_id_2, "root_url": website_b["root_url"],
            "scanned_on": report_b.get("generated_on"), "overall_score": report_b.get("overall_score"),
            "health_level": report_b.get("health_level"), "pages_scanned": len(pages_b),
            "issue_counts": _severity_counts(issues_b),
        },
        "overall_score_delta": round((report_b.get("overall_score") or 0) - (report_a.get("overall_score") or 0), 2),
        "category_deltas": category_deltas,
        "new_issues": new_issues,
        "fixed_issues": fixed_issues,
        "unchanged_issues": unchanged_issues,
        "new_issue_count": len(new_issues),
        "fixed_issue_count": len(fixed_issues),
        "unchanged_issue_count": len(unchanged_issues),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
