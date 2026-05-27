from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit


class NormalWidget(QWidget):
    def __init__(self, note_id: str, db, settings=None, parent=None):
        super().__init__(parent)
        self._note_id = note_id
        self._db = db

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._editor = QPlainTextEdit()
        self._editor.setPlainText(db.load_normal_content(note_id))
        self._editor.setPlaceholderText("在这里写点什么...")
        self._editor.setStyleSheet("""
            QPlainTextEdit {
                background: transparent;
                border: none;
                font-size: 13px;
                line-height: 1.5;
                color: #333;
                selection-background-color: rgba(66, 133, 244, 0.3);
            }
        """)
        layout.addWidget(self._editor)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        interval = 500
        if settings:
            interval = settings.get("advanced", "auto_save_interval") or 500
        self._save_timer.setInterval(interval)
        self._save_timer.timeout.connect(self._save)

        self._editor.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        self._save_timer.start()

    def _save(self):
        self._db.save_normal_content(self._note_id, self._editor.toPlainText())

    def save(self):
        self._save_timer.stop()
        self._save()
