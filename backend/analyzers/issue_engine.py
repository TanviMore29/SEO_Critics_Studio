"""
analyzers/issue_engine.py

Transforms the results already produced by the existing analyzers
(metadata, technical SEO, links, images, advanced signals, sitemap,
robots.txt) into a flat list of structured "issues" for the Issue
Explorer, Page Details drawer, and Scan Comparison features.

This module does not re-crawl or re-analyze anything — it is a pure
aggregation layer over data the pipeline already computed in
`main.py`'s `run_scan()`. It also does not duplicate the *scoring* or
*recommendation* logic in `scoring/score_calculator.py` and
`recommendations/recommendation_engine.py`; those remain the source of
truth for the 100-point score and the aggregate recommendation list.
The issue engine instead produces one issue per *instance* (e.g. one
"Missing title" issue per affected page) so the Issue Explorer and
Page Details views can show exactly where a problem occurs.

Severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFO.
"""

CATEGORY_LINKS = "links"
CATEGORY_METADATA = "metadata"
CATEGORY_TECHNICAL = "technical"
CATEGORY_IMAGES = "images"
CATEGORY_SITEMAP = "sitemap"
CATEGORY_ROBOTS = "robots"
CATEGORY_PERFORMANCE = "performance"
CATEGORY_MOBILE = "mobile"
CATEGORY_SOCIAL = "social"
CATEGORY_DUPLICATE = "duplicate"
CATEGORY_REDIRECT = "redirect"


def _issue(issue_type, category, severity, title, description,
           affected_url=None, affected_count=1, recommendation="", evidence=None):
    return {
        "issue_type": issue_type,
        "category": category,
        "severity": severity,
        "title": title,
        "description": description,
        "affected_url": affected_url,
        "affected_count": affected_count,
        "recommendation": recommendation,
        "evidence": evidence or {},
    }


def duplicate_groups(pages: list, field: str):
    """Group pages by an exact value of `field`, returning only groups with 2+ members."""
    groups = {}
    for p in pages:
        value = p.get(field)
        if not value:
            continue
        groups.setdefault(value, []).append(p["page_url"])
    return {value: urls for value, urls in groups.items() if len(urls) > 1}


