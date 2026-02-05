"""Add reminder tables for task deadline reminders

Revision ID: 004
Revises: 003
Create Date: 2026-01-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add deadline column to tasks table
    op.add_column(
        "tasks",
        sa.Column("deadline", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_tasks_deadline", "tasks", ["deadline"])

    # Create user_whatsapp table
    op.create_table(
        "user_whatsapp",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("country_code", sa.String(5), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("verification_code", sa.String(6), nullable=True),
        sa.Column("code_expires_at", sa.DateTime(), nullable=True),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_user_whatsapp_phone", "user_whatsapp", ["country_code", "phone_number"])

    # Create reminder_preferences table
    op.create_table(
        "reminder_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("default_intervals", postgresql.JSON(), nullable=False, server_default='["24h"]'),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create scheduled_reminders table
    op.create_table(
        "scheduled_reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("scheduled_for", sa.DateTime(), nullable=False),
        sa.Column("reminder_interval", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("celery_task_id", sa.String(255), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_scheduled_reminders_status_scheduled", "scheduled_reminders", ["status", "scheduled_for"])

    # Create reminder_logs table
    op.create_table(
        "reminder_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scheduled_reminder_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scheduled_reminders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("phone_number", sa.String(25), nullable=False),
        sa.Column("message_content", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("delivery_status", sa.String(20), nullable=False, server_default="sent"),
        sa.Column("whatsapp_message_id", sa.String(100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    # Drop tables in reverse order of dependencies
    op.drop_table("reminder_logs")
    op.drop_table("scheduled_reminders")
    op.drop_table("reminder_preferences")
    op.drop_index("ix_user_whatsapp_phone", table_name="user_whatsapp")
    op.drop_table("user_whatsapp")
    op.drop_index("ix_tasks_deadline", table_name="tasks")
    op.drop_column("tasks", "deadline")
