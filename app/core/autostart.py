import sys
import winreg


_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
_NAME = "DesktopNote"


def is_auto_start() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY, 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, _NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def set_auto_start(enable: bool):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY, 0, winreg.KEY_SET_VALUE)
    if enable:
        exe_path = sys.executable if getattr(sys, "frozen", False) else f'"{sys.executable}" "{_main_script()}"'
        winreg.SetValueEx(key, _NAME, 0, winreg.REG_SZ, exe_path)
    else:
        try:
            winreg.DeleteValue(key, _NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)


def _main_script() -> str:
    import os
    return os.path.abspath(sys.argv[0])
