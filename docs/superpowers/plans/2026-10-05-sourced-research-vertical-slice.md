# Sourced Research Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver one locally usable stock research page backed by PostgreSQL, genuine price/news observations, and the existing broker-summary CSV importer, with source and availability timestamps visible.

**Architecture:** FastAPI owns ingestion and read APIs; PostgreSQL stores normalized observations and provider-run outcomes; a small Next.js page renders only stored, sourced data. Yahoo `.JK` is an opt-in local/personal-use price adapter, never enabled for public redistribution. GDELT discovers article metadata and publisher links; the app does not infer article-body claims from headlines.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, psycopg 3, Alembic, httpx, PostgreSQL 16, Next.js, TypeScript, pytest.

**Spec:** `docs/superpowers/specs/2026-10-05-bandarai-mvp-design.md`; prior core: `docs/superpowers/plans/2026-10-05-broker-flow-core.md`.

**Implementation status (2026-10-05):** Vertical slice implemented. The news source order changed after a live GDELT request returned HTTP 429: ANTARA's official Bursa RSS is primary, with GDELT optional. `seendate` and publisher `pubDate` are stored separately. Price fetches and broker imports are versioned; research requires actual ingest time no later than the decision. A local PostgreSQL 16 migration and round-trip integration test passed; the Next.js production build and npm audit passed. Candidate ranking, authentication and deployment remain outside this slice.

## Global Constraints

- Preserve original provider identifiers, source links, observed/published/available/ingested times and timezone offsets; store instants as `timestamptz`.
- No invented quotes, articles, broker rows, headlines, scores or buy/sell recommendations. Absent feeds are marked unavailable.
- A record influences a decision only if `available_at <= decision_at`; current EOD broker data cannot justify BPJS or BSJP decisions earlier that day.
- Yahoo data is local/personal-use only behind an explicit environment switch; a public deployment must not expose it without source rights.
- Broker summary remains per ticker/day/market/investor/broker. Preserve shares versus IDR, RG versus NG, and the existing strict parser.
- No order execution, backtest performance claim or opaque opportunity score in this slice.

## Review Focus

1. Provider timeout or malformed response: record failure and keep the previous valid rows; test the failure path in Task 2.
2. News mentioning a ticker as an ordinary word: require alias/company corroboration or mark match as uncertain; test in Task 3.
3. Duplicate ingest or a corrected provider item: upsert by stable provider key without multiplying rows; test in Tasks 2–4.
4. Morning `decision_at` with same-day EOD broker import: omit future evidence; test in Task 4.
5. No configured quote source or no broker import: return explicit unavailable states, not zero values; test in Task 4 and the UI in Task 5.

## File Map

- `backend/alembic/versions/0001_observations.py`: initial stock, price, article, broker, import-batch and provider-run schema.
- `backend/app/db.py`: pooled connection/session factory; `backend/app/models.py`: ORM model declarations matching the migration.
- `backend/app/adapters/yahoo_price.py`: opt-in `.JK` price-response parser and fetcher.
- `backend/app/adapters/gdelt_news.py`: GDELT DOC API discovery and strict article metadata parsing.
- `backend/app/services/ingest.py`: idempotent write transactions and provider-run bookkeeping.
- `backend/app/services/research.py`: decision-time sourced stock report and unavailable states.
- `backend/app/main.py`: FastAPI routes for health, ingest, and research.
- `frontend/app/stocks/[ticker]/page.tsx`: sourced stock report and data-gap presentation.
- `compose.yaml`, `.env.example`, `README.md`: reproducible local run, opt-in provider settings and source-rights warning.

---

### Task 1: PostgreSQL schema and local connection

**Files:** Create `backend/app/db.py`, `backend/app/models.py`, `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/0001_observations.py`, `compose.yaml`, `.env.example`; modify `backend/pyproject.toml`; test `backend/tests/test_schema.py`.

**Interfaces:** `get_session() -> Iterator[Session]`; tables `stocks`, `price_bars`, `news_items`, `news_ticker_links`, `broker_flow_rows`, `import_batches`, `provider_runs`.

- [ ] **Step 1: Write the failing schema integration test.** Run it only when `TEST_DATABASE_URL` is set; otherwise skip explicitly.

```python
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

def test_schema_rejects_duplicate_price_bar():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required")
    engine = create_engine(url)
    insert = text("""insert into price_bars
        (ticker, provider, observed_at, available_at, open, high, low, close, volume)
        values (:ticker, :provider, :observed_at, :available_at,
                :open, :high, :low, :close, :volume)""")
    params = dict(ticker="BBRI", provider="yahoo", observed_at="2026-10-02T09:00:00+07:00",
                  open=4000, high=4050, low=3990, close=4020, volume=100000,
                  available_at="2026-10-02T09:20:00+07:00")
    with engine.connect() as connection:
        outer = connection.begin()
        connection.execute(text("insert into stocks(ticker, name) values ('BBRI', 'Bank Rakyat Indonesia')"))
        connection.execute(insert, params)
        duplicate = connection.begin_nested()
        with pytest.raises(IntegrityError):
            connection.execute(insert, params)
        duplicate.rollback()
        outer.rollback()
```

