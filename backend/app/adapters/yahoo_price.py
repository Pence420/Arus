"""Opt-in personal-use adapter for delayed Yahoo Finance .JK chart data."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import re

import httpx


TICKER = re.compile(r"^[A-Z]{4,5}$")


@dataclass(frozen=True)
class PriceBarInput:
    ticker: str
    provider: str
    observed_at: datetime
    available_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


def parse_chart_response(ticker: str, data: dict, fetched_at: datetime) -> list[PriceBarInput]:
    if not TICKER.fullmatch(ticker) or fetched_at.tzinfo is None:
        raise ValueError("invalid ticker or naive fetch time")
    chart = data.get("chart") or {}
    if chart.get("error"):
        raise ValueError("price provider returned an error")
    results = chart.get("result") or []
    if len(results) != 1:
        raise ValueError("price provider returned no unique chart")
    result = results[0]
    quotes = ((result.get("indicators") or {}).get("quote") or [])
    if len(quotes) != 1:
        raise ValueError("price provider quote data missing")
    quote = quotes[0]
    stamps = result.get("timestamp") or []
    fields = ("open", "high", "low", "close", "volume")
    if any(len(quote.get(field) or []) != len(stamps) for field in fields):
        raise ValueError("price provider arrays have different lengths")
    rows = []
    for i, stamp in enumerate(stamps):
        values = [quote[field][i] for field in fields]
        if any(value is None for value in values):
            continue
        opening, high, low, close = [Decimal(str(v)) for v in values[:4]]
        volume = values[4]
        if (not isinstance(volume, int) or volume < 0 or low <= 0 or
            not low <= opening <= high or not low <= close <= high):
            raise ValueError("invalid OHLCV from price provider")
        observed = datetime.fromtimestamp(stamp, tz=timezone.utc)
        if observed > fetched_at:
            raise ValueError("quote timestamp is after fetch time")
        rows.append(PriceBarInput(ticker, "yahoo", observed, fetched_at, opening, high, low, close, volume))
    return rows


def fetch_price_bars(ticker: str, client: httpx.Client, fetched_at: datetime | None = None) -> list[PriceBarInput]:
    if not TICKER.fullmatch(ticker):
        raise ValueError("invalid IDX ticker")
    response = client.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.JK",
                          params={"range": "1mo", "interval": "1d"}, timeout=15)
    response.raise_for_status()
    return parse_chart_response(ticker, response.json(), fetched_at or datetime.now(timezone.utc))
