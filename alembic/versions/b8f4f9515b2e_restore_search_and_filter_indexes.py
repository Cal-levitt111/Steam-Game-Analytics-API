"""restore search and filter indexes

Revision ID: b8f4f9515b2e
Revises: 6c2ec617561e
Create Date: 2026-03-03 17:35:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b8f4f9515b2e'
down_revision: Union[str, Sequence[str], None] = '6c2ec617561e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_games_search_vector', 'games', ['search_vector'], postgresql_using='gin')
    op.create_index('ix_games_metacritic_score', 'games', ['metacritic_score'])
    op.create_index('ix_games_release_date', 'games', ['release_date'])
    op.create_index('ix_games_price_usd', 'games', ['price_usd'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_games_price_usd', table_name='games')
    op.drop_index('ix_games_release_date', table_name='games')
    op.drop_index('ix_games_metacritic_score', table_name='games')
    op.drop_index('ix_games_search_vector', table_name='games', postgresql_using='gin')
