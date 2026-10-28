"""
analyzers/url_analyzer.py

Evaluates a URL's response-level health: status code, response time,
page size, HTTPS usage, and redirect chain length. All of this data is
captured once during crawling (website_crawler.py) to avoid re-fetching
each page; this module simply normalizes it into the URL-health summary
used by the scoring engine and reports.
"""


def analyze_url(page_data: dict) -> dict:
    return {
        "url": page_data.get("url"),
        "status_code": page_data.get("status_code"),
        "response_time_ms": page_data.get("response_time_ms"),
        "page_size_kb": page_data.get("page_size_kb"),
        "is_https": page_data.get("is_https"),
        "redirect_count": page_data.get("redirect_count", 0),
    }
