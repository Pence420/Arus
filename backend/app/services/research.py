"""Assemble only evidence that existed by the stated decision time."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import BrokerFlowRow, NewsItem, NewsTickerLink, PriceBar


def _iso(value):
    return value.isoformat() if value is not None else None


def stock_research(session: Session, ticker: str, decision_at: datetime, yahoo_enabled: bool) -> dict:
    if decision_at.tzinfo is None or decision_at.utcoffset() is None:
        raise ValueError("decision_at must include timezone")
    price_query = select(PriceBar).where(PriceBar.ticker == ticker,
        PriceBar.available_at <= decision_at, PriceBar.ingested_at <= decision_at)
    known_price_query = select(PriceBar.id).where(PriceBar.ticker == ticker)
    if not yahoo_enabled:
        price_query = price_query.where(PriceBar.provider != "yahoo")
        known_price_query = known_price_query.where(PriceBar.provider != "yahoo")
    price = session.scalar(price_query.order_by(PriceBar.observed_at.desc(),
                                                PriceBar.available_at.desc()).limit(1))
    future_price = session.scalar(known_price_query.limit(1))
    news = session.execute(select(NewsItem, NewsTickerLink).join(NewsTickerLink,
        NewsTickerLink.news_id == NewsItem.id).where(NewsTickerLink.ticker == ticker,
        NewsItem.available_at <= decision_at, NewsItem.ingested_at <= decision_at,
        NewsTickerLink.ingested_at <= decision_at).order_by(
            func.coalesce(NewsItem.published_at, NewsItem.source_seen_at).desc()).limit(20)).all()
    future_news = session.scalar(select(NewsTickerLink.id).where(NewsTickerLink.ticker == ticker).limit(1))
    broker_versions = session.scalars(select(BrokerFlowRow).where(BrokerFlowRow.ticker == ticker,
        BrokerFlowRow.available_at <= decision_at, BrokerFlowRow.ingested_at <= decision_at,
        BrokerFlowRow.market == "RG",
        BrokerFlowRow.investor == "all").order_by(BrokerFlowRow.trading_date.desc(),
        BrokerFlowRow.ingested_at.desc(), BrokerFlowRow.batch_id.desc())).all()
    brokers = []
    seen_brokers = set()
    for row in broker_versions:
        key = (row.trading_date, row.market, row.investor, row.broker)
        if key not in seen_brokers:
            seen_brokers.add(key)
            brokers.append(row)
        if len(brokers) >= 100:
            break
    future_broker = session.scalar(select(BrokerFlowRow.id).where(BrokerFlowRow.ticker == ticker).limit(1))
    price_status = "available" if price else ("unavailable_at_decision" if future_price else
                   "no_data" if yahoo_enabled else "not_configured")
    news_status = "available" if news else "unavailable_at_decision" if future_news else "no_data"
    broker_status = "available" if brokers else "unavailable_at_decision" if future_broker else "no_data"
    return {
        "ticker": ticker, "decision_at": _iso(decision_at),
        "price": {"status": price_status, "bar": None if price is None else {
            "provider": price.provider, "observed_at": _iso(price.observed_at),
            "available_at": _iso(price.available_at), "ingested_at": _iso(price.ingested_at),
            "open": str(price.open), "high": str(price.high), "low": str(price.low),
            "close": str(price.close), "volume_shares": price.volume,
            "source_url": f"https://finance.yahoo.com/quote/{ticker}.JK/" if price.provider == "yahoo" else None}},
        "news": {"status": news_status, "items": [{
            "title": article.title, "url": article.url, "domain": article.domain,
            "published_at": _iso(article.published_at), "source_seen_at": _iso(article.source_seen_at),
            "available_at": _iso(article.available_at),
            "provider": article.provider, "confidence": link.confidence,
            "match_reason": link.match_reason,
        } for article, link in news]},
        "broker_flow": {"status": broker_status, "rows": [{
            "trading_date": _iso(row.trading_date), "broker": row.broker,
            "market": row.market, "provider": row.provider,
            "buy_shares": row.buy_shares, "sell_shares": row.sell_shares,
            "net_shares": row.buy_shares - row.sell_shares,
            "buy_value_idr": row.buy_value, "sell_value_idr": row.sell_value,
            "net_value_idr": row.buy_value - row.sell_value,
            "available_at": _iso(row.available_at), "ingested_at": _iso(row.ingested_at),
            "source_ref": f"import-batch:{row.batch_id}",
        } for row in brokers]},
    }
