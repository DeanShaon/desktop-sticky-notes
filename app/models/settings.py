import json
from pathlib import Path

_DEFAULTS = {
    "appearance": {
        "theme": "light",
        "default_color": "#FFF9C4",
        "font_family": "Microsoft YaHei",
        "font_size": 10,
        "opacity": 0.95,
        "corner_radius": 8,
    },
    "behavior": {
        "auto_start": False,
        "dock_threshold": 20,
        "strip_width": 6,
        "hide_delay": 400,
        "show_delay": 150,
        "minimize_to_tray": True,
    },
    "advanced": {
        "auto_save_interval": 500,
        "data_dir": "",
    },
}


class Settings:
    _instance = None

    def __init__(self, path: Path):
        self._path = path
        self._data = dict(_DEFAULTS)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self._merge(saved)
        self.save()

    @classmethod
    def instance(cls):
        return cls._instance

    def _merge(self, saved: dict):
        for section, values in saved.items():
            if section in self._data and isinstance(values, dict):
                self._data[section].update(values)

    def get(self, section: str, key: str):
        return self._data.get(section, {}).get(key)

    def set(self, section: str, key: str, value):
        if section not in self._data:
            self._data[section] = {}
        self._data[section][key] = value
        self.save()

    def section(self, name: str) -> dict:
        return dict(self._data.get(name, {}))

    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
