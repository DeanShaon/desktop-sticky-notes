import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.models.settings import Settings
from app.models.database import Database
from app.windows.note_manager import NoteManager

if getattr(sys, "frozen", False):
    _APP_DIR = Path(sys.executable).resolve().parent
else:
    _APP_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = _APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_data_dir(settings: "Settings" = None) -> Path:
    if settings:
        custom = settings.get("advanced", "data_dir")
        d = Path(custom) if custom else DATA_DIR
    else:
        d = DATA_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def run():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setFont(QFont("Microsoft YaHei", 10))

    settings = Settings(DATA_DIR / "settings.json")
    Settings._instance = settings
    data_dir = get_data_dir(settings)
    db = Database(data_dir / "notes.db")

    manager = NoteManager(db, settings)
    manager.restore_notes()

    sys.exit(app.exec())
