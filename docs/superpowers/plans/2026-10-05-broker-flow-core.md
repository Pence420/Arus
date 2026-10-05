# Broker Flow Calculation Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested Python calculation core that turns per-ticker, per-day broker records into auditable flow metrics without mixing units or using future data.

**Architecture:** Keep provider parsing at the boundary and calculations in pure functions. Each normalized row retains its ticker, session date, market segment, broker code, and availability time. The research API and UI will consume these functions in a later plan.

**Tech Stack:** Python 3.12, standard library dataclasses/Decimal/csv, pytest.

**Spec:** `docs/superpowers/specs/2026-10-05-bandarai-mvp-design.md`; calculation reference: `docs/research/2026-10-05-broker-summary-calculation-notes.md`.

**Execution status:** Implemented and verified on 2026-10-05 with 12 passing tests under Python 3.12. The four planned task commits are combined into one reviewed milestone commit. The persistence function additionally requires `decision_at` so callers cannot calculate from unpublished rows.

## Global Constraints

- A broker record is per ticker, per trading day, per segment, per broker, and per investor filter.
- Index Alpha volumes are shares, values are IDR, and multi-day responses are aggregated per broker; do not infer daily persistence from one aggregated response.
- Regular market `RG` and negotiated market `NG` remain separate; no `ALL` record enters the normalized store.
- An observation can influence a decision only when `available_at <= decision_at`.
- VWAP describes executed gross buys/sells in the record, not investor cost basis.
- Indicator thresholds and composite scores are outside this plan until historical validation.

## Review Focus

1. A CSV volume column measured in lots must require explicit conversion; tests in Task 4 reject ambiguous units.
2. Zero buy/sell shares must produce null VWAP; tests in Task 2 cover the zero side.
3. Net shares and net value may have opposite signs; tests in Task 2 use a three-broker balanced example.
4. A missing day must not become a zero-net day; tests in Task 3 cover incomplete series.
5. EOD broker data from decision day must be excluded from morning/afternoon decisions; tests in Task 3 cover the boundary.

## File map

- `backend/pyproject.toml`: Python version, package metadata, and pytest dependency.
- `backend/app/__init__.py`, `backend/app/domain/__init__.py`, `backend/app/adapters/__init__.py`: importable package markers.
- `backend/app/domain/broker_flow.py`: normalized record and deterministic arithmetic.
- `backend/app/domain/availability.py`: decision-time evidence gate and daily persistence.
- `backend/app/adapters/broker_csv.py`: strict CSV boundary for per-day broker records.
- `backend/tests/test_broker_flow.py`, `backend/tests/test_availability.py`, `backend/tests/test_broker_csv.py`: behavior tests.

---

### Task 1: Normalize a single broker observation

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/broker_flow.py`
- Test: `backend/tests/test_broker_flow.py`

**Interfaces:**
- Consumes: ISO ticker, trading date, market, investor filter, broker code, per-side shares/value/frequency and an aware `available_at`.
- Produces: `BrokerRow` with validated nonnegative integers, `RG|NG` market, and timezone-aware availability time.

- [ ] **Step 1: Write the failing test** in `backend/tests/test_broker_flow.py`:

```python
from datetime import date, datetime, timezone
import pytest
from app.domain.broker_flow import BrokerRow

BASE = dict(ticker="BBRI", trading_date=date(2026, 10, 2), market="RG",
            investor="all", broker="YP", buy_shares=100, sell_shares=0,
            buy_value=100_000, sell_value=0, buy_freq=1, sell_freq=0,
            available_at=datetime(2026, 10, 2, 12, tzinfo=timezone.utc))

def test_row_rejects_negative_and_ambiguous_market():
    with pytest.raises(ValueError):
        BrokerRow(**{**BASE, "buy_shares": -1})
    with pytest.raises(ValueError):
        BrokerRow(**{**BASE, "market": "ALL"})
    with pytest.raises(ValueError):
        BrokerRow(**{**BASE, "available_at": datetime(2026, 10, 2, 19)})
