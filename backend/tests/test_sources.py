from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.adapters.gdelt_news import parse_gdelt_articles
from app.adapters.yahoo_price import PriceBarInput, parse_chart_response
from app.models import Base, NewsItem, PriceBar
from app.services.ingest import store_articles, store_price_bars


NOW = datetime(2026, 10, 2, 10, tzinfo=timezone.utc)


def test_price_parser_preserves_provider_quote_time():
    payload = {"chart": {"result": [{"timestamp": [1790902800],
        "indicators": {"quote": [{"open": [4000], "high": [4050], "low": [3990],
                                   "close": [4020], "volume": [100000]}]}}], "error": None}}
    rows = parse_chart_response("BBRI", payload, NOW)
    assert rows[0].observed_at.timestamp() == 1790902800
    assert rows[0].available_at == NOW
    assert rows[0].volume == 100000


def test_price_parser_rejects_bad_shapes():
    with pytest.raises(ValueError):
        parse_chart_response("BBRI", {"chart": {"result": []}}, NOW)
    with pytest.raises(ValueError):
        parse_chart_response("BBRI.JK", {}, NOW)


def test_news_parser_keeps_real_link_and_drops_unsafe_url():
    valid = {"title": "BBRI publishes results", "url": "https://example.org/markets/bbri",
             "seendate": "20261002T020000Z"}
    rows = parse_gdelt_articles({"articles": [valid, valid, {"title": "Rumor", "url": "javascript:alert(1)"}]}, NOW)
    assert len(rows) == 1
    assert rows[0].url == valid["url"]
    assert rows[0].published_at is None
    assert rows[0].source_seen_at < rows[0].available_at


def test_repeat_ingest_does_not_duplicate_sources():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    price = PriceBarInput("BBRI", "yahoo", NOW, NOW, Decimal(1), Decimal(2), Decimal(1), Decimal(2), 100)
    article = parse_gdelt_articles({"articles": [{"title": "BBRI publishes results",
        "url": "https://example.org/markets/bbri", "seendate": "20261002T020000Z"}]}, NOW)[0]
    with Session(engine) as session:
        store_price_bars(session, [price])
        store_price_bars(session, [price])
        newer = PriceBarInput("BBRI", "yahoo", NOW, NOW + timedelta(minutes=1),
                              Decimal(1), Decimal(2), Decimal(1), Decimal(2), 100)
        store_price_bars(session, [newer])
        store_articles(session, [article], "BBRI", "ticker in headline")
        store_articles(session, [article], "BBRI", "ticker in headline")
        session.commit()
        assert session.query(PriceBar).count() == 2
        assert session.query(NewsItem).count() == 1
