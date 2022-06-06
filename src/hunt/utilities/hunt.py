from winreg import HKEYType, HKEY_LOCAL_MACHINE, OpenKey, QueryInfoKey, EnumKey, QueryValueEx
from colorama import Fore, Style

from ..constants import HUNT_SHOWDOWN_STEAM_ID, MMR_RANGES, STAR_SYMBOL


def find_hunt_attributes_path() -> str:
    """
    Locates the game's install path and appends the attributes file path to it.
    :return: A path to the attributes file
    :throws: RuntimeError if the attributes file cannot be found.
    """
    uninstall_key: HKEYType
    with OpenKey(key=HKEY_LOCAL_MACHINE,
                 sub_key=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as uninstall_key:
        sub_key_count: int
        [sub_key_count, _, _] = QueryInfoKey(uninstall_key)
        for i in range(sub_key_count):
            sub_key_name: str = EnumKey(uninstall_key, i)
            if sub_key_name == f"Steam App {HUNT_SHOWDOWN_STEAM_ID}":
                steam_app_key: HKEYType
                with OpenKey(key=uninstall_key, sub_key=sub_key_name) as steam_app_key:
                    install_location: str
                    [install_location, _] = QueryValueEx(steam_app_key, "InstallLocation")
                    return install_location + r"\user\profiles\default\attributes.xml"
    raise RuntimeError("Couldn't find the attributes file.")


def format_mmr(mmr: int) -> str:
    """
    Formats an MMR score to a nice string.
    :param mmr: an MMR score
    :return: a color-formatted string
    """
    stars: int = len(MMR_RANGES) - len([mmr_range for mmr_range in MMR_RANGES if mmr < mmr_range])
    return f"{Fore.BLUE}{mmr}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{STAR_SYMBOL * stars}{Style.RESET_ALL}"
