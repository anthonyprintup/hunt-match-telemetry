from hunt.attributes.player import Player


def test_player_format_name(mocked_player: Player, expected_name_prefix: str) -> None:
    """
    Test Player.format_name by comparing against the expected results.
    :param mocked_player: a mocked Player instance
    :param expected_name_prefix: the expected name prefix
    """
    assert mocked_player.format_name() == expected_name_prefix
    assert mocked_player.format_name(is_local_player=True) == f"{expected_name_prefix} (you)"


def test_player_format_kills(mocked_player: Player, expected_name_prefix: str) -> None:
    """
    Test Player.format_kills by comparing against the expected results.
    :param mocked_player: a mocked Player instance
    :param expected_name_prefix: the expected name prefix
    """
    kills: int = mocked_player.downed_by_me + mocked_player.killed_by_me
    kill_count: str = f" {kills}x" if kills > 1 else ""
    assert mocked_player.format_kills() == f"Killed {expected_name_prefix}{kill_count}"


def test_player_format_deaths(mocked_player: Player, expected_name_prefix: str) -> None:
    """
    Test Player.format_deaths by comparing against the expected results.
    :param mocked_player: a mocked Player instance
    :param expected_name_prefix: the expected name prefix
    """
    deaths: int = mocked_player.downed_me + mocked_player.killed_me
    death_count: str = f" {deaths}x" if deaths > 1 else ""
    assert mocked_player.format_deaths() == f"Died to {expected_name_prefix}{death_count}"
