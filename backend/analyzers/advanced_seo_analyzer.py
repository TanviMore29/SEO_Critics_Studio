"""
analyzers/advanced_seo_analyzer.py

Additional technical SEO signals beyond the core checks: mobile-friendly
viewport tag, structured data (schema.org JSON-LD), Open Graph tags,
Twitter Card tags, declared page language, and favicon presence.

These are all deterministic, rule-based checks against the parsed HTML —
no machine learning or external AI service is involved, consistent with
the project's scope (see SRS section "Important Requirements").
"""


def analyze_advanced(soup) -> dict:
    # Mobile-friendliness: a <meta name="viewport"> tag is the standard
    # signal that a page has a responsive layout.
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = bool(viewport_tag and viewport_tag.get("content"))

    # Structured data: JSON-LD is the most common modern format; also
    # check for legacy microdata (itemscope) as a fallback signal.
    json_ld_tags = soup.find_all("script", attrs={"type": "application/ld+json"})
    microdata_tags = soup.find_all(attrs={"itemscope": True})
    has_structured_data = bool(json_ld_tags or microdata_tags)

    # Open Graph tags (used by Facebook, LinkedIn, etc. when a page is shared)
    og_tags = soup.find_all("meta", attrs={"property": lambda p: p and p.startswith("og:")})
    has_open_graph = len(og_tags) >= 2  # require at least 2 for a meaningful signal

    # Twitter Card tags
    twitter_tags = soup.find_all("meta", attrs={"name": lambda n: n and n.startswith("twitter:")})
    has_twitter_card = len(twitter_tags) >= 1

    # Declared page language (helps search engines serve the right locale)
    html_tag = soup.find("html")
    html_lang = html_tag.get("lang", "").strip() if html_tag else ""

    # Character encoding declaration
    charset_tag = soup.find("meta", attrs={"charset": True})
    has_charset = bool(charset_tag) or bool(
        soup.find("meta", attrs={"http-equiv": lambda h: h and h.lower() == "content-type"})
    )

    # Favicon
    favicon_tag = soup.find("link", attrs={"rel": lambda r: r and "icon" in " ".join(r).lower() if isinstance(r, list) else r and "icon" in r.lower()})
    has_favicon = bool(favicon_tag)

    return {
        "has_viewport": has_viewport,
        "has_structured_data": has_structured_data,
        "has_open_graph": has_open_graph,
        "has_twitter_card": has_twitter_card,
        "html_lang": html_lang,
        "has_charset": has_charset,
        "has_favicon": has_favicon,
    }
