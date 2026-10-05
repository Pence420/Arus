from datetime import date, datetime, timezone

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.domain.broker_flow import BrokerRow
from app.main import app
from app.models import Base, BrokerFlowRow, ProviderRun
from app.services.ingest import store_broker_rows


def client_for_test_db():
    engine = create_engine("sqlite+pysqlite:///:memory:",
                           connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app), engine


def test_empty_report_states_are_not_fake_zeroes():
    client, _ = client_for_test_db()
    try:
        response = client.get("/api/stocks/BBRI/research")
        assert response.status_code == 200
        data = response.json()
        assert data["price"]["bar"] is None
        assert data["broker_flow"]["status"] == "no_data"
        assert data["broker_flow"]["rows"] == []
        assert data["news"]["items"] == []
    finally:
        app.dependency_overrides.clear()


def test_morning_report_excludes_same_day_eod_broker():
    client, engine = client_for_test_db()
    try:
        row = BrokerRow("BBRI", date(2026, 10, 2), "RG", "all", "YP",
                        100, 0, 400000, 0, 1, 0,
                        datetime(2026, 10, 2, 12, tzinfo=timezone.utc))
        with Session(engine) as session:
            store_broker_rows(session, [row], "source.csv")
            session.commit()
        before = client.get("/api/stocks/BBRI/research",
                            params={"decision_at": "2026-10-02T09:00:00+07:00"}).json()
        assert before["broker_flow"]["status"] == "unavailable_at_decision"
        assert before["broker_flow"]["rows"] == []
        after = client.get("/api/stocks/BBRI/research",
                           params={"decision_at": "2030-10-02T20:00:00+07:00"}).json()
        assert after["broker_flow"]["rows"][0]["net_shares"] == 100
    finally:
        app.dependency_overrides.clear()


def test_rejects_naive_decision_and_invalid_ticker():
    client, _ = client_for_test_db()
    try:
        assert client.get("/api/stocks/BBRI/research",
                          params={"decision_at": "2026-10-02T09:00:00"}).status_code == 422
        assert client.get("/api/stocks/123/research").status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_later_broker_correction_cannot_rewrite_earlier_decision():
    client, engine = client_for_test_db()
    try:
        first = BrokerRow("BBRI", date(2026, 10, 2), "RG", "all", "YP",
                          100, 0, 400000, 0, 1, 0,
                          datetime(2026, 10, 2, 12, tzinfo=timezone.utc))
        corrected = BrokerRow("BBRI", date(2026, 10, 2), "RG", "all", "YP",
                              150, 0, 600000, 0, 1, 0,
                              datetime(2026, 10, 2, 12, tzinfo=timezone.utc))
        with Session(engine) as session:
            store_broker_rows(session, [first], "first.csv")
            store_broker_rows(session, [corrected], "corrected.csv")
            versions = session.query(BrokerFlowRow).order_by(BrokerFlowRow.batch_id).all()
            assert len(versions) == 2
            versions[0].ingested_at = datetime(2026, 10, 2, 13, tzinfo=timezone.utc)
            versions[1].ingested_at = datetime(2026, 10, 3, 13, tzinfo=timezone.utc)
            session.commit()
        before = client.get("/api/stocks/BBRI/research",
                            params={"decision_at": "2026-10-02T20:00:00+07:00"}).json()
        after = client.get("/api/stocks/BBRI/research",
                           params={"decision_at": "2026-10-04T20:00:00+07:00"}).json()
        assert before["broker_flow"]["rows"][0]["net_shares"] == 100
        assert after["broker_flow"]["rows"][0]["net_shares"] == 150
    finally:
        app.dependency_overrides.clear()


def test_failed_provider_run_is_recorded(monkeypatch):
    client, engine = client_for_test_db()
    try:
        monkeypatch.setenv("ENABLE_PERSONAL_YAHOO", "1")

        def fail_fetch(*args, **kwargs):
            raise httpx.ConnectTimeout("provider timed out")

        monkeypatch.setattr("app.main.fetch_price_bars", fail_fetch)
        response = client.post("/api/stocks/BBRI/refresh-price")
        assert response.status_code == 502
        with Session(engine) as session:
            run = session.query(ProviderRun).one()
            assert run.status == "failed"
            assert run.provider == "yahoo"
    finally:
        app.dependency_overrides.clear()
