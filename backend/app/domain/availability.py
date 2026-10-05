"""Decision-time filtering and broker-flow continuity metrics."""

from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal

from app.domain.broker_flow import BrokerRow, net_value


def visible_rows(rows: Sequence[BrokerRow], decision_at: datetime) -> list[BrokerRow]:
    """Return only observations that were available at the decision time."""
    if decision_at.tzinfo is None or decision_at.utcoffset() is None:
        raise ValueError("decision_at must include a timezone")
    return [row for row in rows if row.available_at <= decision_at]


def positive_day_persistence(
    rows: Sequence[BrokerRow], expected_dates: Sequence[date], decision_at: datetime
) -> Decimal | None:
    """Fraction of observed trading days with positive net value for one broker.

    Return None if any expected date is missing; a missing day is not zero flow.
    Observations unavailable at ``decision_at`` cannot enter the calculation.
    """
    if not expected_dates or len(set(expected_dates)) != len(expected_dates):
        raise ValueError("expected trading dates must be nonempty and unique")
    eligible = visible_rows(rows, decision_at)
    if not eligible:
        return None
    scope = {(r.ticker, r.market, r.investor, r.broker) for r in eligible}
    if len(scope) != 1 or len({r.trading_date for r in eligible}) != len(eligible):
        raise ValueError("one broker row per date in one scope is required")
    by_date = {r.trading_date: r for r in eligible}
    if set(by_date) != set(expected_dates):
        return None
    return Decimal(sum(net_value(by_date[d]) > 0 for d in expected_dates)) / Decimal(
        len(expected_dates)
    )
