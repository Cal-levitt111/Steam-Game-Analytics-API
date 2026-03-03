import subprocess


EXPECTED_SQL_SNIPPETS = [
    'CREATE TABLE developers',
    'CREATE TABLE games',
    'CREATE TABLE game_developers',
    'CREATE TABLE collections',
    'CREATE TABLE collection_games',
    'CREATE OR REPLACE FUNCTION update_game_search_vector()',
    'CREATE INDEX ix_games_search_vector',
    'CREATE EXTENSION IF NOT EXISTS vector',
    'CREATE INDEX ix_games_embedding_ivfflat_cosine',
]


def test_alembic_upgrade_head_generates_expected_sql() -> None:
    result = subprocess.run(
        ['python', '-m', 'alembic', 'upgrade', 'head', '--sql'],
        capture_output=True,
        text=True,
        check=True,
    )

    sql_script = result.stdout
    for snippet in EXPECTED_SQL_SNIPPETS:
        assert snippet in sql_script

    # These indexes are created in an earlier migration, dropped later,
    # and must be recreated by the hardening migration at head.
    assert sql_script.rfind('CREATE INDEX ix_games_search_vector') > sql_script.rfind('DROP INDEX ix_games_search_vector')
    assert sql_script.rfind('CREATE INDEX ix_games_metacritic_score') > sql_script.rfind('DROP INDEX ix_games_metacritic_score')
    assert sql_script.rfind('CREATE INDEX ix_games_release_date') > sql_script.rfind('DROP INDEX ix_games_release_date')
    assert sql_script.rfind('CREATE INDEX ix_games_price_usd') > sql_script.rfind('DROP INDEX ix_games_price_usd')
