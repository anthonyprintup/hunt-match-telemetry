from __future__ import annotations

from enum import IntEnum, auto as _enum_auto


# noinspection PyArgumentList
class ExitCode(IntEnum):
    # No errors occurred
    SUCCESS: ExitCode = 0
    # Steamworks API related error
    STEAMWORKS_ERROR: ExitCode = _enum_auto()
    # Unsupported platform
    UNSUPPORTED_PLATFORM: ExitCode = _enum_auto()
