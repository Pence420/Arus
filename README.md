# Arus / BandarAI

BandarAI is a local-first Indonesian equity research prototype. It now has a sourced stock page, a FastAPI backend, PostgreSQL schema, real delayed-price ingestion (opt-in personal use), real publisher-headline discovery, and strict broker CSV import. It does not rank BPJS/BSJP candidates, execute trades, or claim that broker codes identify a "bandar".

## Run locally

Requirements: Python 3.12+, `uv`, Node.js 20+, npm, and PostgreSQL 16. The included `compose.yaml` starts **only** the database; API and frontend bind to localhost.

```bash
docker compose up -d db
cd backend
UV_CACHE_DIR=/private/tmp/bandarai-uv-cache uv sync --locked --extra dev
DATABASE_URL=postgresql+psycopg://bandarai:bandarai@localhost:5432/bandarai uv run --locked alembic upgrade head
DATABASE_URL=postgresql+psycopg://bandarai:bandarai@localhost:5432/bandarai ENABLE_PERSONAL_YAHOO=1 ENABLE_LOCAL_IMPORT=1 uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:3000/stocks/BBRI`. If PostgreSQL is already installed locally, use its own `DATABASE_URL` instead of Docker; for a local socket database owned by your macOS user, `postgresql+psycopg:///bandarai` works. Create the database first.

The page starts empty on purpose. Fetch actual BBRI observations while the API is running:

```bash
curl -X POST http://127.0.0.1:8000/api/stocks/BBRI/refresh-price
curl -X POST http://127.0.0.1:8000/api/stocks/BBRI/refresh-news
```

The price adapter uses Yahoo `.JK` chart data only when `ENABLE_PERSONAL_YAHOO=1`, for a personal/local instance. Yahoo data can be delayed and its terms restrict redistribution. Do not host or redistribute it publicly without rights. The API suppresses Yahoo rows for non-local clients. ANTARA's official Bursa RSS supplies actual article titles and publisher links when the ticker or a verified company alias appears in the title; a feed without a match correctly shows no related articles. GDELT discovery is optional with `ENABLE_GDELT=1`, but can return HTTP 429. ANTARA `pubDate` is shown as publication time; GDELT `seendate` is shown as aggregator detection time, not misrepresented as publication time. The app never invents article-body analysis. See [ANTARA RSS](https://www.antaranews.com/rss//), [Yahoo delay notice](https://help.yahoo.com/kb/SLN2352.html), and [GDELT DOC API](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/).

For broker data, upload a normalized CSV legally obtained from your provider:

```bash
curl -F 'file=@broker-daily.csv' http://127.0.0.1:8000/api/import/broker-csv
```

`available_at` is asserted by the importer, not independently verified; verify it from the provider before historical testing. The API hides rows whose provider availability **or actual ingest time** is after the selected `decision_at`. Re-imports keep separate broker versions, so later corrections cannot rewrite earlier decision snapshots. Price fetches are versioned by fetch time for the same reason.

Run backend tests with `cd backend && uv run --locked --extra dev python -m pytest tests -q`, and frontend type/build check with `cd frontend && npm run build`. A running PostgreSQL is needed to exercise the migration; parser and API unit tests use an isolated SQLite test database.

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
