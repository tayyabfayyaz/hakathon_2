"""Initial schema with users and todos tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Create todos table
    op.create_table(
        "todos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_todos_user_id"), "todos", ["user_id"], unique=False)
    op.create_index(op.f("ix_todos_created_at"), "todos", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_todos_created_at"), table_name="todos")
    op.drop_index(op.f("ix_todos_user_id"), table_name="todos")
    op.drop_table("todos")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
