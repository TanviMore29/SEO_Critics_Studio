"""
recommendations/recommendation_engine.py

Generates a prioritized list of actionable SEO recommendations for a
scanned website.

IMPORTANT — scope note: this is a deterministic, rule-based engine. Every
recommendation is produced by checking scan results against fixed
thresholds (e.g. "title longer than 60 characters", "N images missing
ALT text"). There is no machine learning model and no external AI
service involved — this keeps the feature consistent with the project's
declared scope, which explicitly excludes an AI recommendation engine.
"""

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _pct(count: int, total: int) -> float:
    return round((count / total) * 100, 1) if total else 0.0


def generate_recommendations(pages: list, sitemap_data: dict, robots_data: dict) -> list:
    recs = []
    total_pages = len(pages) or 1

    def add(priority, category, title, description, affected=None):
        recs.append({
            "priority": priority,
            "category": category,
            "title": title,
            "description": description,
            "affected_pages": affected,
        })

    # ---------------- Metadata ----------------
    missing_title = [p for p in pages if not p.get("title")]
    if missing_title:
        add("high", "metadata", "Add missing page titles",
            f"{len(missing_title)} of {total_pages} pages ({_pct(len(missing_title), total_pages)}%) have no "
            f"<title> tag. Every indexable page should have a unique, descriptive title.",
            len(missing_title))

    titles = [p["title"] for p in pages if p.get("title")]
    if titles and len(titles) != len(set(titles)):
        dupes = len(titles) - len(set(titles))
        add("high", "metadata", "Fix duplicate page titles",
            f"{dupes} duplicate title(s) detected across the site. Search engines may struggle to "
            f"differentiate pages with identical titles — give each page a unique one.")

    bad_title_len = [p for p in pages if p.get("title") and not (10 <= len(p["title"]) <= 60)]
    if bad_title_len:
        add("medium", "metadata", "Adjust title length",
            f"{len(bad_title_len)} page(s) have a title outside the recommended 10–60 character range. "
            f"Titles that are too short lack context; titles that are too long get truncated in search results.",
            len(bad_title_len))

    missing_desc = [p for p in pages if not p.get("meta_description")]
    if missing_desc:
        add("high", "metadata", "Add missing meta descriptions",
            f"{len(missing_desc)} of {total_pages} pages ({_pct(len(missing_desc), total_pages)}%) have no "
            f"meta description. This is often the snippet shown under your result in search listings.",
            len(missing_desc))

    descs = [p["meta_description"] for p in pages if p.get("meta_description")]
    if descs and len(descs) != len(set(descs)):
        dupes = len(descs) - len(set(descs))
        add("medium", "metadata", "Fix duplicate meta descriptions",
            f"{dupes} duplicate meta description(s) found. Write a unique summary for each page.")

    bad_desc_len = [p for p in pages if p.get("meta_description") and not (50 <= len(p["meta_description"]) <= 160)]
    if bad_desc_len:
        add("medium", "metadata", "Adjust meta description length",
            f"{len(bad_desc_len)} page(s) have a meta description outside the recommended 50–160 character range.",
            len(bad_desc_len))

    # ---------------- Technical SEO ----------------
    no_h1 = [p for p in pages if (p.get("h1_count") or 0) == 0]
    if no_h1:
        add("high", "technical", "Add a primary heading (H1)",
            f"{len(no_h1)} page(s) have no H1 tag. The H1 tells both users and search engines the main "
            f"topic of the page.", len(no_h1))

    multi_h1 = [p for p in pages if (p.get("h1_count") or 0) > 1]
    if multi_h1:
        add("medium", "technical", "Use a single H1 per page",
            f"{len(multi_h1)} page(s) have more than one H1 tag. Keep exactly one H1 to give the page "
            f"a clear topical focus.", len(multi_h1))

    missing_canonical = [p for p in pages if not p.get("canonical_url")]
    if missing_canonical:
        add("low", "technical", "Add canonical tags",
            f"{len(missing_canonical)} page(s) have no canonical URL declared. Canonical tags help "
            f"prevent duplicate-content issues, especially for pages reachable via multiple URLs.",
            len(missing_canonical))

    thin_content = [p for p in pages if (p.get("word_count") or 0) < 300]
    if thin_content:
        add("low", "technical", "Expand thin content",
            f"{len(thin_content)} page(s) have fewer than 300 words of visible text. Thin pages tend to "
            f"rank worse — consider expanding the content or consolidating with a related page.",
            len(thin_content))

    missing_lang = [p for p in pages if not p.get("html_lang")]
    if missing_lang:
        add("low", "technical", "Declare page language",
            f"{len(missing_lang)} page(s) are missing the <html lang=\"...\"> attribute, which helps "
            f"search engines serve the page to the right regional audience.", len(missing_lang))

    missing_structured = [p for p in pages if not p.get("has_structured_data")]
    if missing_structured and len(missing_structured) == total_pages:
        add("low", "technical", "Add structured data (schema.org)",
            f"None of the scanned pages include structured data (JSON-LD or microdata). Structured data "
            f"can unlock rich results such as star ratings, breadcrumbs, or FAQ snippets.")

    # ---------------- Mobile ----------------
    missing_viewport = [p for p in pages if not p.get("has_viewport")]
    if missing_viewport:
        add("high", "mobile", "Add a responsive viewport tag",
            f"{len(missing_viewport)} of {total_pages} pages ({_pct(len(missing_viewport), total_pages)}%) "
            f"have no <meta name=\"viewport\"> tag, which usually means the page isn't optimized for "
            f"mobile screens — a significant ranking factor.", len(missing_viewport))

    # ---------------- Social ----------------
    missing_og = [p for p in pages if not p.get("has_open_graph")]
    if missing_og and len(missing_og) == total_pages:
        add("low", "social", "Add Open Graph tags",
            f"No Open Graph tags (og:title, og:description, og:image) were found. These control how "
            f"your pages look when shared on social platforms.")

    missing_twitter = [p for p in pages if not p.get("has_twitter_card")]
    if missing_twitter and len(missing_twitter) == total_pages:
        add("low", "social", "Add Twitter Card tags",
            f"No Twitter Card meta tags were found. Adding them improves how links appear when shared "
            f"on X/Twitter.")

    # ---------------- Images ----------------
    total_images = sum(p.get("image_count", 0) for p in pages)
    missing_alt = sum(p.get("images_missing_alt", 0) for p in pages)
    if missing_alt:
        add("high", "images", "Add ALT text to images",
            f"{missing_alt} of {total_images} images ({_pct(missing_alt, total_images)}%) are missing "
            f"ALT text. ALT text helps accessibility and lets search engines understand image content.",
            missing_alt)

    missing_dims = sum(p.get("images_missing_dimensions", 0) for p in pages)
    if missing_dims:
        add("low", "images", "Set explicit image dimensions",
            f"{missing_dims} image(s) have no width/height attributes, which can cause layout shift "
            f"while the page loads. Set explicit dimensions on <img> tags.", missing_dims)

    generic_names = sum(p.get("non_descriptive_images", 0) for p in pages)
    if generic_names:
        add("low", "images", "Use descriptive image filenames",
            f"{generic_names} image(s) use generic filenames (e.g. \"IMG_1234.jpg\"). Descriptive, "
            f"keyword-relevant filenames give search engines extra context.", generic_names)

    # ---------------- Links ----------------
    total_broken = sum(p.get("broken_links", 0) for p in pages)
    if total_broken:
        add("high", "links", "Fix broken links",
            f"{total_broken} broken link(s) were detected across the scanned pages. Broken links hurt "
            f"user experience and waste crawl budget.", total_broken)

    # ---------------- Sitemap ----------------
    if not sitemap_data.get("exists"):
        add("high", "sitemap", "Create a sitemap.xml",
            "No sitemap.xml was found at the site root. A sitemap helps search engines discover and "
            "crawl your pages more efficiently.")
    elif not sitemap_data.get("is_valid"):
        add("medium", "sitemap", "Fix sitemap.xml formatting",
            "A sitemap.xml was found but could not be parsed as valid XML with listed URLs. Validate "
            "it against the sitemap protocol.")

    # ---------------- robots.txt ----------------
    if not robots_data.get("exists"):
        add("medium", "robots", "Create a robots.txt file",
            "No robots.txt was found. Even a permissive robots.txt is useful — it's also where you "
            "reference your sitemap.xml for crawlers.")
    elif not robots_data.get("sitemap_reference"):
        add("low", "robots", "Reference your sitemap in robots.txt",
            "robots.txt exists but doesn't reference a sitemap. Adding a \"Sitemap:\" line helps "
            "crawlers find it automatically.")

    # ---------------- Performance ----------------
    non_https = [p for p in pages if not p.get("is_https")]
    if non_https:
        add("high", "performance", "Migrate to HTTPS",
            f"{len(non_https)} page(s) were served without HTTPS. HTTPS is a confirmed ranking signal "
            f"and is expected by modern browsers.", len(non_https))

    slow_pages = [p for p in pages if (p.get("response_time_ms") or 0) > 1500]
    if slow_pages:
        add("medium", "performance", "Improve slow-loading pages",
            f"{len(slow_pages)} page(s) took over 1.5s to respond. Slower pages tend to have higher "
            f"bounce rates and can be down-ranked.", len(slow_pages))

    large_pages = [p for p in pages if (p.get("page_size_kb") or 0) > 1500]
    if large_pages:
        add("medium", "performance", "Reduce page weight",
            f"{len(large_pages)} page(s) exceed 1.5MB in size. Consider compressing images and "
            f"minifying assets to improve load time.", len(large_pages))

    recs.sort(key=lambda r: PRIORITY_ORDER.get(r["priority"], 3))
    return recs
