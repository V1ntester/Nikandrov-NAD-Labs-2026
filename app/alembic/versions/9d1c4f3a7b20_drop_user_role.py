"""Drop the user role column.

Revision ID: 9d1c4f3a7b20
Revises: e1a184ce9f7e
"""

from alembic import op
import sqlalchemy as sa


revision = "9d1c4f3a7b20"
down_revision = "e1a184ce9f7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(20), nullable=False, server_default="creator"),
    )
    op.alter_column("users", "role", server_default=None)
