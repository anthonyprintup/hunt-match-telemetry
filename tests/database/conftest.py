import sqlite3
from sqlite3 import connect as sqlite3_connect, Connection
from typing import Any, Generator

from pytest import fixture, MonkeyPatch

from hunt.database.client import Client as DatabaseClient


def mock_connect(_: str, *args: Any, **kwargs: Any) -> Connection:
    """
    Mock sqlite3.connect to replace the database argument.
    :param _: the original (and ignored) database argument
    :param args: remaining positional arguments
    :param kwargs: remaining keyword arguments
    :return: a sqlite3 Connection instance
    """
    return sqlite3_connect(":memory:", *args, **kwargs)


@fixture(autouse=True)
def database_client_patch(monkeypatch: MonkeyPatch) -> None:
    """
    Set up sqlite3 mocking using monkey patching.
    :param monkeypatch: a MonkeyPatch instance
    """
    monkeypatch.setattr(sqlite3, "connect", mock_connect)


@fixture(scope="session")
def database_client() -> Generator[DatabaseClient, None, None]:
    """
    A fixture to provide an already set up Database.
    :return: a generator which yields a DatabaseClient instance
    """
    database: DatabaseClient
    with DatabaseClient(file_path="") as database:
        yield database