def generate_issues(pages: list, sitemap_data: dict, robots_data: dict) -> list:
    """Generate the full per-instance issue list for a scanned website."""
    issues = []

    for p in pages:
        url = p.get("page_url")

        # ---------------- Metadata ----------------
        if not p.get("title"):
            issues.append(_issue("missing_title", CATEGORY_METADATA, "HIGH",
                "Missing title", "This page has no <title> tag.", url,
                recommendation="Add a unique, descriptive <title> tag (10–60 characters)."))
        elif not (10 <= len(p["title"]) <= 60):
            severity = "LOW" if len(p["title"]) < 10 else "MEDIUM"
            issues.append(_issue("title_length", CATEGORY_METADATA, severity,
                "Title too short" if len(p["title"]) < 10 else "Title too long",
                f"Title is {len(p['title'])} characters (recommended: 10–60).", url,
                recommendation="Adjust the title length to fall within the recommended range.",
                evidence={"title": p["title"], "length": len(p["title"])}))

        if not p.get("meta_description"):
            issues.append(_issue("missing_description", CATEGORY_METADATA, "HIGH",
                "Missing meta description", "This page has no meta description.", url,
                recommendation="Add a unique meta description (50–160 characters)."))
        elif not (50 <= len(p["meta_description"]) <= 160):
            issues.append(_issue("description_length", CATEGORY_METADATA, "MEDIUM",
                "Meta description length off",
                f"Description is {len(p['meta_description'])} characters (recommended: 50–160).", url,
                recommendation="Adjust the meta description length.",
                evidence={"length": len(p["meta_description"])}))

        # ---------------- Technical ----------------
        if (p.get("h1_count") or 0) == 0:
            issues.append(_issue("missing_h1", CATEGORY_TECHNICAL, "HIGH",
                "Missing H1", "This page has no H1 heading.", url,
                recommendation="Add exactly one H1 tag describing the page's main topic."))
        elif p.get("h1_count", 0) > 1:
            issues.append(_issue("multiple_h1", CATEGORY_TECHNICAL, "MEDIUM",
                "Multiple H1 tags", f"This page has {p['h1_count']} H1 tags.", url,
                recommendation="Use a single H1 tag per page.",
                evidence={"h1_count": p["h1_count"]}))

        if not p.get("canonical_url"):
            issues.append(_issue("missing_canonical", CATEGORY_TECHNICAL, "LOW",
                "Missing canonical tag", "No canonical URL is declared for this page.", url,
                recommendation="Add a <link rel=\"canonical\"> tag."))
        elif p.get("canonical_url") != url:
            issues.append(_issue("canonical_mismatch", CATEGORY_TECHNICAL, "INFO",
                "Canonical points elsewhere",
                f"This page's canonical URL points to a different URL ({p['canonical_url']}). "
                f"This may be intentional.", url,
                recommendation="Confirm this is intentional; otherwise point the canonical at this page.",
                evidence={"canonical_url": p["canonical_url"]}))

        if (p.get("word_count") or 0) < 300:
            issues.append(_issue("thin_content", CATEGORY_TECHNICAL, "LOW",
                "Thin content", f"Only {p.get('word_count', 0)} words of visible text.", url,
                recommendation="Expand the content or consolidate with a related page.",
                evidence={"word_count": p.get("word_count", 0)}))

        if not p.get("html_lang"):
            issues.append(_issue("missing_lang", CATEGORY_TECHNICAL, "LOW",
                "Missing declared language", "No <html lang=\"...\"> attribute found.", url,
                recommendation="Declare the page's language on the <html> tag."))

        if not p.get("has_structured_data"):
            issues.append(_issue("missing_structured_data", CATEGORY_TECHNICAL, "INFO",
                "No structured data", "No JSON-LD or microdata structured data found.", url,
                recommendation="Consider adding schema.org structured data for rich results."))

        # ---------------- Mobile ----------------
        if not p.get("has_viewport"):
            issues.append(_issue("missing_viewport", CATEGORY_MOBILE, "HIGH",
                "Missing viewport tag", "No <meta name=\"viewport\"> tag found.", url,
                recommendation="Add a responsive viewport meta tag."))

        # ---------------- Social ----------------
        if not p.get("has_open_graph"):
            issues.append(_issue("missing_open_graph", CATEGORY_SOCIAL, "INFO",
                "Missing Open Graph tags", "No Open Graph meta tags found.", url,
                recommendation="Add og:title, og:description, and og:image tags."))
        if not p.get("has_twitter_card"):
            issues.append(_issue("missing_twitter_card", CATEGORY_SOCIAL, "INFO",
                "Missing Twitter Card tags", "No Twitter Card meta tags found.", url,
                recommendation="Add Twitter Card meta tags."))

        # ---------------- Images ----------------
        if p.get("images_missing_alt", 0) > 0:
            issues.append(_issue("missing_alt", CATEGORY_IMAGES, "HIGH",
                "Images missing ALT text",
                f"{p['images_missing_alt']} of {p.get('image_count', 0)} image(s) are missing ALT text.", url,
                affected_count=p["images_missing_alt"],
                recommendation="Add descriptive ALT text to every meaningful image.",
                evidence={"missing_alt": p["images_missing_alt"], "total_images": p.get("image_count", 0)}))

        if p.get("images_missing_dimensions", 0) > 0:
            issues.append(_issue("missing_image_dimensions", CATEGORY_IMAGES, "LOW",
                "Images missing width/height",
                f"{p['images_missing_dimensions']} image(s) have no explicit dimensions.", url,
                affected_count=p["images_missing_dimensions"],
                recommendation="Set explicit width/height attributes to avoid layout shift."))

        if p.get("non_descriptive_images", 0) > 0:
            issues.append(_issue("generic_image_filename", CATEGORY_IMAGES, "LOW",
                "Non-descriptive image filenames",
                f"{p['non_descriptive_images']} image(s) use generic filenames (e.g. IMG_1234.jpg).", url,
                affected_count=p["non_descriptive_images"],
                recommendation="Rename images with descriptive, keyword-relevant filenames."))

        # ---------------- Links ----------------
        if p.get("broken_links", 0) > 0:
            issues.append(_issue("broken_link", CATEGORY_LINKS, "CRITICAL",
                "Broken links found", f"{p['broken_links']} broken link(s) detected on this page.", url,
                affected_count=p["broken_links"],
                recommendation="Fix or remove the broken links."))

        # ---------------- Performance ----------------
        if not p.get("is_https"):
            issues.append(_issue("http_not_https", CATEGORY_PERFORMANCE, "HIGH",
                "Served over HTTP, not HTTPS", "This page was not served over HTTPS.", url,
                recommendation="Migrate to HTTPS site-wide."))

        if (p.get("response_time_ms") or 0) > 1500:
            issues.append(_issue("slow_response", CATEGORY_PERFORMANCE, "MEDIUM",
                "Slow response time", f"Response took {p['response_time_ms']}ms (threshold: 1500ms).", url,
                recommendation="Investigate server response time or hosting.",
                evidence={"response_time_ms": p["response_time_ms"]}))

        if (p.get("page_size_kb") or 0) > 1500:
            issues.append(_issue("large_page", CATEGORY_PERFORMANCE, "MEDIUM",
                "Large page size", f"Page is {p['page_size_kb']}KB (threshold: 1500KB).", url,
                recommendation="Compress images and minify assets.",
                evidence={"page_size_kb": p["page_size_kb"]}))

        # ---------------- Redirects ----------------
        chain = p.get("redirect_chain") or []
        if len(chain) > 2:  # start + at least 2 hops before final
            issues.append(_issue("redirect_chain", CATEGORY_REDIRECT, "MEDIUM",
                "Redirect chain", f"{len(chain) - 1} redirect hop(s) before reaching the final URL.", url,
                recommendation="Point the original link directly at the final destination.",
                evidence={"chain": chain}))
        if len(chain) != len(set(chain)) and chain:
            issues.append(_issue("redirect_loop", CATEGORY_REDIRECT, "CRITICAL",
                "Possible redirect loop", "A URL repeats within this page's redirect chain.", url,
                recommendation="Investigate and remove the circular redirect.",
                evidence={"chain": chain}))

    # ---------------- Site-level: duplicates ----------------
    for value, urls in duplicate_groups(pages, "title").items():
        issues.append(_issue("duplicate_title", CATEGORY_DUPLICATE, "HIGH",
            "Duplicate title", f'{len(urls)} pages share the title "{value}".', None,
            affected_count=len(urls), recommendation="Give each page a unique title.",
            evidence={"value": value, "urls": urls}))

    for value, urls in duplicate_groups(pages, "meta_description").items():
        issues.append(_issue("duplicate_description", CATEGORY_DUPLICATE, "MEDIUM",
            "Duplicate meta description", f"{len(urls)} pages share the same meta description.", None,
            affected_count=len(urls), recommendation="Write a unique description for each page.",
            evidence={"value": value, "urls": urls}))

    for value, urls in duplicate_groups(pages, "canonical_url").items():
        if len(set(urls)) > 1:  # only interesting if it spans multiple distinct pages
            issues.append(_issue("duplicate_canonical", CATEGORY_DUPLICATE, "LOW",
                "Multiple pages share a canonical URL", f"{len(urls)} pages declare the same canonical target.", None,
                affected_count=len(urls), recommendation="Confirm this consolidation is intentional.",
                evidence={"value": value, "urls": urls}))

    # ---------------- Site-level: sitemap ----------------
    if not sitemap_data.get("exists"):
        issues.append(_issue("sitemap_missing", CATEGORY_SITEMAP, "HIGH",
            "sitemap.xml not found", "No sitemap.xml was found at the site root.", None,
            recommendation="Create and publish a sitemap.xml."))
    elif not sitemap_data.get("is_valid"):
        issues.append(_issue("sitemap_invalid", CATEGORY_SITEMAP, "MEDIUM",
            "sitemap.xml invalid", "A sitemap.xml exists but could not be parsed as valid XML.", None,
            recommendation="Validate the sitemap against the sitemap protocol."))

    # ---------------- Site-level: robots.txt ----------------
    if not robots_data.get("exists"):
        issues.append(_issue("robots_missing", CATEGORY_ROBOTS, "MEDIUM",
            "robots.txt not found", "No robots.txt was found at the site root.", None,
            recommendation="Create a robots.txt file."))
    elif not robots_data.get("sitemap_reference"):
        issues.append(_issue("robots_no_sitemap_ref", CATEGORY_ROBOTS, "LOW",
            "robots.txt doesn't reference sitemap", "robots.txt exists but has no Sitemap: line.", None,
            recommendation="Add a Sitemap: line pointing to your sitemap.xml."))

    return issues


SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


def sort_issues(issues: list) -> list:
    return sorted(issues, key=lambda i: SEVERITY_ORDER.get(i["severity"], 5))
