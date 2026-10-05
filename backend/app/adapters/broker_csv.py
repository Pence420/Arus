"""Strict import boundary for already-normalized daily broker-summary CSV."""

import csv
from datetime import date, datetime
from io import StringIO

from app.domain.broker_flow import BrokerRow


FIELDS = (
    "ticker",
    "trading_date",
    "market",
    "investor",
    "broker",
    "buy_shares",
    "sell_shares",
    "buy_value",
    "sell_value",
    "buy_freq",
    "sell_freq",
    "available_at",
)
NUMERIC = (
    "buy_shares",
    "sell_shares",
    "buy_value",
    "sell_value",
    "buy_freq",
    "sell_freq",
)


def parse_broker_csv(text: str) -> list[BrokerRow]:
    """Parse a per-day, per-broker CSV whose volumes are explicitly shares.

    ``available_at`` is source-provided provenance. Importers must verify it
    before using these rows for historical decision-time evaluation.
    """
    reader = csv.DictReader(StringIO(text))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise ValueError(
            "CSV header must contain exact buy_shares/sell_shares and IDR fields"
        )
    result: list[BrokerRow] = []
    for line_number, raw in enumerate(reader, start=2):
        try:
            data = {key: raw[key].strip() for key in FIELDS}
            for key in NUMERIC:
                data[key] = int(data[key])
            data["trading_date"] = date.fromisoformat(data["trading_date"])
            data["available_at"] = datetime.fromisoformat(data["available_at"])
            result.append(BrokerRow(**data))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
    if not result:
        raise ValueError("CSV contains no broker observations")
    keys = [
        (r.ticker, r.trading_date, r.market, r.investor, r.broker) for r in result
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("CSV contains duplicate broker observations")
    return result
