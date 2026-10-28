"""
analyzers/internal_link_analyzer.py

Classifies all <a> links on a page as internal or external, and checks
a bounded sample of them for broken (4xx/5xx or unreachable) status.
"""

from urllib.parse import urlparse, urljoin
import requests

USER_AGENT = "SEOCriticsStudioBot/1.0 (+educational-mini-project)"
LINK_CHECK_TIMEOUT = 6
MAX_LINKS_TO_CHECK = 15  # keep scan time bounded for a mini project


def analyze_links(soup, base_url: str, domain: str, crawled_status_map: dict):
    internal_links = []
    external_links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")) or not href:
            continue
        absolute_url = urljoin(base_url, href)
        if not absolute_url.startswith(("http://", "https://")):
            continue
        link_domain = urlparse(absolute_url).netloc
        if link_domain.replace("www.", "") == domain.replace("www.", ""):
            internal_links.append(absolute_url)
        else:
            external_links.append(absolute_url)

    broken_count = 0
    checked = 0
    broken_targets = set()
    for link in set(internal_links + external_links):
        if checked >= MAX_LINKS_TO_CHECK:
            break

        # If this URL was already crawled, reuse its known status code.
        if link in crawled_status_map:
            status = crawled_status_map[link]
            if status is None or status >= 400:
                broken_count += 1
                broken_targets.add(link)
            checked += 1
            continue

        try:
            resp = requests.head(
                link, headers={"User-Agent": USER_AGENT},
                timeout=LINK_CHECK_TIMEOUT, allow_redirects=True,
            )
            if resp.status_code >= 400:
                broken_count += 1
                broken_targets.add(link)
        except requests.exceptions.RequestException:
            broken_count += 1
            broken_targets.add(link)
        checked += 1

    # Deduped, normalized-ish list of internal link targets (used to build
    # the internal link graph and detect orphan pages). Capped to keep the
    # payload and downstream graph rendering bounded for very link-heavy pages.
    internal_link_targets = list(dict.fromkeys(internal_links))[:200]

    return {
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "broken_links": broken_count,
        "internal_link_targets": internal_link_targets,
        "broken_link_targets": list(broken_targets),
    }
