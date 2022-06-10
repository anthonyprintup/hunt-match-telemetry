import sqlite3
from sqlite3 import Connection, Cursor
from dataclasses import dataclass
from contextlib import closing

from ..constants import CREATE_TABLE_QUERY


@dataclass(kw_only=True)
class Database:
    file_path: str
    _connection: Connection = None

    def __post_init__(self):
        """Setup the database connection."""
        self._connection = sqlite3.connect(f"file:{self.file_path}", uri=True)
        self._setup_database()

    def _setup_database(self):
        """Sets up the database by creating the required tables."""
        cursor: Cursor
        with closing(self.cursor()) as cursor:
            cursor.execute(CREATE_TABLE_QUERY)
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
