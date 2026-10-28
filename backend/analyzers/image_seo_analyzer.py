"""
analyzers/image_seo_analyzer.py

Reviews all <img> tags on a page and flags those missing a descriptive
ALT attribute, missing explicit width/height (a common cause of layout
shift), or using a generic, non-descriptive filename (e.g. "IMG_1234.jpg")
instead of a keyword-relevant one.
"""

import re
from urllib.parse import urlparse

GENERIC_FILENAME_PATTERN = re.compile(
    r"^(img|image|dsc|photo|pic|screenshot|untitled)[\s_\-]?\d*\.\w+$", re.IGNORECASE
)


def _is_generic_filename(src: str) -> bool:
    if not src:
        return True
    filename = urlparse(src).path.rsplit("/", 1)[-1]
    if not filename:
        return True
    return bool(GENERIC_FILENAME_PATTERN.match(filename))


def analyze_images(soup):
    images = soup.find_all("img")
    image_details = []
    missing_alt_count = 0
    missing_dimensions_count = 0
    non_descriptive_count = 0

    for img in images:
        src = img.get("src", "")
        alt = img.get("alt", "")
        has_alt = bool(alt and alt.strip())
        has_dimensions = bool(img.get("width")) and bool(img.get("height"))
        is_generic_name = _is_generic_filename(src)

        if not has_alt:
            missing_alt_count += 1
        if not has_dimensions:
            missing_dimensions_count += 1
        if is_generic_name:
            non_descriptive_count += 1

        image_details.append({
            "src": src, "alt": alt, "has_alt": has_alt,
            "has_dimensions": has_dimensions, "is_generic_name": is_generic_name,
        })

    return {
        "image_count": len(images),
        "images_missing_alt": missing_alt_count,
        "images_missing_dimensions": missing_dimensions_count,
        "non_descriptive_images": non_descriptive_count,
        "image_details": image_details,
    }

