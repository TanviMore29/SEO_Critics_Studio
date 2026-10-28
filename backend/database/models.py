"""
database/models.py

Simple data-access helper functions for each table.
No ORM is used to keep the mini-project dependencies minimal.
"""

import json
from .db_connection import get_connection


def insert_website(root_url: str, domain_name: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Websites (root_url, domain_name) VALUES (?, ?)",
        (root_url, domain_name),
    )
    conn.commit()
    website_id = cur.lastrowid
    conn.close()
    return website_id


def insert_page(website_id: int, page: dict) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Pages (
            website_id, page_url, status_code, title, meta_description,
            meta_robots, canonical_url, h1_count, h2_count, word_count,
            internal_links, external_links, broken_links, image_count,
            images_missing_alt, is_https, page_size_kb, response_time_ms, page_score,
            has_viewport, has_structured_data, has_open_graph, has_twitter_card,
            html_lang, images_missing_dimensions, non_descriptive_images, top_keywords,
            crawl_depth, redirect_count, redirect_chain, is_indexable
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        website_id, page.get("url"), page.get("status_code"), page.get("title"),
        page.get("meta_description"), page.get("meta_robots"), page.get("canonical"),
        page.get("h1_count"), page.get("h2_count"), page.get("word_count"),
        page.get("internal_links"), page.get("external_links"), page.get("broken_links"),
        page.get("image_count"), page.get("images_missing_alt"), page.get("is_https"),
        page.get("page_size_kb"), page.get("response_time_ms"), page.get("page_score"),
        page.get("has_viewport"), page.get("has_structured_data"), page.get("has_open_graph"),
        page.get("has_twitter_card"), page.get("html_lang"),
        page.get("images_missing_dimensions"), page.get("non_descriptive_images"),
        page.get("top_keywords"),
        page.get("crawl_depth"), page.get("redirect_count"), page.get("redirect_chain"),
        page.get("is_indexable"),
    ))
    conn.commit()
    page_id = cur.lastrowid
    conn.close()
    return page_id


def insert_image(page_id: int, image_url: str, alt_text: str, has_alt: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Images (page_id, image_url, alt_text, has_alt) VALUES (?,?,?,?)",
        (page_id, image_url, alt_text, has_alt),
    )
    conn.commit()
    conn.close()


def insert_report(website_id: int, scores: dict, paths: dict,
                   recommendations: list = None, site_keywords: list = None,
                   advanced_checks: dict = None, sitemap_data: dict = None,
                   robots_data: dict = None, crawl_stats: dict = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Reports (
            website_id, overall_score, health_level, metadata_score, technical_score,
            images_score, links_score, sitemap_score, robots_score, performance_score,
            html_report_path, csv_report_path, excel_report_path,
            recommendations_json, keywords_json, advanced_checks_json,
            sitemap_urls_json, robots_meta_json, crawl_stats_json, pdf_report_path
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        website_id, scores["overall_score"], scores["health_level"],
        scores["metadata_score"], scores["technical_score"], scores["images_score"],
        scores["links_score"], scores["sitemap_score"], scores["robots_score"],
        scores["performance_score"], paths.get("html"), paths.get("csv"), paths.get("excel"),
        json.dumps(recommendations or []), json.dumps(site_keywords or []),
        json.dumps(advanced_checks or {}),
        json.dumps(sitemap_data or {}), json.dumps(robots_data or {}),
        json.dumps(crawl_stats or {}), paths.get("pdf"),
    ))
    conn.commit()
    report_id = cur.lastrowid
    conn.close()
    return report_id


def insert_scan_history(website_id: int, pages_scanned: int, status: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ScanHistory (website_id, pages_scanned, status) VALUES (?,?,?)",
        (website_id, pages_scanned, status),
    )
    conn.commit()
    conn.close()


