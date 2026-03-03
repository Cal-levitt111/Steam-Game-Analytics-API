"""add fts and indexes

Revision ID: 59a9fbcd1491
Revises: 9a2f56a2eda1
Create Date: 2026-02-27 13:40:44.966970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '59a9fbcd1491'
down_revision: Union[str, Sequence[str], None] = '9a2f56a2eda1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('games', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_game_search_vector()
        RETURNS trigger
        AS $$
        DECLARE
            tags_text text;
        BEGIN
            SELECT COALESCE(string_agg(t.name, ' '), '') INTO tags_text
            FROM game_tags gt
            JOIN tags t ON t.id = gt.tag_id
            WHERE gt.game_id = NEW.id;

            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.short_description, '')), 'B') ||
                setweight(to_tsvector('english', tags_text), 'C');

            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_games_search_vector
        BEFORE INSERT OR UPDATE OF name, short_description
        ON games
        FOR EACH ROW
        EXECUTE FUNCTION update_game_search_vector();
        """
    )

    op.create_index('ix_games_search_vector', 'games', ['search_vector'], postgresql_using='gin')
    op.create_index('ix_games_metacritic_score', 'games', ['metacritic_score'])
    op.create_index('ix_games_release_date', 'games', ['release_date'])
    op.create_index('ix_games_price_usd', 'games', ['price_usd'])
    op.create_index('ix_game_genres_genre_id', 'game_genres', ['genre_id'])
    op.create_index('ix_game_tags_tag_id', 'game_tags', ['tag_id'])
    op.create_index('ix_collections_user_id', 'collections', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_collections_user_id', table_name='collections')
    op.drop_index('ix_game_tags_tag_id', table_name='game_tags')
    op.drop_index('ix_game_genres_genre_id', table_name='game_genres')
    op.drop_index('ix_games_price_usd', table_name='games')
    op.drop_index('ix_games_release_date', table_name='games')
    op.drop_index('ix_games_metacritic_score', table_name='games')
    op.drop_index('ix_games_search_vector', table_name='games')

    op.execute('DROP TRIGGER IF EXISTS trg_games_search_vector ON games;')
    op.execute('DROP FUNCTION IF EXISTS update_game_search_vector();')

    op.drop_column('games', 'search_vector')