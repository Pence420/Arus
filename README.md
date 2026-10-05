# Arus / BandarAI

BandarAI is an Indonesian equity research project. The first implemented milestone is a Python core for checking broker-summary arithmetic and data availability. The frontend, database, news ingestion, and trading research screens are not implemented yet.

## Broker-flow core

The module in `backend/app/domain` calculates net shares, net IDR value, buy/sell volume-weighted average price, positive-net-buyer concentration, and positive-day persistence. It keeps regular (`RG`) and negotiated (`NG`) market records separate. A decision-time filter excludes observations that were not yet available.

The CSV importer accepts normalized daily records with this exact header:

```text
ticker,trading_date,market,investor,broker,buy_shares,sell_shares,buy_value,sell_value,buy_freq,sell_freq,available_at
```

Volumes are **shares**, transaction values are **IDR**, and `available_at` is an ISO 8601 timestamp with a timezone. Broker summary exports expressed in lots must be converted explicitly before import (1 regular-market lot = 100 shares). A multi-day aggregate must not be labeled as a daily row. The importer treats `available_at` as supplied provenance; verify it against the provider before using historical data in backtests.

Run the tests with Python 3.12 or newer:

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests -q
```

The [MVP design](docs/superpowers/specs/2026-10-05-bandarai-mvp-design.md), [broker calculation research](docs/research/2026-10-05-broker-summary-calculation-notes.md), and [BPJS/BSJP trading research](docs/research/2026-10-05-indonesian-short-horizon-trading.md) explain the source constraints and what these metrics do and do not mean. These calculations are descriptive; their predictive value has not been established.
