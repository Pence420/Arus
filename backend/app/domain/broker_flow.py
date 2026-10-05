"""Normalized broker observations for one ticker and trading session."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class BrokerRow:
    ticker: str
    trading_date: date
    market: str
    investor: str
    broker: str
    buy_shares: int
    sell_shares: int
    buy_value: int
    sell_value: int
    buy_freq: int
    sell_freq: int
    available_at: datetime

    def __post_init__(self) -> None:
        if self.market not in {"RG", "NG"} or self.investor not in {"all", "f", "d"}:
            raise ValueError("unsupported market or investor filter")
        if not self.ticker.isalpha() or not self.broker.isalpha():
            raise ValueError("ticker and broker must be alphabetic codes")
        for field in (
            "buy_shares", "sell_shares", "buy_value", "sell_value", "buy_freq", "sell_freq"
        ):
            value = getattr(self, field)
            if type(value) is not int or value < 0:
                raise ValueError(f"{field} must be a nonnegative integer")
        if self.available_at.tzinfo is None or self.available_at.utcoffset() is None:
            raise ValueError("available_at must include a timezone")


def net_shares(row: BrokerRow) -> int:
    return row.buy_shares - row.sell_shares


def net_value(row: BrokerRow) -> int:
    return row.buy_value - row.sell_value


def buy_vwap(row: BrokerRow) -> Decimal | None:
    return Decimal(row.buy_value) / Decimal(row.buy_shares) if row.buy_shares else None


def sell_vwap(row: BrokerRow) -> Decimal | None:
    return Decimal(row.sell_value) / Decimal(row.sell_shares) if row.sell_shares else None


def positive_net_concentration(rows: Sequence[BrokerRow], k: int) -> Decimal | None:
    """Share of positive net value attributable to the largest k net buyers.

    Input must be a complete, two-sided all-investor set from one market session.
    Balance checks catch many incomplete inputs, though a balanced subset still
    needs provider coverage verification before this metric is displayed.
    """
    if k < 1:
        raise ValueError("k must be positive")
    if not rows:
        return None
    scope = {(r.ticker, r.trading_date, r.market, r.investor) for r in rows}
    if len(scope) != 1:
        raise ValueError("rows must share ticker, date, market and investor scope")
    if len({row.broker for row in rows}) != len(rows):
        raise ValueError("duplicate broker rows in one session")
    if (
        rows[0].investor != "all"
        or sum(net_shares(r) for r in rows) != 0
        or sum(net_value(r) for r in rows) != 0
    ):
        raise ValueError("complete all-investor two-sided rows are required")
    positives = sorted((max(net_value(r), 0) for r in rows), reverse=True)
    total = sum(positives)
    return Decimal(sum(positives[:k])) / Decimal(total) if total else None
