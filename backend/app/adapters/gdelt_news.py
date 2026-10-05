"""Discover publisher links from GDELT; no article body is inferred."""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from urllib.parse import urlparse

import httpx


@dataclass(frozen=True)
class NewsItemInput:
    provider: str
    source_key: str
    title: str
    url: str
    domain: str
    published_at: datetime | None
    source_seen_at: datetime
    available_at: datetime


def parse_gdelt_articles(data: dict, fetched_at: datetime) -> list[NewsItemInput]:
    if fetched_at.tzinfo is None:
        raise ValueError("fetch time must be timezone-aware")
    if not isinstance(data.get("articles", []), list):
        raise ValueError("GDELT articles must be an array")
    result = []
    seen_keys = set()
    for item in data.get("articles", []):
        try:
            url = item["url"].strip()
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc or parsed.username:
                continue
            title = item["title"].strip()
            if not title:
                continue
            seen_at = datetime.strptime(item["seendate"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            if seen_at > fetched_at:
                continue
            key = sha256(url.encode()).hexdigest()
            if key in seen_keys:
                continue
            seen_keys.add(key)
            result.append(NewsItemInput("gdelt", key, title, url, parsed.hostname or "", None, seen_at, fetched_at))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    return result


def discover_articles(query: str, client: httpx.Client, fetched_at: datetime | None = None) -> list[NewsItemInput]:
    if not query or len(query) > 100:
        raise ValueError("invalid news query")
    response = client.get("https://api.gdeltproject.org/api/v2/doc/doc",
                          params={"query": query, "mode": "artlist", "format": "json", "maxrecords": 50,
                                  "sort": "datedesc"}, timeout=20)
    response.raise_for_status()
    return parse_gdelt_articles(response.json(), fetched_at or datetime.now(timezone.utc))