```

- [ ] **Step 2: Run** `cd backend && python -m pytest tests/test_broker_flow.py -q`; expect import failure.
- [ ] **Step 3: Add** `backend/pyproject.toml` and package markers, then implement `BrokerRow`:

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "bandarai-core"
version = "0.1.0"
requires-python = ">=3.12"

[project.optional-dependencies]
dev = ["pytest>=8,<9"]

[tool.setuptools.packages.find]
where = ["."]
include = ["app*"]
```

```python
from dataclasses import dataclass
from datetime import date, datetime

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
        if any(getattr(self, field) < 0 for field in
               ("buy_shares", "sell_shares", "buy_value", "sell_value", "buy_freq", "sell_freq")):
            raise ValueError("transaction fields cannot be negative")
        if self.available_at.tzinfo is None or self.available_at.utcoffset() is None:
            raise ValueError("available_at must include a timezone")
```

- [ ] **Step 4: Run** `cd backend && python -m pip install -e '.[dev]' && python -m pytest tests/test_broker_flow.py -q`; expect pass.
- [ ] **Step 5: Commit** these files with `git commit -m "feat: define validated broker flow observations"`.

### Task 2: Calculate flow and concentration without inventing cost basis

**Files:**
- Modify: `backend/app/domain/broker_flow.py`
- Modify: `backend/tests/test_broker_flow.py`

**Interfaces:**
- Consumes: `BrokerRow` from Task 1 and a complete list of rows from the same ticker/date/market/investor scope.
- Produces: `net_shares(row) -> int`, `net_value(row) -> int`, `buy_vwap(row) -> Decimal | None`, `sell_vwap(row) -> Decimal | None`, `positive_net_concentration(rows, k) -> Decimal | None`.

- [ ] **Step 1: Add failing tests**:

```python
from decimal import Decimal
from app.domain.broker_flow import net_shares, net_value, buy_vwap, sell_vwap, positive_net_concentration

def test_net_signs_can_disagree_and_zero_side_has_no_vwap():
    row = BrokerRow(**{**BASE, "buy_shares": 200, "buy_value": 20_000,
                       "sell_shares": 190, "sell_value": 21_300})
    assert net_shares(row) == 10
    assert net_value(row) == -1_300
    assert buy_vwap(row) == Decimal(100)
    assert sell_vwap(row) == Decimal(21_300) / Decimal(190)
    assert sell_vwap(BrokerRow(**BASE)) is None

def test_concentration_uses_positive_nets_not_signed_total():
    rows = [BrokerRow(**{**BASE, "broker": code, "buy_shares": buy,
                         "sell_shares": sell, "buy_value": buy,
                         "sell_value": sell})
            for code, buy, sell in [("AA", 40, 0), ("BB", 30, 0),
                                    ("CC", 20, 0), ("DD", 10, 0),
                                    ("EE", 0, 100)]]
    assert positive_net_concentration(rows, 2) == Decimal("0.7")
```

- [ ] **Step 2: Run** `cd backend && python -m pytest tests/test_broker_flow.py -q`; expect missing-function failure.
- [ ] **Step 3: Implement** pure functions in `broker_flow.py`:

```python
from decimal import Decimal
from collections.abc import Sequence

def net_shares(row: BrokerRow) -> int:
    return row.buy_shares - row.sell_shares

def net_value(row: BrokerRow) -> int:
    return row.buy_value - row.sell_value

def buy_vwap(row: BrokerRow) -> Decimal | None:
    return Decimal(row.buy_value) / Decimal(row.buy_shares) if row.buy_shares else None

def sell_vwap(row: BrokerRow) -> Decimal | None:
    return Decimal(row.sell_value) / Decimal(row.sell_shares) if row.sell_shares else None

def positive_net_concentration(rows: Sequence[BrokerRow], k: int) -> Decimal | None:
    if k < 1:
        raise ValueError("k must be positive")
    if not rows:
        return None
    scope = {(r.ticker, r.trading_date, r.market, r.investor) for r in rows}
    if len(scope) != 1:
        raise ValueError("rows must share ticker, date, market and investor scope")
    if rows[0].investor != "all" or sum(net_shares(r) for r in rows) != 0 or sum(net_value(r) for r in rows) != 0:
        raise ValueError("complete all-investor two-sided rows are required")
    positives = sorted((max(net_value(r), 0) for r in rows), reverse=True)
    total = sum(positives)
    return Decimal(sum(positives[:k])) / Decimal(total) if total else None
```

