from pathlib import Path
from sqlite3 import Connection, connect as sqlite3_connect
from typing import Any, Generator

from pytest import MonkeyPatch, fixture

from hunt.database.client import Client as DatabaseClient

_DUMMY_FILE_PATH: Path = Path("dummy_file_path")


# noinspection PyUnusedLocal
def mock_sqlite3_connect(database: str, *args: Any, **kwargs: Any) -> Connection:
    """
    Mock sqlite3.connect to replace the database argument.
    :param database: the original database argument
    :param args: remaining positional arguments
    :param kwargs: remaining keyword arguments
    :return: a sqlite3 Connection instance
    """
    assert database == f"file:{_DUMMY_FILE_PATH}"
    return sqlite3_connect(":memory:", *args, **kwargs)


@fixture(scope="module")
def monkeypatch_module_scope() -> Generator[MonkeyPatch, None, None]:
    monkeypatch: MonkeyPatch = MonkeyPatch()
    yield monkeypatch
    monkeypatch.undo()


@fixture(scope="module")
def database_client(monkeypatch_module_scope: MonkeyPatch) -> Generator[DatabaseClient, None, None]:
    """
    A fixture to provide an already set up Database.
    :return: a generator which yields a DatabaseClient instance
    """
    monkeypatch_module_scope.setattr("hunt.database.client.sqlite3_connect", mock_sqlite3_connect)

    database: DatabaseClient
    with DatabaseClient(file_path=_DUMMY_FILE_PATH) as database:
        yield database
