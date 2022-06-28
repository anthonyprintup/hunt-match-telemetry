from colorama import Fore, Style

from .constants import MMR_RANGES, STAR_SYMBOL


def format_mmr(mmr: int) -> str:
    """
    Formats an MMR score to a nice string.
    :param mmr: an MMR score
    :return: a color-formatted string
    """
    stars: int = len(MMR_RANGES) - len([mmr_range for mmr_range in MMR_RANGES if mmr < mmr_range])
    return f"{Fore.BLUE}{mmr}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{STAR_SYMBOL * stars}{Style.RESET_ALL}"
