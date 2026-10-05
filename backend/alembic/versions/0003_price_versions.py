"""Keep separate fetch-time versions of the same price bar.

Revision ID: 0003_price_versions
Revises: 0002_news_seen_time
"""

from alembic import op

revision = "0003_price_versions"
down_revision = "0002_news_seen_time"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("price_bars_ticker_provider_observed_at_key", "price_bars", type_="unique")
    op.create_unique_constraint("uq_price_observation_version", "price_bars",
                                ["ticker", "provider", "observed_at", "available_at"])


def downgrade():
    op.drop_constraint("uq_price_observation_version", "price_bars", type_="unique")
    op.create_unique_constraint("price_bars_ticker_provider_observed_at_key", "price_bars",
                                ["ticker", "provider", "observed_at"])
