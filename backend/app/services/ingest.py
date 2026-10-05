"""Transactional, idempotent storage for source data."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.adapters.gdelt_news import NewsItemInput
from app.adapters.yahoo_price import PriceBarInput
from app.domain.broker_flow import BrokerRow
from app.models import BrokerFlowRow, ImportBatch, NewsItem, NewsTickerLink, PriceBar, ProviderRun, Stock


def ensure_stock(session: Session, ticker: str, name: str | None = None) -> None:
    statement = _insert_for(session, Stock).values(ticker=ticker, name=name or ticker)
    session.execute(statement.on_conflict_do_nothing(index_elements=["ticker"]))


def _insert_for(session: Session, model):
    dialect = session.get_bind().dialect.name
    if dialect == "postgresql":
        return pg_insert(model)
    if dialect == "sqlite":
        return sqlite_insert(model)
    raise ValueError(f"unsupported database dialect: {dialect}")


def store_price_bars(session: Session, rows: list[PriceBarInput]) -> int:
    for row in rows:
        ensure_stock(session, row.ticker)
        values = dict(ticker=row.ticker, provider=row.provider, observed_at=row.observed_at,
                      available_at=row.available_at, open=row.open, high=row.high,
                      low=row.low, close=row.close, volume=row.volume)
        statement = _insert_for(session, PriceBar).values(**values)
        session.execute(statement.on_conflict_do_nothing(
            index_elements=["ticker", "provider", "observed_at", "available_at"]))
    return len(rows)


def store_articles(session: Session, items: list[NewsItemInput], ticker: str, match_reason: str) -> int:
    ensure_stock(session, ticker)
    for item in items:
        statement = _insert_for(session, NewsItem).values(**item.__dict__)
        session.execute(statement.on_conflict_do_nothing(index_elements=["provider", "source_key"]))
        article_id = session.scalar(select(NewsItem.id).where(NewsItem.provider == item.provider,
                                                               NewsItem.source_key == item.source_key))
        confidence = "corroborated" if ticker in item.title.upper().split() or item.provider == "antara_rss" else "uncertain"
        link = _insert_for(session, NewsTickerLink).values(news_id=article_id, ticker=ticker,
            match_reason=match_reason, confidence=confidence)
        session.execute(link.on_conflict_do_nothing(index_elements=["news_id", "ticker"]))
    return len(items)


def store_broker_rows(session: Session, rows: list[BrokerRow], filename: str) -> int:
    batch = ImportBatch(filename=filename[:255], row_count=len(rows))
    session.add(batch)
    session.flush()
    for row in rows:
        ensure_stock(session, row.ticker)
        values = dict(batch_id=batch.id, buy_shares=row.buy_shares, sell_shares=row.sell_shares,
                      buy_value=row.buy_value, sell_value=row.sell_value, buy_freq=row.buy_freq,
                      sell_freq=row.sell_freq, available_at=row.available_at)
        statement = _insert_for(session, BrokerFlowRow).values(
            ticker=row.ticker, trading_date=row.trading_date, market=row.market,
            investor=row.investor, broker=row.broker, provider="csv", **values)
        session.execute(statement.on_conflict_do_nothing(
            index_elements=["ticker", "trading_date", "market", "investor", "broker", "provider", "batch_id"]))
    session.flush()
    return len(rows)


def record_run(session: Session, provider: str, ticker: str, started_at: datetime,
               status: str, error: str | None = None) -> None:
    session.add(ProviderRun(provider=provider, ticker=ticker, status=status,
                            started_at=started_at, finished_at=datetime.now(timezone.utc),
                            error=error[:500] if error else None))
    session.commit()
