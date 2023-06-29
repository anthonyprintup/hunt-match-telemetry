import json
from pathlib import Path

from hunt.attributes.match import DatabaseClient, Match
from .conftest import MAGIC_FILE_PATH, MagicMock, datetime


def test_match_generate_file_path(expected_match: Match, static_time: datetime, expected_file_path: Path) -> None:
    """
    Test Match.generate_file_path by comparing the generated file path to the expected file path.
    :param expected_match: a Match instance
    :param static_time: a static datetime value
    :param expected_file_path: the expected file path
    """
    assert expected_match.generate_file_path(time=static_time) == expected_file_path
    assert expected_match.generate_file_path() != expected_file_path


def test_match_try_save_to_file(io_safe_match: Match, database_client: DatabaseClient, mock_open: MagicMock) -> None:
    """
    Test Match.try_save_to_file using wrapped Match instance to prevent filesystem access.
    :param io_safe_match: an IO safe Match instance
    :param database_client: a Database instance
    :param mock_open: the MagicMock instance used to patch builtins.open
    """
    # Invoke Match methods
    assert io_safe_match.generate_file_path() == MAGIC_FILE_PATH
    assert not io_safe_match.try_save_to_file(database=database_client)  # hash doesn't exist, inserted match data
    assert io_safe_match.try_save_to_file(database=database_client)  # hash already exists

    # Assertions
    match_data: str = json.dumps(io_safe_match, indent=2, default=vars)
    mock_open.assert_called_once_with(MAGIC_FILE_PATH, mode="w")  # assert open(MAGIC_FILE_PATH, mode="w") invoked

    mock_open_handle: MagicMock = mock_open()
    mock_open_handle.write.assert_called_once_with(match_data)  # assert file.write(match_data) invoked
