from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.domain.availability import positive_day_persistence, visible_rows
from app.domain.broker_flow import BrokerRow


BASE = dict(
    ticker="BBRI",
    trading_date=date(2026, 10, 2),
    market="RG",
    investor="all",
    broker="YP",
    buy_shares=100,
    sell_shares=0,
    buy_value=100_000,
    sell_value=0,
    buy_freq=1,
    sell_freq=0,
    available_at=datetime(2026, 10, 2, 12, tzinfo=timezone.utc),
)


def test_today_eod_is_invisible_to_afternoon_decision():
    row = BrokerRow(**BASE)
    afternoon = datetime(2026, 10, 2, 8, tzinfo=timezone.utc)
    assert visible_rows([row], afternoon) == []
    assert visible_rows([row], row.available_at) == [row]


def test_missing_day_does_not_count_as_zero():
    row = BrokerRow(**BASE)
    assert positive_day_persistence(
        [row], [date(2026, 10, 1), date(2026, 10, 2)], row.available_at
    ) is None
    assert positive_day_persistence([row], [date(2026, 10, 2)], row.available_at) == Decimal(1)


def test_persistence_cannot_use_unpublished_row():
    row = BrokerRow(**BASE)
    afternoon = datetime(2026, 10, 2, 8, tzinfo=timezone.utc)
    assert positive_day_persistence([row], [row.trading_date], afternoon) is None


def test_duplicate_daily_row_is_rejected():
    row = BrokerRow(**BASE)
    with pytest.raises(ValueError, match="one broker row"):
        positive_day_persistence([row, row], [row.trading_date], row.available_at)
