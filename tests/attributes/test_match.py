from datetime import datetime

from hunt.attributes.match import Match


def test_match_generate_file_path(expected_match: Match, static_time: datetime, expected_file_path: str) -> None:
    """
    Test Match.generate_file_path by comparing the generated file path to the expected file path.
    :param expected_match: a Match instance
    :param static_time: a static datetime value
    :param expected_file_path: the expected file path
    """
    assert expected_match.generate_file_path(time=static_time) == expected_file_path
    assert expected_match.generate_file_path() != expected_file_path
