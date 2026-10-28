"""
analyzers/keyword_analyzer.py

Simple, deterministic word-frequency analysis of a page's visible text.
This surfaces the terms a page appears to be "about" from a pure counting
standpoint (stopwords removed) so the report can flag keyword focus and
title/H1 alignment. This is plain text statistics, not machine learning
or an AI model.
"""

import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "for", "of",
    "to", "in", "on", "at", "by", "with", "from", "as", "is", "are", "was",
    "were", "be", "been", "being", "this", "that", "these", "those", "it",
    "its", "into", "about", "over", "after", "before", "between", "out",
    "up", "down", "off", "again", "further", "than", "too", "very", "can",
    "will", "just", "not", "no", "nor", "so", "such", "own", "same", "we",
    "you", "your", "our", "us", "i", "he", "she", "they", "them", "his",
    "her", "their", "what", "which", "who", "whom", "how", "all", "any",
    "each", "more", "most", "other", "some", "there", "here", "when",
    "where", "why", "do", "does", "did", "doing", "have", "has", "had",
    "having", "am", "an", "also", "may", "might", "shall", "should",
    "would", "could",
}

WORD_PATTERN = re.compile(r"[a-zA-Z]{3,}")


def analyze_keywords(soup, top_n: int = 8) -> dict:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True).lower()

    words = WORD_PATTERN.findall(text)
    filtered = [w for w in words if w not in STOPWORDS]

    if not filtered:
        return {"top_keywords": [], "keyword_density": {}}

    counts = Counter(filtered)
    total_words = len(filtered)
    top_keywords = []
    for word, count in counts.most_common(top_n):
        density = round((count / total_words) * 100, 2)
        top_keywords.append({"keyword": word, "count": count, "density": density})

    return {"top_keywords": top_keywords, "total_words": total_words}


def merge_site_keywords(page_keyword_lists: list, top_n: int = 10) -> list:
    """Aggregate per-page top keywords into a site-wide ranked list."""
    combined = Counter()
    for kw_list in page_keyword_lists:
        for item in kw_list:
            combined[item["keyword"]] += item["count"]

    total = sum(combined.values()) or 1
    result = []
    for word, count in combined.most_common(top_n):
        result.append({
            "keyword": word,
            "count": count,
            "density": round((count / total) * 100, 2),
        })
    return result
