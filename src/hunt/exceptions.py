class Error(Exception):
    """Generic error exception."""


class ParserError(Error):
    """Parser-related exception."""


class SteamworksError(Error):
    """Steamworks API-related exception."""