- [ ] **Step 2: Run** `cd backend && uv run --extra dev python -m pytest tests/test_schema.py -q`; expect missing module or table failure with a configured test DB.
- [ ] **Step 3: Add migration and models.** Use `bigint generated by default as identity` IDs, `text` identifiers, `date` sessions, `timestamptz` instants, `numeric(18,4)` prices, `bigint` shares/IDR, nonnegative checks and unique source keys. Create indexes for `(ticker, observed_at desc)` prices, `(ticker, available_at desc)` broker rows, news-link foreign keys, and `(provider, source_key)` articles. Use a small SQLAlchemy pool and dispose it on shutdown.

```sql
create table price_bars (
  id bigint generated by default as identity primary key,
  ticker text not null references stocks(ticker),
  provider text not null,
  observed_at timestamptz not null,
  available_at timestamptz not null,
  ingested_at timestamptz not null default now(),
  open numeric(18,4) not null,
  high numeric(18,4) not null,
  low numeric(18,4) not null,
  close numeric(18,4) not null,
  volume bigint not null check (volume >= 0),
  unique (ticker, provider, observed_at),
  check (low <= high and open between low and high and close between low and high)
);
```

- [ ] **Step 4: Run** migration against disposable local PostgreSQL and run schema test plus existing tests; expect pass.
- [ ] **Step 5: Commit** with `feat: add sourced market observation schema`.

### Task 2: Genuine price adapter and idempotent ingestion

**Files:** Create `backend/app/adapters/yahoo_price.py`, `backend/app/services/ingest.py`; test `backend/tests/test_yahoo_price.py`, `backend/tests/test_ingest.py`; modify `backend/pyproject.toml`.

**Interfaces:** `fetch_price_bars(ticker: str, client: httpx.Client) -> list[PriceBarInput]`; `store_price_bars(session, rows) -> int`. Both require an explicit `ENABLE_PERSONAL_YAHOO=1` setting at the route/job boundary.

- [ ] **Step 1: Write tests with a recorded, reduced response fixture.** Assert `.JK` symbol validation, real response timestamps converted to aware datetimes, null-price rows omitted, zero/negative volume rejected, HTTP failure recorded as `provider_runs.status='failed'`, and a repeated ingest updates rather than duplicates the same `(ticker, provider, observed_at)` key.

```python
from datetime import datetime, timezone
from app.adapters.yahoo_price import parse_chart_response

def test_price_parser_keeps_actual_quote_time():
    fetched_at = datetime(2026, 10, 2, 3, tzinfo=timezone.utc)
    response = {"chart": {"result": [{"timestamp": [1790902800],
        "indicators": {"quote": [{"open": [4000], "high": [4050], "low": [3990],
                                   "close": [4020], "volume": [100000]}]}}], "error": None}}
    rows = parse_chart_response("BBRI", response, fetched_at=fetched_at)
    assert rows[0].ticker == "BBRI"
    assert rows[0].observed_at.timestamp() == response["chart"]["result"][0]["timestamp"][0]
    assert rows[0].available_at == fetched_at
```

- [ ] **Step 2: Run** those tests; expect import failure.
- [ ] **Step 3: Implement strict parsing and persistence.** Keep fetched/available time separate from provider quote time; an absent provider publication timestamp is not invented. Use `INSERT ... ON CONFLICT (...) DO UPDATE` within one transaction. Record provider run start/end/error without deleting last successful observations.
- [ ] **Step 4: Run** adapter, ingest, and existing tests; expect pass.
- [ ] **Step 5: Commit** with `feat: ingest timestamped personal-use market prices`.

### Task 3: Real article discovery, not headline-only claims

**Files:** Create `backend/app/adapters/gdelt_news.py`; modify `backend/app/services/ingest.py`; test `backend/tests/test_gdelt_news.py`, `backend/tests/test_news_ingest.py`.

**Interfaces:** `discover_articles(query: str, client: httpx.Client) -> list[NewsItemInput]`; `store_articles(session, items, ticker, match_reason) -> int`.

- [ ] **Step 1: Write failing tests.** Fixture should contain a valid URL, title, domain and source datetime plus a malformed/duplicate item. Require URL scheme `https`, valid aware publication time, and explicit match reason. An uncorroborated ordinary-word ticker match must be `uncertain`, not strong evidence.

