"""drop redundant duplicate description columns

Revision ID: 6c2ec617561e
Revises: 4dd6c697e688
Create Date: 2026-03-03 14:57:36.757011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c2ec617561e'
down_revision: Union[str, Sequence[str], None] = '4dd6c697e688'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('DROP TRIGGER IF EXISTS trg_games_search_vector ON games;')
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
                setweight(to_tsvector('english', COALESCE(NEW.about_the_game, '')), 'B') ||
                setweight(to_tsvector('english', tags_text), 'C');

            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_games_search_vector
        BEFORE INSERT OR UPDATE OF name, about_the_game
        ON games
        FOR EACH ROW
        EXECUTE FUNCTION update_game_search_vector();
        """
    )
    op.execute(
        """
        UPDATE games g
        SET search_vector =
            setweight(to_tsvector('english', COALESCE(g.name, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(g.about_the_game, '')), 'B') ||
            setweight(
                to_tsvector(
                    'english',
                    COALESCE(
                        (
                            SELECT string_agg(t.name, ' ')
                            FROM game_tags gt
                            JOIN tags t ON t.id = gt.tag_id
                            WHERE gt.game_id = g.id
                        ),
                        ''
                    )
                ),
                'C'
            );
        """
    )

    op.drop_column('games', 'detailed_description')
    op.drop_column('games', 'short_description')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('games', sa.Column('short_description', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('games', sa.Column('detailed_description', sa.TEXT(), autoincrement=False, nullable=True))
    op.execute(
        """
        UPDATE games
        SET
            short_description = COALESCE(short_description, about_the_game),
            detailed_description = COALESCE(detailed_description, about_the_game);
        """
    )
    op.execute('DROP TRIGGER IF EXISTS trg_games_search_vector ON games;')
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
    op.execute(
        """
        UPDATE games g
        SET search_vector =
            setweight(to_tsvector('english', COALESCE(g.name, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(g.short_description, '')), 'B') ||
            setweight(
                to_tsvector(
                    'english',
                    COALESCE(
                        (
                            SELECT string_agg(t.name, ' ')
                            FROM game_tags gt
                            JOIN tags t ON t.id = gt.tag_id
                            WHERE gt.game_id = g.id
                        ),
                        ''
                    )
                ),
                'C'
            );
        """
    )
