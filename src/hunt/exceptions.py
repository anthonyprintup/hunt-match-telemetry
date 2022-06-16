class Error(Exception):
    """Generic error exceptions."""


class UnsupportedPlatformError(Error):
    """Raised when the platform isn't supported."""


class ParserError(Error):
    """Parser-related exceptions."""


class SteamworksError(Error):
    """Steamworks API-related exceptions."""
