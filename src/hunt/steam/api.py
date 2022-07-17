from __future__ import annotations

import ctypes
import os
import sys
from ctypes import Array, CDLL, cdll
from zipfile import ZipFile

from .type_aliases import AppId_t, char, char_pointer, uint32, void_pointer
from ..constants import STEAMWORKS_BINARIES_PATH, STEAMWORKS_SDK_PATH
from ..exceptions import SteamworksError, UnsupportedPlatformError


class SteamworksApi:
    _api: CDLL

    def __init__(self, api_binary_path: str):
        """
        Loads the Steamworks API binary.
        :param api_binary_path: the path to the API binary
        """
        self._api = cdll.LoadLibrary(name=api_binary_path)

    def setup_types(self) -> None:
        """Sets up native function types."""
        # SteamAPI
        self._api.SteamAPI_Init.restype = ctypes.c_bool

        # SteamApps
        self._api.SteamAPI_SteamApps_v008.restype = void_pointer
        self._api.SteamAPI_ISteamApps_GetAppInstallDir.restype = uint32
        self._api.SteamAPI_ISteamApps_GetAppInstallDir.argtypes = (void_pointer, AppId_t, char_pointer, uint32)

        # SteamFriends
        self._api.SteamAPI_SteamFriends_v017.restype = void_pointer
        self._api.SteamAPI_ISteamFriends_GetPersonaName.restype = char_pointer
        self._api.SteamAPI_ISteamFriends_GetPersonaName.argtypes = (void_pointer,)

    def init(self) -> None:
        """
        Invoke SteamAPI_Init.
        :raises SteamworksError: if initialization failed
        """
        if not self._api.SteamAPI_Init():
            raise SteamworksError("SteamAPI initialization failed.")

    def _steam_apps(self) -> void_pointer:
        """
        Returns a pointer to the ISteamApps interface.
        :return: a pointer to ISteamApps
        :raises SteamworksError: if the API returned a null pointer
        """
        steam_apps: void_pointer = self._api.SteamAPI_SteamApps_v008()
        if not steam_apps:
            raise SteamworksError("The pointer to ISteamApps was null.")
        return steam_apps

    def _steam_friends(self) -> void_pointer:
        """
        Returns a pointer to the ISteamFriends interface.
        :return: a pointer to ISteamFriends
        :raises SteamworksError: if the API returned a null pointer
        """
        steam_friends: void_pointer = self._api.SteamAPI_SteamFriends_v017()
        if not steam_friends:
            raise SteamworksError("The pointer to ISteamFriends was null.")
        return steam_friends

    def get_install_directory(self, app_id: int) -> str:
        """
        Gets the installation path of the app id.
        :param app_id: the app id of the game
        :return: a path to the app directory
        :raises SteamworksError: if the installation path returned was empty
        :raises SteamworksError: if the API returned a null pointer (SteamworksApi._steam_apps)
        """
        # Get the ISteamApps pointer
        steam_apps: void_pointer = self._steam_apps()

        # Allocate a path buffer
        max_path_size: int = 260  # ctypes.wintypes.MAX_PATH
        install_directory_buffer: Array[char] = ctypes.create_string_buffer(max_path_size)

        # Invoke SteamAPI_ISteamApps_GetAppInstallDir
        bytes_written: uint32 = self._api.SteamAPI_ISteamApps_GetAppInstallDir(
            steam_apps,
            AppId_t(app_id),
            install_directory_buffer,
            len(install_directory_buffer))
        if not bytes_written:
            raise SteamworksError("ISteamApps::GetAppInstallDir returned zero bytes.")

        # Strip the trailing null bytes and return the installation path
        return install_directory_buffer.raw.rstrip(b"\x00").decode()

    def get_persona_name(self) -> str:
        """
        Gets the user's persona (display) name.
        :return: the user's display name
        """
        # Get the ISteamFriends pointer
        steam_friends: void_pointer = self._steam_friends()

        # Invoke SteamAPI_ISteamFriends_GetPersonaName
        persona_name: bytes = self._api.SteamAPI_ISteamFriends_GetPersonaName(steam_friends)
        return persona_name.decode()

    def shutdown(self) -> None:
        """Invoke SteamAPI_Shutdown."""
        self._api.SteamAPI_Shutdown()

    @staticmethod
    def prepare_and_initialize(api_binary_path: str, app_id: int) -> SteamworksApi:
        """
        This function will set up everything required to use the Steamworks API.
        :param api_binary_path: the path of the API binary
        :param app_id: the app id of the game
        :return: a new SteamworksApi instance
        :raises SteamworksError: if initialization failed (SteamworksApi.init)
        """
        # Setup the SteamAppId environment variable:
        #   the Steam API will attempt to resolve this
        #   environment variable because "steam_appid.txt"
        #   doesn't exist in the working directory.
        os.environ["SteamAppId"] = f"{app_id}"

        # Initialize the api
        api: SteamworksApi = SteamworksApi(api_binary_path=api_binary_path)
        api.setup_types()

        try:
            # Wrap SteamworksApi.init to guarantee that SteamAPI_Shutdown is invoked
            api.init()
        except SteamworksError:
            # Cleanup/shutdown the Steamworks API
            api.shutdown()
            raise

        # Return the api instance
        return api


