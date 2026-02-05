"""Add voice support: user_voice_preferences table and message.input_method column.

Revision ID: 003_add_voice_support
Revises: 002_add_chat_tables
Create Date: 2026-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_voice_support'
down_revision: Union[str, None] = '002_add_chat_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_voice_preferences table and add input_method to messages."""
    # Create user_voice_preferences table
    op.create_table(
        'user_voice_preferences',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('voice_output_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('continuous_mode_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('preferred_voice', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('user_id')
    )

    # Add input_method column to messages table
    op.add_column(
        'messages',
        sa.Column('input_method', sa.String(10), nullable=False, server_default='text')
    )

    # Add check constraint for input_method values
    op.create_check_constraint(
        'chk_messages_input_method',
        'messages',
        "input_method IN ('text', 'voice')"
    )


def downgrade() -> None:
    """Remove voice support: drop table and column."""
    # Drop check constraint first
    op.drop_constraint('chk_messages_input_method', 'messages', type_='check')

    # Drop input_method column from messages
    op.drop_column('messages', 'input_method')

    # Drop user_voice_preferences table
    op.drop_table('user_voice_preferences')
