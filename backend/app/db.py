"""Small pooled database connection shared by API requests."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://bandarai:bandarai@localhost:5432/bandarai")
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=5, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