```python
from datetime import datetime, timezone
from app.adapters.gdelt_news import parse_gdelt_articles

def test_news_requires_real_url_and_publication_time():
    fetched_at = datetime(2026, 10, 2, 3, tzinfo=timezone.utc)
    valid = {"title": "BBRI publishes results", "url": "https://example.org/markets/bbri",
             "domain": "example.org", "seendate": "20261002T020000Z"}
    articles = parse_gdelt_articles({"articles": [valid, {"title": "Rumor", "url": "javascript:alert(1)"}]}, fetched_at)
    assert len(articles) == 1
    assert articles[0].url == valid["url"]
    assert articles[0].published_at <= articles[0].available_at
```

- [ ] **Step 2: Run** news tests; expect import failure.
- [ ] **Step 3: Implement GDELT DOC `artlist` request and parser.** Store publisher URL and provider source key (canonical URL hash), `published_at`, `available_at` (not earlier than actual fetch), `ingested_at`, ticker link and match confidence/reason. Do not fetch or summarize full article bodies. Upsert duplicates atomically.
- [ ] **Step 4: Run** news and existing tests; expect pass.
- [ ] **Step 5: Commit** with `feat: discover and store sourced Indonesian market news`.

### Task 4: Research API and broker CSV import

**Files:** Create `backend/app/services/research.py`, `backend/app/main.py`; test `backend/tests/test_research_api.py`; modify `backend/app/services/ingest.py`.

**Interfaces:** `GET /api/stocks/{ticker}/research?decision_at=<ISO8601>` returns `price`, `news`, `broker_flow`, `data_status`, with source and timestamps; `POST /api/import/broker-csv` accepts a strictly normalized CSV file in local mode, never arbitrary filesystem paths.

- [ ] **Step 1: Write failing API tests** for an empty DB, a sourced BBRI row, a future-available broker row and an invalid CSV. Use FastAPI dependency override to supply the disposable test session.

```python
def test_morning_report_excludes_same_day_eod_broker(client, seeded_broker_row):
    response = client.get("/api/stocks/BBRI/research",
                          params={"decision_at": "2026-10-02T09:00:00+07:00"})
    assert response.status_code == 200
    assert response.json()["broker_flow"]["status"] == "unavailable_at_decision"
    assert response.json()["broker_flow"]["rows"] == []
```

- [ ] **Step 2: Run** API tests; expect missing endpoint failure.
- [ ] **Step 3: Implement endpoints.** Validate ticker and aware `decision_at`; query each source with `available_at <= decision_at`; return explicit `not_configured`, `no_data`, `stale` or `available` states as applicable. Enforce upload size, CSV parser errors, one atomic import batch and a local-only import setting. Do not show a concentration figure until coverage is verified.
- [ ] **Step 4: Run** API and existing tests; expect pass.
- [ ] **Step 5: Commit** with `feat: expose time-safe sourced stock research API`.

### Task 5: End-to-end local stock page

**Files:** Create `frontend/package.json`, `frontend/app/layout.tsx`, `frontend/app/stocks/[ticker]/page.tsx`, `frontend/app/globals.css`, `frontend/tsconfig.json`; modify `compose.yaml`, `.env.example`, `README.md`; test `frontend` component tests and a local API/UI smoke check.

**Interfaces:** The page consumes Task 4's JSON contract; URL ticker is validated server-side; source links open the original publishers.

- [ ] **Step 1: Write component tests** using a fixed API fixture for a populated result and empty result. Require provider, observed/available time and source link on populated cards; require a clear unavailable label and no fabricated zero on empty cards.

```tsx
expect(screen.getByText(/Data broksum belum tersedia/i)).toBeInTheDocument();
expect(screen.queryByText(/0 broker/i)).not.toBeInTheDocument();
```

- [ ] **Step 2: Run** component tests; expect missing component failure.
- [ ] **Step 3: Implement the page and local Compose wiring.** Show price as delayed/observational, news as linked headlines, broker rows as descriptive flow, a selectable decision time and an overall source-status strip. Local dev instructions include migration, optional Yahoo switch, GDELT refresh and broker CSV import; no hidden demo data ships as a real feed.
- [ ] **Step 4: Run** Python tests, frontend tests/build, then manually load `/stocks/BBRI` with and without configured sources; verify links, timestamps and empty states.
- [ ] **Step 5: Commit** with `feat: add sourced stock research page` and push `main` only after reviewing staged diff and remote destination.

## Out of Scope for This Plan

Authentication, saved watchlists, candidate ranking, Index Alpha integration, AI thesis generation and historical performance evaluation remain separate milestones. This slice intentionally ships a truthful research page first; BPJS/BSJP candidates consume its time-safe evidence in the next plan.
