from __future__ import annotations

from enum import IntEnum, auto as _enum_auto


class ExitCode(IntEnum):
    # No errors occurred
    SUCCESS: ExitCode = 0  # type: ignore[assignment]
    # Filesystem error
    FILESYSTEM_ERROR: ExitCode = _enum_auto()  # type: ignore[assignment]
    # Steamworks API related error
    STEAMWORKS_ERROR: ExitCode = _enum_auto()  # type: ignore[assignment]
    # Unsupported platform
    UNSUPPORTED_PLATFORM: ExitCode = _enum_auto()  # type: ignore[assignment]