def get_scan_history(limit: int = 20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sh.scan_id, sh.scan_date, sh.pages_scanned, sh.status,
               w.website_id, w.root_url, w.domain_name,
               r.overall_score, r.health_level, r.report_id
        FROM ScanHistory sh
        JOIN Websites w ON sh.website_id = w.website_id
        LEFT JOIN Reports r ON r.website_id = w.website_id
        ORDER BY sh.scan_date DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_website(website_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Websites WHERE website_id = ?", (website_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_pages(website_id: int) -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pages WHERE website_id = ?", (website_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    for p in rows:
        try:
            p["top_keywords"] = json.loads(p["top_keywords"]) if p.get("top_keywords") else []
        except (json.JSONDecodeError, TypeError):
            p["top_keywords"] = []
        try:
            p["redirect_chain"] = json.loads(p["redirect_chain"]) if p.get("redirect_chain") else []
        except (json.JSONDecodeError, TypeError):
            p["redirect_chain"] = []
    return rows


def get_latest_report(website_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM Reports WHERE website_id = ? ORDER BY report_id DESC LIMIT 1",
        (website_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    report = dict(row)
    json_field_map = {
        "recommendations_json": ("recommendations", []),
        "keywords_json": ("keywords", []),
        "advanced_checks_json": ("advanced_checks", {}),
        "sitemap_urls_json": ("sitemap", {}),
        "robots_meta_json": ("robots", {}),
        "crawl_stats_json": ("crawl_stats", {}),
    }
    for json_field, (target_key, default) in json_field_map.items():
        raw = report.get(json_field)
        try:
            report[target_key] = json.loads(raw) if raw else default
        except (json.JSONDecodeError, TypeError):
            report[target_key] = default
    return report


def get_report_bundle(website_id: int):
    """Return website info, latest report, and all page rows for a website.
    JSON-encoded columns (recommendations, keywords, advanced checks,
    sitemap/robots detail, crawl stats, and each page's top keywords /
    redirect chain) are decoded back into native lists/dicts."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Websites WHERE website_id = ?", (website_id,))
    website = cur.fetchone()

    cur.execute(
        "SELECT * FROM Reports WHERE website_id = ? ORDER BY report_id DESC LIMIT 1",
        (website_id,),
    )
    report_row = cur.fetchone()
    report = dict(report_row) if report_row else None
    if report:
        json_field_map = {
            "recommendations_json": ("recommendations", []),
            "keywords_json": ("keywords", []),
            "advanced_checks_json": ("advanced_checks", {}),
            "sitemap_urls_json": ("sitemap", {}),
            "robots_meta_json": ("robots", {}),
            "crawl_stats_json": ("crawl_stats", {}),
        }
        for json_field, (target_key, default) in json_field_map.items():
            raw = report.get(json_field)
            try:
                report[target_key] = json.loads(raw) if raw else default
            except (json.JSONDecodeError, TypeError):
                report[target_key] = default

    cur.execute("SELECT * FROM Pages WHERE website_id = ?", (website_id,))
    page_rows = [dict(p) for p in cur.fetchall()]
    for p in page_rows:
        try:
            p["top_keywords"] = json.loads(p["top_keywords"]) if p.get("top_keywords") else []
        except (json.JSONDecodeError, TypeError):
            p["top_keywords"] = []
        try:
            p["redirect_chain"] = json.loads(p["redirect_chain"]) if p.get("redirect_chain") else []
        except (json.JSONDecodeError, TypeError):
            p["redirect_chain"] = []

    conn.close()
    return {
        "website": dict(website) if website else None,
        "report": report,
        "pages": page_rows,
    }


# ---------------------------------------------------------------------------
# Issues (Issue Explorer / Page Details / Scan Comparison)
# ---------------------------------------------------------------------------

def insert_issues(website_id: int, issues: list):
    if not issues:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO Issues (
            website_id, issue_type, category, severity, title, description,
            affected_url, affected_count, recommendation, evidence_json
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
    """, [
        (
            website_id, i["issue_type"], i["category"], i["severity"], i["title"],
            i["description"], i.get("affected_url"), i.get("affected_count", 1),
            i.get("recommendation", ""), json.dumps(i.get("evidence", {})),
        )
        for i in issues
    ])
    conn.commit()
    conn.close()


def get_issues(website_id: int, severity: str = None, category: str = None,
                issue_type: str = None, affected_url: str = None) -> list:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM Issues WHERE website_id = ?"
    params = [website_id]
    if severity:
        query += " AND UPPER(severity) = ?"
        params.append(severity.upper())
    if category:
        query += " AND LOWER(category) = ?"
        params.append(category.lower())
    if issue_type:
        query += " AND issue_type = ?"
        params.append(issue_type)
    if affected_url:
        query += " AND affected_url = ?"
        params.append(affected_url)
    query += " ORDER BY CASE severity " \
              "WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 " \
              "WHEN 'LOW' THEN 3 ELSE 4 END"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        try:
            r["evidence"] = json.loads(r["evidence_json"]) if r.get("evidence_json") else {}
        except (json.JSONDecodeError, TypeError):
            r["evidence"] = {}
    conn.close()
    return rows


def get_latest_website_id_for_domain_excluding(domain_name: str, exclude_website_id: int = None):
    """Used by scan comparison to find a prior scan of the same domain."""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT website_id FROM Websites WHERE domain_name = ?"
    params = [domain_name]
    if exclude_website_id:
        query += " AND website_id != ?"
        params.append(exclude_website_id)
    query += " ORDER BY website_id DESC LIMIT 1"
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return row["website_id"] if row else None


# ---------------------------------------------------------------------------
# Page links (Internal Link Graph)
# ---------------------------------------------------------------------------

def insert_page_links(website_id: int, edges: list):
    if not edges:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO PageLinks (website_id, source_url, target_url, is_broken) VALUES (?,?,?,?)",
        [(website_id, e["source"], e["target"], e.get("is_broken", False)) for e in edges],
    )
    conn.commit()
    conn.close()


def get_page_links(website_id: int) -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT source_url, target_url, is_broken FROM PageLinks WHERE website_id = ?", (website_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Single page lookup (Page Details drawer)
# ---------------------------------------------------------------------------

def get_page_by_id(website_id: int, page_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pages WHERE website_id = ? AND page_id = ?", (website_id, page_id))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    page = dict(row)
    try:
        page["top_keywords"] = json.loads(page["top_keywords"]) if page.get("top_keywords") else []
    except (json.JSONDecodeError, TypeError):
        page["top_keywords"] = []
    try:
        page["redirect_chain"] = json.loads(page["redirect_chain"]) if page.get("redirect_chain") else []
    except (json.JSONDecodeError, TypeError):
        page["redirect_chain"] = []
    return page
