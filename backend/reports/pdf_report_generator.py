"""
reports/pdf_report_generator.py

Generates a professional PDF summary of a scan, suitable for a B.Sc.
project demonstration or handing to a stakeholder. Built with ReportLab
(already a dependency, previously unused by earlier report generators).

Mirrors the same data used by the HTML/Excel reports — no new data is
invented for this format.
"""

import os
from xml.sax.saxutils import escape as _xml_escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports_output", "pdf")
os.makedirs(OUTPUT_DIR, exist_ok=True)

INK = colors.HexColor("#14213D")
MUTED = colors.HexColor("#555555")
LIGHT = colors.HexColor("#F4F6F8")

HEALTH_COLORS = {
    "Excellent": colors.HexColor("#2E7D32"),
    "Good": colors.HexColor("#66BB6A"),
    "Average": colors.HexColor("#F9A825"),
    "Poor": colors.HexColor("#EF6C00"),
    "Critical": colors.HexColor("#C62828"),
}

SEVERITY_COLORS = {
    "CRITICAL": colors.HexColor("#C62828"),
    "HIGH": colors.HexColor("#EF6C00"),
    "MEDIUM": colors.HexColor("#F9A825"),
    "LOW": colors.HexColor("#2E7D32"),
    "INFO": colors.HexColor("#546E7A"),
}

# Plain hex strings for use inside Paragraph <font color="..."> markup
# (reportlab Color objects aren't directly usable there).
HEALTH_HEX = {
    "Excellent": "#2E7D32", "Good": "#66BB6A", "Average": "#F9A825",
    "Poor": "#EF6C00", "Critical": "#C62828",
}
SEVERITY_HEX = {
    "CRITICAL": "#C62828", "HIGH": "#EF6C00", "MEDIUM": "#F9A825",
    "LOW": "#2E7D32", "INFO": "#546E7A",
}


