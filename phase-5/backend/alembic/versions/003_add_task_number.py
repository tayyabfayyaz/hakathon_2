"""Add task_number column for voice/chat agents

Revision ID: 003
Revises: 002
Create Date: 2025-01-26

"""
from typing import Sequence, Union
import random

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add task_number column with a temporary default
    op.add_column(
        "tasks",
        sa.Column(
            "task_number",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # Update existing tasks with unique random numbers per user
    connection = op.get_bind()

    # Get all existing tasks grouped by user
    tasks = connection.execute(
        sa.text("SELECT id, user_id FROM tasks ORDER BY user_id, created_at")
    ).fetchall()

    # Generate unique task numbers per user
    user_numbers = {}  # user_id -> set of used numbers

    for task_id, user_id in tasks:
        if user_id not in user_numbers:
            user_numbers[user_id] = set()

        # Generate unique number for this user
        while True:
            task_number = random.randint(1000, 9999)
            if task_number not in user_numbers[user_id]:
                user_numbers[user_id].add(task_number)
                break

        # Update the task
        connection.execute(
            sa.text("UPDATE tasks SET task_number = :num WHERE id = :id"),
            {"num": task_number, "id": task_id}
        )

    # Create index for efficient lookups by task_number
    op.create_index("ix_tasks_task_number", "tasks", ["task_number"])
    op.create_index("ix_tasks_user_task_number", "tasks", ["user_id", "task_number"])


def downgrade() -> None:
    op.drop_index("ix_tasks_user_task_number", table_name="tasks")
    op.drop_index("ix_tasks_task_number", table_name="tasks")
    op.drop_column("tasks", "task_number")
