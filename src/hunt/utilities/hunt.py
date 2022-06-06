from winreg import HKEYType, HKEY_LOCAL_MACHINE, OpenKey, QueryInfoKey, EnumKey, QueryValueEx
from ..constants import HUNT_SHOWDOWN_STEAM_ID


def find_hunt_attributes_path() -> str:
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
    return ""
