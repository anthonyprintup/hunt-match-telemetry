from contextlib import closing

import pytest

from hunt.database.client import Client as DatabaseClient, Cursor


@pytest.mark.parametrize("table_name", ("data_hashes", "player_log_bountyhunt", "player_log_quickplay"))
def test_database_tables(database_client: DatabaseClient, table_name: str) -> None:
    cursor: Cursor
    with closing(database_client.cursor()) as cursor:
        query: str = "SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?)"
        assert cursor.execute(query, (table_name,)).fetchone()[0] >= 1, "Missing database table."
