"""
analyzers/robots_analyzer.py

Checks for the presence and directives defined in the website's
robots.txt file, and (new) parses it into per-user-agent rule groups so
crawled pages can be checked against the Disallow/Allow rules.

SCOPE NOTE: this is a simplified, educational parser — not a full
implementation of the robots.txt specification (RFC 9309) or Google's
extended rules. It supports: multiple "User-agent" groups, "Disallow"
and "Allow" directives, "Sitemap" references, a trailing "*" wildcard,
and a trailing "$" end-anchor. It does NOT support mid-pattern wildcards,
crawl-delay, or group precedence edge cases the way production crawlers
do. This is clearly labeled wherever the parsed data is shown.
"""

from urllib.parse import urlparse
import requests

USER_AGENT = "SEOCriticsStudioBot/1.0 (+educational-mini-project)"
REQUEST_TIMEOUT = 10


def _parse_groups(text: str):
    """Parse robots.txt text into a list of {user_agent, disallow, allow} groups."""
    groups = []
    current_agents = []
    current_group = None

    def start_new_group(agent):
        nonlocal current_group
        current_group = {"user_agent": agent, "disallow": [], "allow": []}
        groups.append(current_group)

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()

        if key == "user-agent":
            # A run of consecutive User-agent lines belongs to the same group.
            if current_group is None or current_group["disallow"] or current_group["allow"]:
                start_new_group(value)
                current_agents = [value]
            else:
                current_group["user_agent"] = f'{current_group["user_agent"]}, {value}'
                current_agents.append(value)
        elif key == "disallow" and current_group is not None:
            if value:
                current_group["disallow"].append(value)
        elif key == "allow" and current_group is not None:
            if value:
                current_group["allow"].append(value)

    return groups


def _pattern_matches(path: str, pattern: str) -> bool:
    """Simplified robots.txt pattern match: supports trailing '*' wildcard
    and trailing '$' end-anchor. See module docstring for scope limits."""
    if not pattern:
        return False
    if pattern.endswith("$"):
        return path == pattern[:-1]
    if pattern.endswith("*"):
        return path.startswith(pattern[:-1])
    return path.startswith(pattern)


def is_path_blocked(path: str, groups: list, user_agent: str = "*") -> bool:
    """Check whether `path` is disallowed for the given user-agent, using the
    longest-matching-rule-wins heuristic (a simplified approximation of the
    real specification's precedence rules)."""
    applicable_rules = []
    for group in groups:
        agents = [a.strip().lower() for a in group["user_agent"].split(",")]
        if user_agent.lower() in agents or "*" in agents:
            for rule in group["disallow"]:
                if _pattern_matches(path, rule):
                    applicable_rules.append((len(rule), "disallow"))
            for rule in group["allow"]:
                if _pattern_matches(path, rule):
                    applicable_rules.append((len(rule), "allow"))

    if not applicable_rules:
        return False
    applicable_rules.sort(key=lambda r: r[0], reverse=True)
    return applicable_rules[0][1] == "disallow"


def analyze_robots(root_url: str):
    parsed = urlparse(root_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    result = {
        "robots_url": robots_url,
        "exists": False,
        "disallowed_paths": [],
        "sitemap_reference": None,
        "user_agent_groups": [],
        "rule_count": 0,
    }

    try:
        response = requests.get(
            robots_url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200 and response.text.strip():
            result["exists"] = True
            groups = _parse_groups(response.text)
            result["user_agent_groups"] = groups
            result["rule_count"] = sum(len(g["disallow"]) + len(g["allow"]) for g in groups)

            # Keep the original flattened fields for backward compatibility
            # with the existing scoring/recommendation logic.
            seen_paths = []
            for group in groups:
                for path in group["disallow"]:
                    if path not in seen_paths:
                        seen_paths.append(path)
            result["disallowed_paths"] = seen_paths

            for line in response.text.splitlines():
                line = line.strip()
                if line.lower().startswith("sitemap:"):
                    result["sitemap_reference"] = line.split(":", 1)[1].strip()
                    break
    except requests.exceptions.RequestException:
        pass

    return result
