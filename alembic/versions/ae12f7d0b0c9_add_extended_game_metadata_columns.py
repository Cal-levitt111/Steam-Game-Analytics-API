"""add extended game metadata columns

Revision ID: ae12f7d0b0c9
Revises: 59a9fbcd1491
Create Date: 2026-03-03 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae12f7d0b0c9'
down_revision: Union[str, Sequence[str], None] = '59a9fbcd1491'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('games', sa.Column('estimated_owners', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('peak_ccu', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('discount_percent', sa.SmallInteger(), nullable=True))
    op.add_column('games', sa.Column('dlc_count', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('about_the_game', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('supported_languages', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('full_audio_languages', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('reviews', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('support_url', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('support_email', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('metacritic_url', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('user_score', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('score_rank', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('achievements', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('recommendations', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('average_playtime_forever', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('average_playtime_two_weeks', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('median_playtime_forever', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('median_playtime_two_weeks', sa.Integer(), nullable=True))
    op.add_column('games', sa.Column('screenshots', sa.Text(), nullable=True))
    op.add_column('games', sa.Column('movies', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('games', 'movies')
    op.drop_column('games', 'screenshots')
    op.drop_column('games', 'median_playtime_two_weeks')
    op.drop_column('games', 'median_playtime_forever')
    op.drop_column('games', 'average_playtime_two_weeks')
    op.drop_column('games', 'average_playtime_forever')
    op.drop_column('games', 'notes')
    op.drop_column('games', 'recommendations')
    op.drop_column('games', 'achievements')
    op.drop_column('games', 'score_rank')
    op.drop_column('games', 'user_score')
    op.drop_column('games', 'metacritic_url')
    op.drop_column('games', 'support_email')
    op.drop_column('games', 'support_url')
    op.drop_column('games', 'reviews')
    op.drop_column('games', 'full_audio_languages')
    op.drop_column('games', 'supported_languages')
    op.drop_column('games', 'about_the_game')
    op.drop_column('games', 'dlc_count')
    op.drop_column('games', 'discount_percent')
    op.drop_column('games', 'peak_ccu')
    op.drop_column('games', 'estimated_owners')
