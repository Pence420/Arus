"""Keep broker import versions and record when article links were made.

Revision ID: 0004_evidence_versions
Revises: 0003_price_versions
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_evidence_versions"
down_revision = "0003_price_versions"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("broker_flow_rows_ticker_trading_date_market_investor_broker_key",
                       "broker_flow_rows", type_="unique")
    op.create_unique_constraint("uq_broker_import_version", "broker_flow_rows",
        ["ticker", "trading_date", "market", "investor", "broker", "provider", "batch_id"])
    op.add_column("news_ticker_links", sa.Column("ingested_at", sa.DateTime(timezone=True),
        server_default=sa.text("now()"), nullable=False))


def downgrade():
    op.drop_column("news_ticker_links", "ingested_at")
    op.drop_constraint("uq_broker_import_version", "broker_flow_rows", type_="unique")
    op.create_unique_constraint("broker_flow_rows_ticker_trading_date_market_investor_broker_key",
        "broker_flow_rows", ["ticker", "trading_date", "market", "investor", "broker", "provider"])
