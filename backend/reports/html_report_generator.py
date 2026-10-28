"""
reports/html_report_generator.py

Generates a self-contained, styled HTML SEO report for a scanned website.
"""

import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports_output", "html")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _health_color(level: str) -> str:
    return {
        "Excellent": "#2e7d32",
        "Good": "#66bb6a",
        "Average": "#f9a825",
        "Poor": "#ef6c00",
        "Critical": "#c62828",
    }.get(level, "#666")


def generate_html_report(website: dict, scores: dict, pages: list, sitemap_data: dict, robots_data: dict,
                          recommendations: list = None, site_keywords: list = None,
                          advanced_checks: dict = None) -> str:
    domain = website["domain_name"]
    color = _health_color(scores["health_level"])
    recommendations = recommendations or []
    site_keywords = site_keywords or []
    advanced_checks = advanced_checks or {}
    total_pages = advanced_checks.get("total_pages", len(pages)) or 1

    rows = ""
    for p in pages:
        rows += f"""
        <tr>
            <td>{p['page_url']}</td>
            <td>{p['status_code']}</td>
            <td>{(p['title'] or '')[:60]}</td>
            <td>{p['h1_count']}</td>
            <td>{p['word_count']}</td>
            <td>{p['image_count']}</td>
            <td>{p['images_missing_alt']}</td>
            <td>{p['broken_links']}</td>
        </tr>"""

    max_scores = scores["max_scores"]
    category_rows = "".join(f"""
        <tr>
            <td>{label}</td>
            <td>{scores[key]} / {max_scores[maxkey]}</td>
        </tr>""" for label, key, maxkey in [
        ("Metadata", "metadata_score", "metadata"),
        ("Technical SEO", "technical_score", "technical"),
        ("Images", "images_score", "images"),
        ("Links", "links_score", "links"),
        ("Sitemap", "sitemap_score", "sitemap"),
        ("robots.txt", "robots_score", "robots"),
        ("Performance", "performance_score", "performance"),
    ])

    priority_colors = {"high": "#c62828", "medium": "#ef6c00", "low": "#2e7d32"}
    recommendation_rows = "".join(f"""
        <tr>
            <td><span style="color:{priority_colors.get(r['priority'], '#666')}; font-weight:bold; text-transform:uppercase; font-size:11px;">{r['priority']}</span></td>
            <td>{r['title']}</td>
            <td>{r['description']}</td>
        </tr>""" for r in recommendations) or '<tr><td colspan="3">No issues detected — nice work!</td></tr>'

    advanced_rows = f"""
        <tr><td>Pages with mobile viewport tag</td><td>{advanced_checks.get('pages_with_viewport', 0)} / {total_pages}</td></tr>
        <tr><td>Pages with structured data</td><td>{advanced_checks.get('pages_with_structured_data', 0)} / {total_pages}</td></tr>
        <tr><td>Pages with Open Graph tags</td><td>{advanced_checks.get('pages_with_open_graph', 0)} / {total_pages}</td></tr>
        <tr><td>Pages with Twitter Card tags</td><td>{advanced_checks.get('pages_with_twitter_card', 0)} / {total_pages}</td></tr>
        <tr><td>Pages with declared language</td><td>{advanced_checks.get('pages_with_lang', 0)} / {total_pages}</td></tr>
    """

    keyword_chips = "".join(
        f'<span style="display:inline-block; background:#eef2f7; color:#14213d; padding:5px 12px; '
        f'border-radius:14px; font-size:12.5px; margin:3px;">{kw["keyword"]} <b>({kw["count"]})</b></span>'
        for kw in site_keywords
    ) or "<span>No keyword data available.</span>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SEO Report - {domain}</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f4f6f8; color: #1a1a1a; }}
    .header {{ background: #14213d; color: #fff; padding: 30px 40px; }}
    .header h1 {{ margin: 0 0 6px 0; font-size: 26px; }}
    .container {{ padding: 30px 40px; }}
    .score-card {{ background: #fff; border-radius: 10px; padding: 24px; display: flex; align-items: center; gap: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
    .score-circle {{ width: 100px; height: 100px; border-radius: 50%; background: {color}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: bold; }}
    .health-label {{ font-size: 20px; font-weight: bold; color: {color}; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; margin-top: 20px; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #eee; text-align: left; font-size: 13px; }}
    th {{ background: #14213d; color: #fff; }}
    tr:hover {{ background: #fafafa; }}
    h2 {{ margin-top: 36px; color: #14213d; }}
    .meta-info {{ font-size: 13px; color: #555; margin-top: 6px; }}
    .keyword-box {{ background: #fff; border-radius: 8px; padding: 16px; margin-top: 20px; }}
    .note {{ font-size: 12px; color: #777; margin-top: 8px; }}
</style>
</head>
<body>
    <div class="header">
        <h1>SEO Critics Studio — Analysis Report</h1>
        <div>Website: {website['root_url']}</div>
        <div class="meta-info">Domain: {domain} | Pages Scanned: {len(pages)}</div>
    </div>
    <div class="container">
        <div class="score-card">
            <div class="score-circle">{scores['overall_score']}</div>
            <div>
                <div class="health-label">{scores['health_level']}</div>
                <div>Overall SEO Score out of 100</div>
            </div>
        </div>

        <h2>Category Score Breakdown</h2>
        <table>
            <tr><th>Category</th><th>Score</th></tr>
            {category_rows}
        </table>

        <h2>Recommendations</h2>
        <table>
            <tr><th>Priority</th><th>Recommendation</th><th>Details</th></tr>
            {recommendation_rows}
        </table>
        <div class="note">Recommendations are generated by a fixed set of rule-based checks against the scan results — not an AI model.</div>

        <h2>Additional Technical Signals</h2>
        <table>
            <tr><th>Check</th><th>Coverage</th></tr>
            {advanced_rows}
        </table>

        <h2>Top Keywords (site-wide)</h2>
        <div class="keyword-box">{keyword_chips}</div>

        <h2>Sitemap &amp; robots.txt</h2>
        <table>
            <tr><th>Check</th><th>Result</th></tr>
            <tr><td>sitemap.xml exists</td><td>{"Yes" if sitemap_data.get("exists") else "No"}</td></tr>
            <tr><td>sitemap.xml URL count</td><td>{sitemap_data.get("url_count", 0)}</td></tr>
            <tr><td>robots.txt exists</td><td>{"Yes" if robots_data.get("exists") else "No"}</td></tr>
            <tr><td>robots.txt disallowed paths</td><td>{len(robots_data.get("disallowed_paths", []))}</td></tr>
        </table>

        <h2>Page-Level Details</h2>
        <table>
            <tr>
                <th>URL</th><th>Status</th><th>Title</th><th>H1 Count</th>
                <th>Word Count</th><th>Images</th><th>Missing ALT</th><th>Broken Links</th>
            </tr>
            {rows}
        </table>
    </div>
</body>
</html>"""

    file_path = os.path.join(OUTPUT_DIR, f"{domain}_seo_report.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return file_path
