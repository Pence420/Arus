"""Separate publisher publication from aggregator first-seen time.

Revision ID: 0002_news_seen_time
Revises: 0001_observations
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_news_seen_time"
down_revision = "0001_observations"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("news_items", sa.Column("source_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("update news_items set source_seen_at = available_at")
    op.alter_column("news_items", "source_seen_at", nullable=False)
    op.alter_column("news_items", "published_at", nullable=True)


def downgrade():
    op.execute("update news_items set published_at = source_seen_at where published_at is null")
    op.alter_column("news_items", "published_at", nullable=False)
    op.drop_column("news_items", "source_seen_at")
