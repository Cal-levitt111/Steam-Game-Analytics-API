"""add pgvector embedding column

Revision ID: c51ef0df6f74
Revises: b8f4f9515b2e
Create Date: 2026-03-03 18:10:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c51ef0df6f74'
down_revision: Union[str, Sequence[str], None] = 'b8f4f9515b2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    op.execute('ALTER TABLE games ADD COLUMN embedding vector(384);')
    op.execute(
        """
        CREATE INDEX ix_games_embedding_ivfflat_cosine
        ON games
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP INDEX IF EXISTS ix_games_embedding_ivfflat_cosine;')
    op.execute('ALTER TABLE games DROP COLUMN IF EXISTS embedding;')
