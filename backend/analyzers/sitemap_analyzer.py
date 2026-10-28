"""
analyzers/sitemap_analyzer.py

Checks for the presence and validity of the website's sitemap.xml file,
and (new) returns the list of URLs it declares so the app can compare
sitemap coverage against what was actually crawled.
"""

from urllib.parse import urlparse
import requests
from lxml import etree

USER_AGENT = "SEOCriticsStudioBot/1.0 (+educational-mini-project)"
REQUEST_TIMEOUT = 10
MAX_URLS_RETURNED = 500  # cap so a huge sitemap can't bloat the response/DB row


def analyze_sitemap(root_url: str):
    parsed = urlparse(root_url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

    result = {
        "sitemap_url": sitemap_url,
        "exists": False,
        "is_valid": False,
        "url_count": 0,
        "urls": [],
        "truncated": False,
    }

    try:
        response = requests.get(
            sitemap_url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200 and response.content:
            result["exists"] = True
            try:
                tree = etree.fromstring(response.content)
                # Count <url> or <sitemap> child elements regardless of namespace
                url_elements = [el for el in tree.iter() if el.tag.endswith("url") or el.tag.endswith("sitemap")]
                result["url_count"] = len(url_elements)
                result["is_valid"] = len(url_elements) > 0

                # Also collect the actual <loc> values (the real page/sub-sitemap
                # URLs) for sitemap-vs-crawl coverage comparison.
                loc_elements = [el for el in tree.iter() if el.tag.endswith("loc")]
                locs = [el.text.strip() for el in loc_elements if el.text and el.text.strip()]
                result["truncated"] = len(locs) > MAX_URLS_RETURNED
                result["urls"] = locs[:MAX_URLS_RETURNED]
            except etree.XMLSyntaxError:
                result["is_valid"] = False
    except requests.exceptions.RequestException:
        pass

    return result
