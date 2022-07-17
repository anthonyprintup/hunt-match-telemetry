from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from sqlite3 import Connection, Cursor, connect as sqlite3_connect
from types import TracebackType

from ..constants import DATABASE_TABLE_QUERIES


@dataclass(kw_only=True)
class Client:
    file_path: str
    _connection: Connection | None = None

    def __post_init__(self) -> None:
        """Setup the database connection."""
        self._connection = sqlite3_connect(f"file:{self.file_path}", check_same_thread=False, uri=True)
        self._setup_database()

    def _setup_database(self) -> None:
        """Sets up the database by creating the required tables."""
        cursor: Cursor
        with closing(self.cursor()) as cursor:
            # Setup each table
            table: str
            for table_query in DATABASE_TABLE_QUERIES:
                cursor.execute(table_query)
        self.save()

    def cursor(self) -> Cursor:
        """Returns a new Cursor instance."""
        assert self._connection is not None
        return self._connection.cursor()

    def save(self) -> None:
        """Commit the changes to disk."""
        assert self._connection is not None
        self._connection.commit()

    def close(self) -> None:
        """Closes the connection."""
        assert self._connection is not None
        self._connection.close()

    # Context manager support
    def __enter__(self) -> Client:
        """Return self when entering the scope."""
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:
        """Close the database connection when exiting the scope."""
        self.close()
