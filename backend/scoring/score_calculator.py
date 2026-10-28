"""
scoring/score_calculator.py

Computes the overall SEO score (out of 100) and category breakdown
for a scanned website, following the distribution defined in the SRS:

    Metadata        20
    Technical SEO   20
    Images          15
    Links           15
    Sitemap         10
    robots.txt      10
    Performance     10
    ------------------
    Total          100
"""

MAX_METADATA = 20
MAX_TECHNICAL = 20
MAX_IMAGES = 15
MAX_LINKS = 15
MAX_SITEMAP = 10
MAX_ROBOTS = 10
MAX_PERFORMANCE = 10


def _score_metadata(pages: list) -> float:
    if not pages:
        return 0
    titles = [p["title"] for p in pages if p.get("title")]
    descriptions = [p["meta_description"] for p in pages if p.get("meta_description")]

    per_page_scores = []
    for p in pages:
        score = 0
        # Title present and reasonable length (10-60 chars) -> 10 pts
        title_len = len(p.get("title") or "")
        if title_len > 0:
            score += 6 if not (10 <= title_len <= 60) else 10
        # Meta description present and reasonable length (50-160 chars) -> 10 pts
        desc_len = len(p.get("meta_description") or "")
        if desc_len > 0:
            score += 6 if not (50 <= desc_len <= 160) else 10
        per_page_scores.append(score)

    avg_score = sum(per_page_scores) / len(per_page_scores)

    # Penalize duplicate titles / descriptions across the site
    duplicate_penalty = 0
    if titles and len(titles) != len(set(titles)):
        duplicate_penalty += 3
    if descriptions and len(descriptions) != len(set(descriptions)):
        duplicate_penalty += 2

    final = max(0, avg_score - duplicate_penalty)
    return round(min(final, MAX_METADATA), 2)


def _score_technical(pages: list) -> float:
    if not pages:
        return 0
    per_page_scores = []
    for p in pages:
        score = 0
        if p.get("canonical"):
            score += 6
        if p.get("h1_count") == 1:
            score += 8
        elif p.get("h1_count", 0) > 1:
            score += 4
        if p.get("word_count", 0) >= 300:
            score += 6
        elif p.get("word_count", 0) >= 100:
            score += 3
        per_page_scores.append(score)
    avg_score = sum(per_page_scores) / len(per_page_scores)
    return round(min(avg_score, MAX_TECHNICAL), 2)


def _score_images(pages: list) -> float:
    total_images = sum(p.get("image_count", 0) for p in pages)
    missing_alt = sum(p.get("images_missing_alt", 0) for p in pages)
    if total_images == 0:
        return MAX_IMAGES  # no images = no ALT-tag issues
    coverage_ratio = 1 - (missing_alt / total_images)
    return round(coverage_ratio * MAX_IMAGES, 2)


def _score_links(pages: list) -> float:
    if not pages:
        return 0
    total_links = sum(p.get("internal_links", 0) + p.get("external_links", 0) for p in pages)
    broken_links = sum(p.get("broken_links", 0) for p in pages)
    if total_links == 0:
        return MAX_LINKS
    broken_ratio = broken_links / total_links
    score = MAX_LINKS * (1 - min(broken_ratio * 3, 1))  # heavier penalty per broken link
    return round(max(score, 0), 2)


def _score_sitemap(sitemap_data: dict) -> float:
    if not sitemap_data.get("exists"):
        return 0
    if not sitemap_data.get("is_valid"):
        return MAX_SITEMAP * 0.4
    return float(MAX_SITEMAP)


def _score_robots(robots_data: dict) -> float:
    if not robots_data.get("exists"):
        return 0
    score = MAX_ROBOTS * 0.7
    if robots_data.get("sitemap_reference"):
        score += MAX_ROBOTS * 0.3
    return round(min(score, MAX_ROBOTS), 2)


def _score_performance(pages: list) -> float:
    if not pages:
        return 0
    per_page_scores = []
    for p in pages:
        score = 0
        response_time = p.get("response_time_ms") or 99999
        if response_time <= 500:
            score += 4
        elif response_time <= 1500:
            score += 2
        if p.get("is_https"):
            score += 3
        page_size = p.get("page_size_kb") or 9999
        if page_size <= 500:
            score += 3
        elif page_size <= 1500:
            score += 1.5
        per_page_scores.append(score)
    avg_score = sum(per_page_scores) / len(per_page_scores)
    return round(min(avg_score, MAX_PERFORMANCE), 2)


def get_health_level(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 55:
        return "Average"
    if score >= 35:
        return "Poor"
    return "Critical"


def compute_score(pages: list, sitemap_data: dict, robots_data: dict) -> dict:
    metadata_score = _score_metadata(pages)
    technical_score = _score_technical(pages)
    images_score = _score_images(pages)
    links_score = _score_links(pages)
    sitemap_score = _score_sitemap(sitemap_data)
    robots_score = _score_robots(robots_data)
    performance_score = _score_performance(pages)

    overall_score = round(
        metadata_score + technical_score + images_score + links_score +
        sitemap_score + robots_score + performance_score, 2
    )

    return {
        "metadata_score": metadata_score,
        "technical_score": technical_score,
        "images_score": images_score,
        "links_score": links_score,
        "sitemap_score": sitemap_score,
        "robots_score": robots_score,
        "performance_score": performance_score,
        "overall_score": overall_score,
        "health_level": get_health_level(overall_score),
        "max_scores": {
            "metadata": MAX_METADATA,
            "technical": MAX_TECHNICAL,
            "images": MAX_IMAGES,
            "links": MAX_LINKS,
            "sitemap": MAX_SITEMAP,
            "robots": MAX_ROBOTS,
            "performance": MAX_PERFORMANCE,
        },
    }
