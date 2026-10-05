"""Normalized source observations; no inferred trading signals live here."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


IdType = BigInteger().with_variant(Integer, "sqlite")


class Stock(Base):
    __tablename__ = "stocks"
    ticker: Mapped[str] = mapped_column(String(12), primary_key=True)
    name: Mapped[str] = mapped_column(Text)


class PriceBar(Base):
    __tablename__ = "price_bars"
    __table_args__ = (
        UniqueConstraint("ticker", "provider", "observed_at", "available_at", name="uq_price_observation_version"),
        CheckConstraint("volume >= 0"),
        CheckConstraint("low <= high AND open >= low AND open <= high AND close >= low AND close <= high"),
        Index("ix_price_ticker_available", "ticker", "available_at"),
    )
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(ForeignKey("stocks.ticker"))
    provider: Mapped[str] = mapped_column(Text)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    open: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    high: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    low: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    volume: Mapped[int] = mapped_column(BigInteger)


class NewsItem(Base):
    __tablename__ = "news_items"
    __table_args__ = (UniqueConstraint("provider", "source_key"),)
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(Text)
    source_key: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NewsTickerLink(Base):
    __tablename__ = "news_ticker_links"
    __table_args__ = (UniqueConstraint("news_id", "ticker"), Index("ix_news_link_ticker", "ticker"))
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news_items.id", ondelete="CASCADE"))
    ticker: Mapped[str] = mapped_column(ForeignKey("stocks.ticker"))
    match_reason: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(Text)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ImportBatch(Base):
    __tablename__ = "import_batches"
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    row_count: Mapped[int] = mapped_column(BigInteger)


class BrokerFlowRow(Base):
    __tablename__ = "broker_flow_rows"
    __table_args__ = (
        UniqueConstraint("ticker", "trading_date", "market", "investor", "broker", "provider", "batch_id",
                         name="uq_broker_import_version"),
        CheckConstraint("buy_shares >= 0 AND sell_shares >= 0 AND buy_value >= 0 AND sell_value >= 0 AND buy_freq >= 0 AND sell_freq >= 0"),
        Index("ix_broker_ticker_available", "ticker", "available_at"),
        Index("ix_broker_batch", "batch_id"),
    )
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(ForeignKey("stocks.ticker"))
    trading_date: Mapped[date] = mapped_column(Date)
    market: Mapped[str] = mapped_column(String(2))
    investor: Mapped[str] = mapped_column(String(3))
    broker: Mapped[str] = mapped_column(String(8))
    provider: Mapped[str] = mapped_column(Text)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"))
    buy_shares: Mapped[int] = mapped_column(BigInteger)
    sell_shares: Mapped[int] = mapped_column(BigInteger)
    buy_value: Mapped[int] = mapped_column(BigInteger)
    sell_value: Mapped[int] = mapped_column(BigInteger)
    buy_freq: Mapped[int] = mapped_column(BigInteger)
    sell_freq: Mapped[int] = mapped_column(BigInteger)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProviderRun(Base):
    __tablename__ = "provider_runs"
    id: Mapped[int] = mapped_column(IdType, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(Text)
    ticker: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)
