"""
analyzers/metadata_analyzer.py

Extracts and evaluates <title>, <meta name="description">, and
<meta name="robots"> tags from a parsed HTML page.
"""


def analyze_metadata(soup):
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    description_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = description_tag["content"].strip() if description_tag and description_tag.get("content") else ""

    robots_tag = soup.find("meta", attrs={"name": "robots"})
    meta_robots = robots_tag["content"].strip() if robots_tag and robots_tag.get("content") else ""

    return {
        "title": title,
        "title_length": len(title),
        "meta_description": meta_description,
        "meta_description_length": len(meta_description),
        "meta_robots": meta_robots,
    }
