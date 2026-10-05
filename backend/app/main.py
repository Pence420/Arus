"""Local-first source ingestion and decision-time research API."""

import os
import re
from datetime import datetime, timezone

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.adapters.gdelt_news import discover_articles
from app.adapters.antara_rss import discover_antara_articles
from app.adapters.yahoo_price import fetch_price_bars
from app.db import get_session
from app.domain.broker_flow import BrokerRow
from app.adapters.broker_csv import parse_broker_csv
from app.services.ingest import record_run, store_articles, store_broker_rows, store_price_bars
from app.services.research import stock_research


app = FastAPI(title="BandarAI research API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])
TICKER = re.compile(r"^[A-Z]{4,5}$")


def checked_ticker(ticker: str) -> str:
    value = ticker.upper()
    if not TICKER.fullmatch(value):
        raise HTTPException(422, "Ticker BEI tidak valid")
    return value


def local_request(request: Request) -> bool:
    return request.client is not None and request.client.host in {"127.0.0.1", "::1", "testclient"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stocks/{ticker}/research")
def research(ticker: str, request: Request, decision_at: datetime | None = None,
             session: Session = Depends(get_session)):
    ticker = checked_ticker(ticker)
    moment = decision_at or datetime.now(timezone.utc)
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise HTTPException(422, "decision_at harus punya zona waktu")
    return stock_research(session, ticker, moment,
                          local_request(request) and os.getenv("ENABLE_PERSONAL_YAHOO") == "1")


@app.post("/api/stocks/{ticker}/refresh-price")
def refresh_price(ticker: str, request: Request, session: Session = Depends(get_session)):
    ticker = checked_ticker(ticker)
    if not local_request(request) or os.getenv("ENABLE_PERSONAL_YAHOO") != "1":
        raise HTTPException(403, "Yahoo hanya untuk penggunaan pribadi/lokal dan belum diaktifkan")
    started = datetime.now(timezone.utc)
    try:
        with httpx.Client(headers={"User-Agent": "BandarAI local research/0.1"}) as client:
            rows = fetch_price_bars(ticker, client)
        count = store_price_bars(session, rows)
        record_run(session, "yahoo", ticker, started, "success")
        return {"stored": count, "provider": "yahoo"}
    except (httpx.HTTPError, ValueError) as exc:
        session.rollback()
        record_run(session, "yahoo", ticker, started, "failed", str(exc))
        raise HTTPException(502, "Sumber harga gagal; data terakhir tidak dihapus") from exc


@app.post("/api/stocks/{ticker}/refresh-news")
def refresh_news(ticker: str, request: Request, session: Session = Depends(get_session)):
    ticker = checked_ticker(ticker)
    if not local_request(request):
        raise HTTPException(403, "Refresh hanya tersedia di aplikasi lokal")
    started = datetime.now(timezone.utc)
    try:
        with httpx.Client(headers={"User-Agent": "BandarAI local research/0.1"}, follow_redirects=True) as client:
            articles = discover_antara_articles(ticker, client)
            provider = "antara_rss"
            reason = "ANTARA title contains ticker or verified company alias"
            if not articles and os.getenv("ENABLE_GDELT") == "1":
                articles = discover_articles(f'"{ticker}" AND (saham OR emiten OR stock)', client)
                provider = "gdelt"
                reason = "GDELT query: ticker plus market keyword; unverified title match"
        count = store_articles(session, articles, ticker, reason)
        record_run(session, provider, ticker, started, "success")
        return {"stored": count, "provider": provider}
    except (httpx.HTTPError, ValueError) as exc:
        session.rollback()
        record_run(session, "news", ticker, started, "failed", str(exc))
        raise HTTPException(502, "Sumber berita gagal; data terakhir tidak dihapus") from exc


@app.post("/api/import/broker-csv")
async def import_broker_csv(file: UploadFile, request: Request,
                            session: Session = Depends(get_session)):
    if not local_request(request) or os.getenv("ENABLE_LOCAL_IMPORT") != "1":
        raise HTTPException(403, "Impor lokal tidak diaktifkan")
    raw = await file.read(2_000_001)
    if len(raw) > 2_000_000:
        raise HTTPException(413, "CSV melebihi 2 MB")
    try:
        rows = parse_broker_csv(raw.decode("utf-8-sig"))
        count = store_broker_rows(session, rows, file.filename or "upload.csv")
        session.commit()
        return {"stored": count}
    except (UnicodeDecodeError, ValueError) as exc:
        session.rollback()
        raise HTTPException(422, str(exc)) from exc
