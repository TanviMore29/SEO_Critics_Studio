"""
reports/csv_report_generator.py

Generates a CSV export of page-level SEO analysis results.
"""

import csv
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports_output", "csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FIELDNAMES = [
    "page_url", "status_code", "title", "meta_description", "meta_robots",
    "canonical_url", "h1_count", "h2_count", "word_count",
    "internal_links", "external_links", "broken_links",
    "image_count", "images_missing_alt", "is_https",
    "page_size_kb", "response_time_ms", "page_score",
]


def generate_csv_report(domain: str, pages: list) -> str:
    file_path = os.path.join(OUTPUT_DIR, f"{domain}_seo_report.csv")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for page in pages:
            writer.writerow(page)
    return file_path