- [ ] **Step 4: Add the scope test below, then run** `cd backend && python -m pytest tests/test_broker_flow.py -q`; expect pass.

```python
def test_concentration_rejects_mixed_tickers():
    first = BrokerRow(**BASE)
    second = BrokerRow(**{**BASE, "ticker": "BBCA", "broker": "AK"})
    with pytest.raises(ValueError, match="share ticker"):
        positive_net_concentration([first, second], 2)
```
- [ ] **Step 5: Commit** with `git commit -m "feat: calculate auditable broker flow metrics"`.

### Task 3: Enforce availability and observed-day persistence

**Files:**
- Create: `backend/app/domain/availability.py`
- Test: `backend/tests/test_availability.py`

**Interfaces:**
- Consumes: `BrokerRow`, timezone-aware `decision_at`, and an explicit ordered sequence of expected trading dates.
- Produces: `visible_rows(rows, decision_at) -> list[BrokerRow]` and `positive_day_persistence(rows, expected_dates, decision_at) -> Decimal | None`.

- [ ] **Step 1: Write failing tests**:

```python
from datetime import date, datetime, timezone
from decimal import Decimal
import pytest
from app.domain.availability import visible_rows, positive_day_persistence
from app.domain.broker_flow import BrokerRow

BASE = dict(ticker="BBRI", trading_date=date(2026, 10, 2), market="RG",
            investor="all", broker="YP", buy_shares=100, sell_shares=0,
            buy_value=100_000, sell_value=0, buy_freq=1, sell_freq=0,
            available_at=datetime(2026, 10, 2, 12, tzinfo=timezone.utc))

def test_today_eod_is_invisible_to_afternoon_decision():
    row = BrokerRow(**BASE)
    afternoon = datetime(2026, 10, 2, 8, tzinfo=timezone.utc)
    assert visible_rows([row], afternoon) == []
    assert visible_rows([row], row.available_at) == [row]

def test_missing_day_does_not_count_as_zero():
    row = BrokerRow(**BASE)
    assert positive_day_persistence([row], [date(2026, 10, 1), date(2026, 10, 2)], row.available_at) is None
    assert positive_day_persistence([row], [date(2026, 10, 2)], row.available_at) == Decimal(1)

def test_persistence_cannot_use_unpublished_row():
    row = BrokerRow(**BASE)
    afternoon = datetime(2026, 10, 2, 8, tzinfo=timezone.utc)
    assert positive_day_persistence([row], [row.trading_date], afternoon) is None
```

- [ ] **Step 2: Run** `cd backend && python -m pytest tests/test_availability.py -q`; expect import failure.
- [ ] **Step 3: Implement** `availability.py`:

```python
from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from app.domain.broker_flow import BrokerRow, net_value

def visible_rows(rows: Sequence[BrokerRow], decision_at: datetime) -> list[BrokerRow]:
    if decision_at.tzinfo is None or decision_at.utcoffset() is None:
        raise ValueError("decision_at must include a timezone")
    return [row for row in rows if row.available_at <= decision_at]

def positive_day_persistence(rows: Sequence[BrokerRow], expected_dates: Sequence[date], decision_at: datetime) -> Decimal | None:
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
    return Decimal(sum(net_value(by_date[d]) > 0 for d in expected_dates)) / Decimal(len(expected_dates))
```

