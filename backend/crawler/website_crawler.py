"""
crawler/website_crawler.py

Crawls a target website starting from its root URL using a breadth-first
search, staying within the same domain, up to a configurable page limit
and depth limit. Each fetched page's HTML, status code, response time,
size, and HTTPS status are returned for downstream analysis.
"""

import time
from collections import deque
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

USER_AGENT = "SEOCriticsStudioBot/1.0 (+educational-mini-project)"
REQUEST_TIMEOUT = 10


def normalize_url(url: str) -> str:
    """Strip URL fragments and trailing slashes for consistent deduplication."""
    parsed = urlparse(url)
    path = parsed.path if parsed.path else "/"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def is_same_domain(url: str, domain: str) -> bool:
    return urlparse(url).netloc.replace("www.", "") == domain.replace("www.", "")


def fetch_page(url: str):
    """Fetch a single URL and capture response metadata, including the
    redirect chain (the sequence of URLs hopped through before the final
    response), used by the redirect analysis feature."""
    start = time.time()
    try:
        response = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT, allow_redirects=True
        )
        elapsed_ms = int((time.time() - start) * 1000)
        redirect_chain = [r.url for r in response.history] + [response.url] if response.history else []
        return {
            "url": url,
            "status_code": response.status_code,
            "html": response.text if "text/html" in response.headers.get("Content-Type", "") else "",
            "response_time_ms": elapsed_ms,
            "page_size_kb": round(len(response.content) / 1024, 2),
            "is_https": url.startswith("https://"),
            "redirect_count": len(response.history),
            "redirect_chain": redirect_chain,
            "final_url": response.url,
            "error": None,
        }
    except requests.exceptions.RequestException as exc:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "url": url,
            "status_code": None,
            "html": "",
            "response_time_ms": elapsed_ms,
            "page_size_kb": 0,
            "is_https": url.startswith("https://"),
            "redirect_count": 0,
            "redirect_chain": [],
            "final_url": url,
            "error": str(exc),
        }


def extract_internal_links(html: str, base_url: str, domain: str):
    """Extract same-domain links from a page's HTML for further crawling."""
    links = set()
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        return links

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute_url = urljoin(base_url, href)
        if is_same_domain(absolute_url, domain) and absolute_url.startswith(("http://", "https://")):
            links.add(normalize_url(absolute_url))
    return links


def crawl_website(root_url: str, max_pages: int = 10, max_depth: int = 2):
    """
    Perform a breadth-first crawl of a website.

    Returns a list of page dicts:
        {url, depth, status_code, html, response_time_ms,
         page_size_kb, is_https, error}
    """
    root_url = normalize_url(root_url)
    domain = urlparse(root_url).netloc

    visited = set()
    queue = deque([(root_url, 0)])
    results = []

    while queue and len(results) < max_pages:
        current_url, depth = queue.popleft()

        if current_url in visited or depth > max_depth:
            continue
        visited.add(current_url)

        page_data = fetch_page(current_url)
        page_data["depth"] = depth
        results.append(page_data)

        if page_data["html"] and depth < max_depth:
            internal_links = extract_internal_links(page_data["html"], current_url, domain)
            for link in internal_links:
                if link not in visited and len(results) + len(queue) < max_pages:
                    queue.append((link, depth + 1))

    return results, domain
