"""Add notifications table for real-time notifications

Revision ID: 005
Revises: 004
Create Date: 2026-02-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("type", sa.String(30), nullable=False),  # deadline_reminder, deadline_reached, task_overdue, system
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="sent"),  # pending, sent, read, dismissed
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    # Index for fetching user notifications sorted by date
    op.create_index("ix_notifications_user_created", "notifications", ["user_id", "created_at"])
    # Index for unread count queries
    op.create_index("ix_notifications_user_status", "notifications", ["user_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_notifications_user_status", table_name="notifications")
    op.drop_index("ix_notifications_user_created", table_name="notifications")
    op.drop_table("notifications")
