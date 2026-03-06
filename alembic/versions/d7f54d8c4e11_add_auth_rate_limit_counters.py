"""add auth rate limit counters

Revision ID: d7f54d8c4e11
Revises: c51ef0df6f74
Create Date: 2026-03-05 16:02:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7f54d8c4e11'
down_revision: Union[str, Sequence[str], None] = 'c51ef0df6f74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'auth_rate_limit_counters',
        sa.Column('scope', sa.Text(), nullable=False),
        sa.Column('identifier_hash', sa.Text(), nullable=False),
        sa.Column('window_started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('blocked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('scope', 'identifier_hash'),
    )
    op.create_index(
        'ix_auth_rate_limit_counters_blocked_until',
        'auth_rate_limit_counters',
        ['blocked_until'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_auth_rate_limit_counters_blocked_until', table_name='auth_rate_limit_counters')
    op.drop_table('auth_rate_limit_counters')
