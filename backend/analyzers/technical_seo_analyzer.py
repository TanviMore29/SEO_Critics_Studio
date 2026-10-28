"""
analyzers/technical_seo_analyzer.py

Checks canonical tag presence, H1/H2 heading structure, and
visible word count of a page.
"""

from bs4 import BeautifulSoup


def analyze_technical(html: str, soup):
    """
    `soup` is used for canonical/heading lookups (read-only).
    A fresh soup is parsed from `html` for word-count extraction so the
    shared `soup` instance passed between analyzers is never mutated.
    """
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_tag["href"].strip() if canonical_tag and canonical_tag.get("href") else ""

    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")

    # Use an independent soup copy so script/style removal doesn't
    # affect other analyzers relying on the shared soup object.
    text_soup = BeautifulSoup(html, "lxml")
    for tag in text_soup(["script", "style", "noscript"]):
        tag.decompose()
    visible_text = text_soup.get_text(separator=" ", strip=True)
    word_count = len(visible_text.split())

    return {
        "canonical": canonical,
        "h1_count": len(h1_tags),
        "h2_count": len(h2_tags),
        "word_count": word_count,
    }
