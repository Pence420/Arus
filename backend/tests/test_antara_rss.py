from datetime import datetime, timezone

import pytest

from app.adapters.antara_rss import parse_antara_feed


NOW = datetime(2026, 10, 5, 12, tzinfo=timezone.utc)
FEED = """<rss><channel>
<item><title>BBRI catat pertumbuhan kredit</title><link>https://www.antaranews.com/berita/123/bbri</link><pubDate>Mon, 05 Oct 2026 09:00:00 +0700</pubDate></item>
<item><title>Bank Rakyat Indonesia tambah layanan</title><link>https://www.antaranews.com/berita/124/layanan</link><pubDate>Mon, 05 Oct 2026 09:10:00 +0700</pubDate></item>
<item><title>Bukan BBRIX</title><link>https://www.antaranews.com/berita/125/lain</link><pubDate>Mon, 05 Oct 2026 09:20:00 +0700</pubDate></item>
<item><title>BBRI palsu</title><link>https://evil.test/berita/1</link><pubDate>Mon, 05 Oct 2026 09:30:00 +0700</pubDate></item>
</channel></rss>"""


def test_feed_matches_exact_ticker_and_known_alias_only():
    rows = parse_antara_feed(FEED, "BBRI", NOW)
    assert len(rows) == 2
    assert all(row.provider == "antara_rss" for row in rows)
    assert rows[0].published_at < rows[0].available_at


def test_invalid_feed_rejected():
    with pytest.raises(ValueError):
        parse_antara_feed("<rss>", "BBRI", NOW)
