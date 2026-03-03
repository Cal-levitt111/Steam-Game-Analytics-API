import subprocess


EXPECTED_SQL_SNIPPETS = [
    'CREATE TABLE developers',
    'CREATE TABLE games',
    'CREATE TABLE game_developers',
    'CREATE TABLE collections',
    'CREATE TABLE collection_games',
    'CREATE OR REPLACE FUNCTION update_game_search_vector()',
    'CREATE INDEX ix_games_search_vector',
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