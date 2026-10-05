import pytest

from app.adapters.broker_csv import parse_broker_csv


HEADER = (
    "ticker,trading_date,market,investor,broker,buy_shares,sell_shares,"
    "buy_value,sell_value,buy_freq,sell_freq,available_at"
)
GOOD = "BBRI,2026-10-02,RG,all,YP,100,0,100000,0,1,0,2026-10-02T19:00:00+07:00"


def test_explicit_share_columns_import():
    rows = parse_broker_csv(HEADER + "\n" + GOOD + "\n")
    assert len(rows) == 1
    assert rows[0].buy_shares == 100


def test_ambiguous_lot_header_is_rejected():
    with pytest.raises(ValueError, match="buy_shares"):
        parse_broker_csv(HEADER.replace("buy_shares", "buy_lots") + "\n" + GOOD + "\n")


def test_malformed_number_reports_line():
    with pytest.raises(ValueError, match="line 2"):
        parse_broker_csv(HEADER + "\n" + GOOD.replace(",100,0,", ",unknown,0,") + "\n")


def test_duplicate_broker_day_is_rejected():
    with pytest.raises(ValueError, match="duplicate broker observations"):
        parse_broker_csv(HEADER + "\n" + GOOD + "\n" + GOOD + "\n")