def generate_api_binary_path() -> str:
    """
    Generates a path to the Steamworks API binary depending on the platform.
    :return: a path to the Steamworks API binary
    :raises UnsupportedPlatformError: if the current platform isn't supported
    """
    file_name: str
    bits: str = "64" if ctypes.sizeof(void_pointer) == 8 else ""
    match sys.platform:
        case "linux":
            file_name = f"libsteam_api{bits}.so"
        case "win32" | "cygwin":
            file_name = f"steam_api{bits}.dll"
        case "darwin":
            file_name = f"libsteam_api{bits}.dylib"
        case _:
            raise UnsupportedPlatformError(f"Unsupported platform: {sys.platform}")

    return os.path.join(STEAMWORKS_BINARIES_PATH, file_name)


def try_extract_steamworks_binaries() -> str:
    """
    Downloads the Steamworks SDK and extracts the API binary to the API path.
    :return: a path to the Steamworks API binary
    :raises SteamworksError: if the Steamworks SDK is missing from disk at STEAMWORKS_SDK_PATH
    :raises UnsupportedPlatformError: if the current platform isn't supported (generate_api_binary_path)
    """
    # Check if the binary has already been downloaded
    expected_api_binary_path: str = generate_api_binary_path()
    if os.path.exists(expected_api_binary_path):
        return expected_api_binary_path

    if not os.path.exists(STEAMWORKS_SDK_PATH):
        raise SteamworksError("Missing the Steamworks SDK.")

    # Extract the correct binary to the disk
    with ZipFile(file=STEAMWORKS_SDK_PATH) as zip_file:
        # Generate the binary file path
        file_name: str
        match (sys.platform, ctypes.sizeof(void_pointer) * 8):
            case ("linux", 32):
                file_name = "sdk/redistributable_bin/linux32/libsteam_api.so"
            case ("linux", 64):
                file_name = "sdk/redistributable_bin/linux64/libsteam_api.so"
            case ("win32" | "cygwin", 32):
                file_name = "sdk/redistributable_bin/steam_api.dll"
            case ("win32" | "cygwin", 64):
                file_name = "sdk/redistributable_bin/win64/steam_api64.dll"
            case ("darwin", 64):
                file_name = "sdk/redistributable_bin/osx/libsteam_api.dylib"
            case _:
                raise UnsupportedPlatformError(f"Unsupported platform: {sys.platform}")

        # Open the binary file and write it to disk
        with zip_file.open(name=file_name) as zip_binary_file:
            with open(expected_api_binary_path, mode="wb") as disk_binary_file:
                disk_binary_file.write(zip_binary_file.read())

    # Return the Steamworks API binary path
    return expected_api_binary_path


def fetch_hunt_attributes_path(steamworks_api: SteamworksApi, app_id: int) -> str:
    """
    Locates the game's install path and appends the attributes file path to it.
    :param steamworks_api: a Steamworks API instance
    :param app_id: the app id of the game
    :return: A path to the attributes file
    """
    install_directory: str = steamworks_api.get_install_directory(app_id=app_id)
    return install_directory + r"\user\profiles\default\attributes.xml"
