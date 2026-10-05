"""Optional test against a migrated disposable PostgreSQL database."""

import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.adapters.gdelt_news import NewsItemInput
from app.adapters.yahoo_price import PriceBarInput
from app.domain.broker_flow import BrokerRow
from app.services.ingest import store_articles, store_broker_rows, store_price_bars
from app.services.research import stock_research


def test_postgres_source_roundtrip():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not configured")
    engine = create_engine(url)
    now = datetime.now(timezone.utc)
    decision_after = now + timedelta(minutes=1)
    earlier = datetime(2026, 10, 2, 10, tzinfo=timezone.utc)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with Session(bind=connection) as session:
                price = PriceBarInput("BBRI", "yahoo", earlier, now, Decimal(4000),
                                      Decimal(4050), Decimal(3990), Decimal(4020), 100000)
                store_price_bars(session, [price])
                store_price_bars(session, [price])
                article = NewsItemInput("test_news", "test-bbri-2026-10-05",
                    "BBRI reports results", "https://example.org/bbri", "example.org", earlier, now, now)
                store_articles(session, [article], "BBRI", "ticker in title")
                broker = BrokerRow("BBRI", date(2026, 10, 2), "RG", "all", "YP",
                    100, 0, 400000, 0, 1, 0, now)
                store_broker_rows(session, [broker], "test.csv")
                session.flush()
                before = stock_research(session, "BBRI", earlier, True)
                assert before["price"]["bar"] is None
                assert before["broker_flow"]["rows"] == []
                after = stock_research(session, "BBRI", decision_after, True)
                assert after["price"]["bar"]["close"] == "4020.0000"
                assert len(after["news"]["items"]) == 1
                assert after["broker_flow"]["rows"][0]["net_value_idr"] == 400000
        finally:
            transaction.rollback()
