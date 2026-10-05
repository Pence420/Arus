"""Official ANTARA Bursa RSS headline links for a small local watchlist."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import httpx

from app.adapters.gdelt_news import NewsItemInput


FEED_URL = "https://www.antaranews.com/rss/ekonomi-bursa.xml"
ALIASES = {
    "BBRI": ("bank rakyat indonesia",),
    "BBCA": ("bank central asia",),
    "BMRI": ("bank mandiri",),
    "BBNI": ("bank negara indonesia",),
    "TLKM": ("telkom indonesia", "telkomsel"),
    "ASII": ("astra international",),
}


def _matches(title: str, ticker: str) -> bool:
    if re.search(rf"(?<![A-Za-z0-9]){re.escape(ticker)}(?![A-Za-z0-9])", title, re.I):
        return True
    lowered = title.casefold()
    return any(alias in lowered for alias in ALIASES.get(ticker, ()))


def parse_antara_feed(xml_text: str, ticker: str, fetched_at: datetime) -> list[NewsItemInput]:
    if fetched_at.tzinfo is None or not re.fullmatch(r"[A-Z]{4,5}", ticker):
        raise ValueError("ticker and fetch time must be valid")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError("ANTARA RSS is not valid XML") from exc
    result = []
    seen = set()
    for node in root.findall("./channel/item"):
        title = (node.findtext("title") or "").strip()
        url = (node.findtext("link") or "").strip()
        published_raw = (node.findtext("pubDate") or "").strip()
        parsed = urlparse(url)
        if not title or not _matches(title, ticker) or parsed.scheme != "https" or parsed.hostname not in {
            "www.antaranews.com", "antaranews.com"
        }:
            continue
        try:
            published = parsedate_to_datetime(published_raw)
            if published.tzinfo is None or published > fetched_at:
                continue
        except (TypeError, ValueError):
            continue
        key = sha256(url.encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        result.append(NewsItemInput("antara_rss", key, title, url, parsed.hostname or "",
                                    published.astimezone(timezone.utc), fetched_at, fetched_at))
    return result


def discover_antara_articles(ticker: str, client: httpx.Client,
                             fetched_at: datetime | None = None) -> list[NewsItemInput]:
    response = client.get(FEED_URL, timeout=35)
    response.raise_for_status()
    return parse_antara_feed(response.text, ticker, fetched_at or datetime.now(timezone.utc))
