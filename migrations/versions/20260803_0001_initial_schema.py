"""Create the QSecNet core persistence schema.

Revision ID: 20260803_0001
Revises:
Create Date: 2026-08-03
"""

from alembic import op

from backend.models import Base

revision = "20260803_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all first-release tables from the declarative metadata."""
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Remove all first-release tables in dependency order."""
    Base.metadata.drop_all(bind=op.get_bind())
