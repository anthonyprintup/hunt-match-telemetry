from winreg import HKEYType, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, OpenKey, QueryValueEx
from colorama import Fore, Style

from ..constants import HUNT_SHOWDOWN_STEAM_ID, MMR_RANGES, STAR_SYMBOL


def fetch_hunt_attributes_path() -> str:
    """
    Locates the game's install path and appends the attributes file path to it.
    :return: A path to the attributes file
    :throws: RuntimeError if the attributes file cannot be found.
    """
    registry_location: str = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App {HUNT_SHOWDOWN_STEAM_ID}"
    try:
        steam_app_key: HKEYType
        with OpenKey(key=HKEY_LOCAL_MACHINE, sub_key=registry_location) as steam_app_key:
            install_location: str
            [install_location, _] = QueryValueEx(steam_app_key, "InstallLocation")
            return install_location + r"\user\profiles\default\attributes.xml"
    except FileNotFoundError:
        raise RuntimeError("Couldn't find the attributes file.")


def fetch_steam_username() -> str:
    """
    Gets the user's Steam username.
    :return: The last game username used by Steam.
    :throws: RuntimeError if the username cannot be located.
    """
    try:
        steam_key: HKEYType
        with OpenKey(key=HKEY_CURRENT_USER, sub_key=r"SOFTWARE\Valve\Steam") as steam_key:
            last_game_named_used: str
            [last_game_named_used, _] = QueryValueEx(steam_key, "LastGameNameUsed")
            return last_game_named_used
    except FileNotFoundError:
        raise RuntimeError("Failed to find Steam's last used username.")


def format_mmr(mmr: int) -> str:
    """
    Formats an MMR score to a nice string.
    :param mmr: an MMR score
    :return: a color-formatted string
    """
    stars: int = len(MMR_RANGES) - len([mmr_range for mmr_range in MMR_RANGES if mmr < mmr_range])
    return f"{Fore.BLUE}{mmr}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{STAR_SYMBOL * stars}{Style.RESET_ALL}"
