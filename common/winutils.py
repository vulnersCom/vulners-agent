import winreg
import re
import pythoncom
import win32com.client
import ctypes
import wmi
from common.stringops import remove_non_ascii


def get_windows_data():
    key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"

    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as key:
        releaseId = int(winreg.QueryValueEx(key, "ReleaseID")[0])
        installation_type = str(winreg.QueryValueEx(key, "InstallationType")[0])
        edition = str(winreg.QueryValueEx(key, "EditionID")[0])

    class OSVersionInfo(ctypes.Structure):
        _fields_ = [
            ("dwOSVersionInfoSize", ctypes.c_int),
            ("dwMajorVersion", ctypes.c_int),
            ("dwMinorVersion", ctypes.c_int),
            ("dwBuildNumber", ctypes.c_int),
            ("dwPlatformId", ctypes.c_int),
            ("szCSDVersion", ctypes.c_char * 128)]

    GetVersionEx = getattr(ctypes.windll.kernel32, "GetVersionExA")
    version = OSVersionInfo()
    version.dwOSVersionInfoSize = ctypes.sizeof(OSVersionInfo)
    GetVersionEx(ctypes.byref(version))

    pythoncom.CoInitialize()
    c = wmi.WMI()
    os = c.Win32_OperatingSystem()[0]

    return {
        "build": version.dwBuildNumber,
        "major": version.dwMajorVersion,
        "minor": version.dwMinorVersion,
        "platform": version.dwPlatformId,
        "release": releaseId,
        "name": remove_non_ascii(os.Caption),
        "version": os.Version,
        "type": installation_type,
        "edition": edition,
    }


def get_windows_updates():
    # Search installed/not installed Software Windows Updates
    wua = win32com.client.Dispatch("Microsoft.Update.Session")
    update_seeker = wua.CreateUpdateSearcher()
    installed_updates_search = update_seeker.Search("IsInstalled=1 and Type='Software'")
    missing_updates_search = update_seeker.Search("IsInstalled=0 and Type='Software'")
    _ = win32com.client.Dispatch("Microsoft.Update.UpdateColl")
    # compiles the regex pattern for finding Windows Update codes
    updates_pattern = re.compile("KB*\d+")
    missing_kbs = set()
    installed_kbs = set()
    missing_updates = set()
    installed_updates = set()

    for update in missing_updates_search.Updates:
        missing_updates.add(update.Identity.UpdateID)
        update_str = str(update)
        # extracts Windows Update code using regex
        update_code = updates_pattern.findall(update_str)
        missing_kbs = missing_kbs.union(update_code)
    for update in installed_updates_search.Updates:
        installed_updates.add(update.Identity.UpdateID)
        update_str = str(update)
        # extracts Windows Update code using regex
        update_code = updates_pattern.findall(update_str)
        installed_kbs = installed_kbs.union(update_code)

    return list(missing_kbs), \
           list(missing_updates), \
           list(installed_kbs), \
           list(installed_updates)


def enumerate_register_subkeys(key):
    i = 0
    while True:
        try:
            subkey = winreg.EnumKey(key, i)
            yield subkey
            i += 1
        except WindowsError:
            break


def get_register_key_values(key):
    key_dict = {}
    i = 0
    while True:
        try:
            subvalue = winreg.EnumValue(key, i)
        except WindowsError:
            break
        key_dict[subvalue[0]] = subvalue[1:]
        i += 1
    return key_dict


def traverse_registry_tree(hkey, keypath, reg_dict):

    key = winreg.OpenKey(hkey, keypath, 0, winreg.KEY_READ)
    reg_dict[keypath] = get_register_key_values(key)
    for subkey in enumerate_register_subkeys(key):
        subkeypath = "%s\\%s" % (keypath, subkey)
        traverse_registry_tree(hkey, subkeypath, reg_dict)
    return reg_dict


def get_windows_installed_software():
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    reg_dict = {}
    software_enumeration = {}
    for path in registry_paths:
        traverse_registry_tree(winreg.HKEY_LOCAL_MACHINE, path, reg_dict)
    for software_data in reg_dict.values():
        if "DisplayName" in software_data and "DisplayVersion" in software_data:
            software_enumeration[software_data["DisplayName"][0].strip()] = software_data["DisplayVersion"][0]

    return software_enumeration