def _esc(value) -> str:
    """Escape text for safe use inside ReportLab's mini-XML Paragraph markup."""
    return _xml_escape(str(value)) if value is not None else ""


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("H1Custom", parent=styles["Heading1"], textColor=INK, spaceAfter=6))
    styles.add(ParagraphStyle("H2Custom", parent=styles["Heading2"], textColor=INK, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("BodyMuted", parent=styles["Normal"], textColor=MUTED, fontSize=9))
    styles.add(ParagraphStyle("CellText", parent=styles["Normal"], fontSize=8, leading=10))
    return styles


def generate_pdf_report(website: dict, scores: dict, pages: list, sitemap_data: dict, robots_data: dict,
                         recommendations: list, site_keywords: list, advanced_checks: dict,
                         issues: list, crawl_stats: dict) -> str:
    styles = _styles()
    domain = website["domain_name"]
    file_path = os.path.join(OUTPUT_DIR, f"{domain}_seo_report.pdf")

    doc = SimpleDocTemplate(
        file_path, pagesize=A4,
        topMargin=18 * mm, bottomMargin=16 * mm, leftMargin=16 * mm, rightMargin=16 * mm,
    )
    story = []

    # --- Title ---
    story.append(Paragraph("SEO Critics Studio — Audit Report", styles["H1Custom"]))
    story.append(Paragraph(f"Website: {_esc(website['root_url'])}", styles["Normal"]))
    story.append(Paragraph(f"Domain: {_esc(domain)} &nbsp;|&nbsp; Pages scanned: {len(pages)}", styles["BodyMuted"]))
    story.append(Spacer(1, 10))

    # --- Score summary ---
    health = scores["health_level"]
    health_hex = HEALTH_HEX.get(health, "#14213D")
    score_table = Table([
        [Paragraph(f"<b>{scores['overall_score']}</b> / 100", styles["Normal"]),
         Paragraph(f'<font color="{health_hex}"><b>{health}</b></font>', styles["Normal"])],
    ], colWidths=[90 * mm, 90 * mm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(score_table)

    # --- Category breakdown ---
    story.append(Paragraph("Category Score Breakdown", styles["H2Custom"]))
    max_scores = scores["max_scores"]
    cat_rows = [["Category", "Score"]]
    for label, key, maxkey in [
        ("Metadata", "metadata_score", "metadata"), ("Technical SEO", "technical_score", "technical"),
        ("Images", "images_score", "images"), ("Links", "links_score", "links"),
        ("Sitemap", "sitemap_score", "sitemap"), ("robots.txt", "robots_score", "robots"),
        ("Performance", "performance_score", "performance"),
    ]:
        cat_rows.append([label, f"{scores[key]} / {max_scores[maxkey]}"])
    cat_table = Table(cat_rows, colWidths=[90 * mm, 90 * mm])
    cat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(cat_table)

    # --- Crawl statistics ---
    story.append(Paragraph("Crawl Statistics", styles["H2Custom"]))
    cs_rows = [["Metric", "Value"]]
    for label, key in [
        ("Pages crawled", "pages_crawled"), ("2xx responses", "status_2xx"),
        ("3xx responses", "status_3xx"), ("4xx responses", "status_4xx"),
        ("5xx / failed", "status_5xx_or_failed"), ("Average response time (ms)", "avg_response_time_ms"),
        ("Average page size (KB)", "avg_page_size_kb"), ("Maximum crawl depth", "max_depth"),
    ]:
        cs_rows.append([label, str(crawl_stats.get(key, "—"))])
    cs_table = Table(cs_rows, colWidths=[90 * mm, 90 * mm])
    cs_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(cs_table)

    # --- Sitemap / robots ---
    story.append(Paragraph("Sitemap &amp; robots.txt", styles["H2Custom"]))
    sr_rows = [
        ["sitemap.xml exists", "Yes" if sitemap_data.get("exists") else "No"],
        ["sitemap.xml URL count", str(sitemap_data.get("url_count", 0))],
        ["robots.txt exists", "Yes" if robots_data.get("exists") else "No"],
        ["robots.txt rule count", str(robots_data.get("rule_count", 0))],
    ]
    sr_table = Table(sr_rows, colWidths=[90 * mm, 90 * mm])
    sr_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sr_table)

    # --- Top issues ---
    story.append(Paragraph("Top Issues", styles["H2Custom"]))
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    top_issues = sorted(issues, key=lambda i: severity_order.get(i["severity"], 5))[:20]
    if top_issues:
        issue_rows = [["Severity", "Issue", "Affected URL"]]
        for i in top_issues:
            sev_hex = SEVERITY_HEX.get(i["severity"], "#555555")
            issue_rows.append([
                Paragraph(f'<font color="{sev_hex}"><b>{i["severity"]}</b></font>', styles["CellText"]),
                Paragraph(_esc(i["title"]), styles["CellText"]),
                Paragraph(_esc((i.get("affected_url") or "Site-wide")[:70]), styles["CellText"]),
            ])
        issue_table = Table(issue_rows, colWidths=[22 * mm, 68 * mm, 90 * mm])
        issue_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(issue_table)
    else:
        story.append(Paragraph("No issues detected.", styles["Normal"]))

    # --- Recommendations ---
    story.append(PageBreak())
    story.append(Paragraph("Recommendations", styles["H1Custom"]))
    story.append(Paragraph(
        "Generated by fixed, rule-based checks against this scan's results — not an AI model.",
        styles["BodyMuted"]))
    story.append(Spacer(1, 6))
    if recommendations:
        for r in recommendations[:20]:
            sev_hex = SEVERITY_HEX.get(r["priority"].upper(), "#555555")
            story.append(Paragraph(
                f'<font color="{sev_hex}"><b>[{r["priority"].upper()}]</b></font> '
                f'<b>{_esc(r["title"])}</b><br/><font size=8 color="#555555">{_esc(r["description"])}</font>',
                styles["Normal"]))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No issues detected — nice work!", styles["Normal"]))

    # --- Page findings summary ---
    story.append(Paragraph("Page Findings Summary", styles["H2Custom"]))
    page_rows = [["URL", "Status", "Title", "Words", "Issues"]]
    issue_count_by_url = {}
    for i in issues:
        if i.get("affected_url"):
            issue_count_by_url[i["affected_url"]] = issue_count_by_url.get(i["affected_url"], 0) + 1
    for p in pages[:40]:
        page_rows.append([
            Paragraph(_esc((p.get("page_url") or "")[:55]), styles["CellText"]),
            str(p.get("status_code") or "—"),
            Paragraph(_esc((p.get("title") or "—")[:35]), styles["CellText"]),
            str(p.get("word_count") or 0),
            str(issue_count_by_url.get(p.get("page_url"), 0)),
        ])
    page_table = Table(page_rows, colWidths=[75 * mm, 15 * mm, 55 * mm, 18 * mm, 17 * mm])
    page_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(page_table)
    if len(pages) > 40:
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"...and {len(pages) - 40} more page(s). See the HTML/Excel report for the full list.",
                                styles["BodyMuted"]))

    doc.build(story)
    return file_path