- [ ] **Step 4: Add the duplicate-date test below, then run** `cd backend && python -m pytest tests/test_availability.py -q`; expect pass.

```python
def test_duplicate_daily_row_is_rejected():
    row = BrokerRow(**BASE)
    with pytest.raises(ValueError, match="one broker row"):
        positive_day_persistence([row, row], [row.trading_date], row.available_at)
```
- [ ] **Step 5: Commit** with `git commit -m "feat: prevent broker flow look-ahead"`.

### Task 4: Import explicit-unit daily CSV exports

**Files:**
- Create: `backend/app/adapters/__init__.py`
- Create: `backend/app/adapters/broker_csv.py`
- Test: `backend/tests/test_broker_csv.py`

**Interfaces:**
- Consumes: CSV text with header `ticker,trading_date,market,investor,broker,buy_shares,sell_shares,buy_value,sell_value,buy_freq,sell_freq,available_at`.
- Produces: `parse_broker_csv(text) -> list[BrokerRow]`; raises `ValueError` with a line number for malformed rows.

- [ ] **Step 1: Write failing tests**:

```python
import pytest
from app.adapters.broker_csv import parse_broker_csv

HEADER = "ticker,trading_date,market,investor,broker,buy_shares,sell_shares,buy_value,sell_value,buy_freq,sell_freq,available_at"
GOOD = "BBRI,2026-10-02,RG,all,YP,100,0,100000,0,1,0,2026-10-02T19:00:00+07:00"

def test_explicit_share_columns_import():
    rows = parse_broker_csv(HEADER + "\n" + GOOD + "\n")
    assert len(rows) == 1 and rows[0].buy_shares == 100

def test_ambiguous_lot_header_is_rejected():
    with pytest.raises(ValueError, match="buy_shares"):
        parse_broker_csv(HEADER.replace("buy_shares", "buy_lots") + "\n" + GOOD + "\n")

def test_malformed_number_reports_line():
    with pytest.raises(ValueError, match="line 2"):
        parse_broker_csv(HEADER + "\n" + GOOD.replace(",100,0,", ",unknown,0,") + "\n")
```

- [ ] **Step 2: Run** `cd backend && python -m pytest tests/test_broker_csv.py -q`; expect import failure.
- [ ] **Step 3: Implement** `broker_csv.py`:

```python
import csv
from datetime import date, datetime
from io import StringIO
from app.domain.broker_flow import BrokerRow

FIELDS = ("ticker", "trading_date", "market", "investor", "broker", "buy_shares",
          "sell_shares", "buy_value", "sell_value", "buy_freq", "sell_freq", "available_at")
NUMERIC = ("buy_shares", "sell_shares", "buy_value", "sell_value", "buy_freq", "sell_freq")

def parse_broker_csv(text: str) -> list[BrokerRow]:
    reader = csv.DictReader(StringIO(text))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise ValueError("CSV header must contain exact share and IDR fields in the documented order")
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
    keys = [(r.ticker, r.trading_date, r.market, r.investor, r.broker) for r in result]
    if len(keys) != len(set(keys)):
        raise ValueError("CSV contains duplicate broker observations")
    return result
```

- [ ] **Step 4: Add the duplicate test below, then run** `cd backend && python -m pytest tests/test_broker_csv.py -q`; expect pass.

```python
def test_duplicate_broker_day_is_rejected():
    with pytest.raises(ValueError, match="duplicate broker observations"):
        parse_broker_csv(HEADER + "\n" + GOOD + "\n" + GOOD + "\n")
```
- [ ] **Step 5: Commit** with `git commit -m "feat: import explicit-unit daily broker CSV"`.

## Follow-on plans

After this core passes review, create separate implementation plans for (1) permitted market/news adapters and PostgreSQL persistence, (2) FastAPI research endpoints and decision snapshots, and (3) Next.js research UI, authentication and watchlists. Each should ship a working vertical slice and retain source timestamps. A hosted/public release needs rights review for each data source.
