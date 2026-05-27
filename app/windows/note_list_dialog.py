from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QWidget, QTabWidget, QToolButton,
    QLineEdit, QInputDialog, QMessageBox,
)


class NoteListItem(QFrame):
    open_clicked = Signal(str)
    delete_clicked = Signal(str)
    rename_clicked = Signal(str)

    def __init__(self, note_id: str, title: str, mode: str, is_open: bool, parent=None):
        super().__init__(parent)
        self._note_id = note_id
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            NoteListItem {
                background: rgba(255,255,255,0.7);
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 2px 0;
            }
            NoteListItem:hover {
                background: rgba(255,255,255,0.9);
                border-color: #bbb;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 6, 6)
        layout.setSpacing(8)

        mode_icons = {"normal": "📝", "todo": "☑", "timeline": "🕐"}
        icon_label = QLabel(mode_icons.get(mode, "📝"))
        icon_label.setFixedWidth(20)
        layout.addWidget(icon_label)

        display_title = title if title and title != "新便签" else f"未命名便签"
        self._title_label = QLabel(display_title)
        self._title_label.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(self._title_label, 1)

        if is_open:
            status = QLabel("已打开")
            status.setStyleSheet("color: #4caf50; font-size: 11px;")
            layout.addWidget(status)

        rename_btn = QToolButton()
        rename_btn.setText("✏")
        rename_btn.setToolTip("重命名")
        rename_btn.setFixedSize(24, 24)
        rename_btn.setStyleSheet("""
            QToolButton { border: none; font-size: 12px; }
            QToolButton:hover { background: rgba(0,0,0,0.1); border-radius: 4px; }
        """)
        rename_btn.clicked.connect(lambda: self.rename_clicked.emit(self._note_id))
        layout.addWidget(rename_btn)

        open_btn = QPushButton("打开")
        open_btn.setFixedSize(48, 24)
        open_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        open_btn.clicked.connect(lambda: self.open_clicked.emit(self._note_id))
        layout.addWidget(open_btn)

        del_btn = QToolButton()
        del_btn.setText("🗑")
        del_btn.setToolTip("删除")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet("""
            QToolButton { border: none; font-size: 12px; }
            QToolButton:hover { background: rgba(231,76,60,0.2); border-radius: 4px; }
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._note_id))
        layout.addWidget(del_btn)

    def set_title(self, title: str):
        self._title_label.setText(title)


class NoteListDialog(QDialog):
    open_note = Signal(str)
    delete_note = Signal(str)
    create_note_signal = Signal(str)

    def __init__(self, db, settings, open_windows: dict, parent=None):
        super().__init__(parent)
        self._db = db
        self._settings = settings
        self._open_windows = open_windows
        self.setWindowTitle("便签列表")
        self.setMinimumSize(400, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._tabs.addTab(self._build_tab("normal"), "📝 普通")
        self._tabs.addTab(self._build_tab("todo"), "☑ 待办")
        self._tabs.addTab(self._build_tab("timeline"), "🕐 时间线")

    def _build_tab(self, mode: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QHBoxLayout()
        mode_names = {"normal": "普通便签", "todo": "待办便签", "timeline": "时间线便签"}
        title_label = QLabel(mode_names.get(mode, ""))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        header.addWidget(title_label)
        header.addStretch()

        create_btn = QPushButton("+ 新建")
        create_btn.setStyleSheet("""
            QPushButton {
                background: #4caf50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background: #43a047; }
        """)
        create_btn.clicked.connect(lambda m=mode: self._on_create(m))
        header.addWidget(create_btn)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(4)

        notes = self._db.list_notes()
        mode_notes = [n for n in notes if n.mode == mode]

        if not mode_notes:
            empty_label = QLabel("暂无便签，点击上方 + 新建 创建")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #999; font-size: 12px; padding: 20px;")
            list_layout.addWidget(empty_label)
        else:
            for note in mode_notes:
                is_open = note.id in self._open_windows
                item = NoteListItem(note.id, note.title, note.mode, is_open)
                item.open_clicked.connect(self._on_open)
                item.delete_clicked.connect(self._on_delete)
                item.rename_clicked.connect(self._on_rename)
                list_layout.addWidget(item)

        list_layout.addStretch()
        scroll.setWidget(list_widget)
        layout.addWidget(scroll, 1)

        return tab

    def _on_create(self, mode: str):
        title, ok = QInputDialog.getText(self, "新建便签", "便签标题（可留空）：")
        if ok:
            self.create_note_signal.emit(mode)
            if title.strip():
                notes = self._db.list_notes()
                if notes:
                    latest = notes[-1]
                    self._db.update_note(latest.id, title=title.strip())
            self._refresh()

    def _on_open(self, note_id: str):
        self.open_note.emit(note_id)
        self.accept()

    def _on_delete(self, note_id: str):
        reply = QMessageBox.question(
            self, "删除便签", "确定要删除这个便签吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_note.emit(note_id)
            self._refresh()

    def _on_rename(self, note_id: str):
        note = self._db.load_note(note_id)
        current = note.title if note else ""
        title, ok = QInputDialog.getText(self, "重命名便签", "新标题：", text=current)
        if ok and title.strip():
            self._db.update_note(note_id, title=title.strip())
            self._refresh()

    def _refresh(self):
        current_index = self._tabs.currentIndex()
        for i in range(self._tabs.count() - 1, -1, -1):
            self._tabs.removeTab(i)
        self._tabs.addTab(self._build_tab("normal"), "📝 普通")
        self._tabs.addTab(self._build_tab("todo"), "☑ 待办")
        self._tabs.addTab(self._build_tab("timeline"), "🕐 时间线")
        self._tabs.setCurrentIndex(current_index)
