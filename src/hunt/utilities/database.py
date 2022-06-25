from __future__ import annotations

import sqlite3
from sqlite3 import Connection, Cursor
from dataclasses import dataclass
from contextlib import closing
from types import TracebackType

from ..constants import DATABASE_TABLE_QUERIES


@dataclass(kw_only=True)
class Database:
    file_path: str
    _connection: Connection = None

    def __post_init__(self):
        """Setup the database connection."""
        self._connection = sqlite3.connect(f"file:{self.file_path}", check_same_thread=False, uri=True)
        self._setup_database()

    def _setup_database(self):
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
        return self._connection.cursor()

    def save(self):
        """Commit the changes to disk."""
        self._connection.commit()

    def close(self):
        """Closes the connection."""
        self._connection.close()

    # Context manager support
    def __enter__(self) -> Database:
        """Return self when entering the scope."""
        return self

    def __exit__(self, exc_type: type(BaseException) | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None):
        """Close the database connection when exiting the scope."""
        self.close()
