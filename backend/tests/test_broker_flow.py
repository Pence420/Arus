from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.domain.broker_flow import (
    BrokerRow,
    buy_vwap,
    net_shares,
    net_value,
    positive_net_concentration,
    sell_vwap,
)


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


def test_row_rejects_negative_and_ambiguous_market():
    with pytest.raises(ValueError):
        BrokerRow(**{**BASE, "buy_shares": -1})
    with pytest.raises(ValueError):
        BrokerRow(**{**BASE, "market": "ALL"})
    with pytest.raises(ValueError):
        BrokerRow(**{**BASE, "available_at": datetime(2026, 10, 2, 19)})


def test_net_signs_can_disagree_and_zero_side_has_no_vwap():
    row = BrokerRow(
        **{
            **BASE,
            "buy_shares": 200,
            "buy_value": 20_000,
            "sell_shares": 190,
            "sell_value": 21_300,
        }
    )
    assert net_shares(row) == 10
    assert net_value(row) == -1_300
    assert buy_vwap(row) == Decimal(100)
    assert sell_vwap(row) == Decimal(21_300) / Decimal(190)
    assert sell_vwap(BrokerRow(**BASE)) is None


def test_concentration_uses_positive_nets_not_signed_total():
    rows = [
        BrokerRow(
            **{
                **BASE,
                "broker": code,
                "buy_shares": buy,
                "sell_shares": sell,
                "buy_value": buy,
                "sell_value": sell,
            }
        )
        for code, buy, sell in [
            ("AA", 40, 0),
            ("BB", 30, 0),
            ("CC", 20, 0),
            ("DD", 10, 0),
            ("EE", 0, 100),
        ]
    ]
    assert positive_net_concentration(rows, 2) == Decimal("0.7")


def test_concentration_rejects_mixed_tickers():
    first = BrokerRow(**BASE)
    second = BrokerRow(**{**BASE, "ticker": "BBCA", "broker": "AK"})
    with pytest.raises(ValueError, match="share ticker"):
        positive_net_concentration([first, second], 2)
