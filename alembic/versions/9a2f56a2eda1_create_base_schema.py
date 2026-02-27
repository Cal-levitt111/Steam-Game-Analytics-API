"""create base schema

Revision ID: 9a2f56a2eda1
Revises:
Create Date: 2026-02-27 13:34:12.705286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a2f56a2eda1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_dimension_table(name: str) -> None:
    op.create_table(
        name,
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False, unique=True),
        sa.Column('slug', sa.Text(), nullable=False, unique=True),
    )


def upgrade() -> None:
    """Upgrade schema."""
    _create_dimension_table('developers')
    _create_dimension_table('publishers')
    _create_dimension_table('genres')
    _create_dimension_table('tags')
    _create_dimension_table('categories')

    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('steam_app_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('detailed_description', sa.Text(), nullable=True),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('price_usd', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('metacritic_score', sa.SmallInteger(), nullable=True),
        sa.Column('positive_reviews', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('negative_reviews', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('required_age', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('website', sa.Text(), nullable=True),
        sa.Column('header_image', sa.Text(), nullable=True),
        sa.Column('windows', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('mac', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('linux', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_table(
        'game_genres',
        sa.Column('game_id', sa.Integer(), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('genre_id', sa.Integer(), sa.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_table(
        'game_tags',
        sa.Column('game_id', sa.Integer(), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_table(
        'game_categories',
        sa.Column('game_id', sa.Integer(), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_table(
        'game_developers',
        sa.Column('game_id', sa.Integer(), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('developer_id', sa.Integer(), sa.ForeignKey('developers.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_table(
        'game_publishers',
        sa.Column('game_id', sa.Integer(), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('publisher_id', sa.Integer(), sa.ForeignKey('publishers.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.Text(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_table(
        'collection_games',
        sa.Column('collection_id', sa.Integer(), sa.ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('game_id', sa.Integer(), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('collection_games')
    op.drop_table('collections')
    op.drop_table('users')
    op.drop_table('game_publishers')
    op.drop_table('game_developers')
    op.drop_table('game_categories')
    op.drop_table('game_tags')
    op.drop_table('game_genres')
    op.drop_table('games')
    op.drop_table('categories')
    op.drop_table('tags')
    op.drop_table('genres')
    op.drop_table('publishers')
    op.drop_table('developers')