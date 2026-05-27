from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QObject, Qt

from app.windows.note_window import NoteWindow


class NoteManager(QObject):
    def __init__(self, db, settings):
        super().__init__()
        self._db = db
        self._settings = settings
        self._window = None
        self._setup_tray()

    def _setup_tray(self):
        self._tray = QSystemTrayIcon()
        self._tray.setToolTip("桌面便签")

        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#FFF9C4"))
        painter.setPen(QColor("#FBC02D"))
        painter.drawRoundedRect(4, 4, 24, 24, 4, 4)
        painter.end()
        self._tray.setIcon(QIcon(pixmap))

        menu = QMenu()

        act_show = menu.addAction("显示便签")
        act_show.triggered.connect(self._show_window)

        act_settings = menu.addAction("设置")
        act_settings.triggered.connect(self._open_settings)

        menu.addSeparator()

        act_quit = menu.addAction("退出")
        act_quit.triggered.connect(self._quit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _ensure_window(self):
        if self._window is None:
            notes = self._db.list_notes()
            if notes:
                note_id = notes[0].id
            else:
                color = self._settings.get("appearance", "default_color") or "#FFF9C4"
                note_id = self._db.create_note("normal", color)
            self._window = NoteWindow(note_id, self._db, self._settings)
            self._window.closed.connect(self._on_window_closed)
            self._window.minimize_to_tray.connect(self._on_minimize_to_tray)
            self._window.quit_app.connect(self._quit)

    def restore_notes(self):
        self._ensure_window()
        self._window.show()

    def _show_window(self):
        self._ensure_window()
        self._window.showNormal()
        self._window.activateWindow()

    def _open_settings(self):
        from app.windows.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._settings, None)
        dlg.settings_changed.connect(self._apply_settings)
        dlg.exec()

    def _apply_settings(self):
        if self._window:
            self._window.apply_settings()

    def _on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self._show_window()

    def _on_window_closed(self):
        if self._window:
            self._window.save_current()
        self._window = None

    def _on_minimize_to_tray(self):
        if self._window:
            self._window.hide()

    def _quit(self):
        if self._window:
            self._window.save_current()
        self._db.close()
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
