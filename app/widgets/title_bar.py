from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QLineEdit


class TitleBar(QWidget):
    close_clicked = Signal()
    pin_clicked = Signal()
    mode_changed = Signal(str)
    settings_clicked = Signal()
    drag_finished = Signal()
    drag_started = Signal()
    new_note_clicked = Signal(str)
    title_changed = Signal(str)
    sidebar_toggle_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(62)
        self._drag_pos = None
        self._dragging = False
        self._current_mode = "normal"
        self._editing_title = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 2, 6, 2)
        main_layout.setSpacing(2)

        top_row = QHBoxLayout()
        top_row.setSpacing(2)

        top_row.addStretch()

        self._mode_normal = QToolButton()
        self._mode_normal.setText("📝")
        self._mode_normal.setToolTip("普通模式")
        self._mode_normal.setFixedSize(26, 26)
        self._mode_normal.clicked.connect(lambda: self.mode_changed.emit("normal"))
        top_row.addWidget(self._mode_normal)

        self._mode_todo = QToolButton()
        self._mode_todo.setText("☑")
        self._mode_todo.setToolTip("待办模式")
        self._mode_todo.setFixedSize(26, 26)
        self._mode_todo.clicked.connect(lambda: self.mode_changed.emit("todo"))
        top_row.addWidget(self._mode_todo)

        self._mode_timeline = QToolButton()
        self._mode_timeline.setText("🕐")
        self._mode_timeline.setToolTip("时间线模式")
        self._mode_timeline.setFixedSize(26, 26)
        self._mode_timeline.clicked.connect(lambda: self.mode_changed.emit("timeline"))
        top_row.addWidget(self._mode_timeline)

        self._pin_btn = QToolButton()
        self._pin_btn.setText("📌")
        self._pin_btn.setToolTip("置顶")
        self._pin_btn.setFixedSize(26, 26)
        self._pin_btn.setCheckable(True)
        self._pin_btn.clicked.connect(self.pin_clicked.emit)
        top_row.addWidget(self._pin_btn)

        self._settings_btn = QToolButton()
        self._settings_btn.setText("⚙")
        self._settings_btn.setToolTip("设置")
        self._settings_btn.setFixedSize(26, 26)
        self._settings_btn.clicked.connect(self.settings_clicked.emit)
        top_row.addWidget(self._settings_btn)

        self._min_btn = QToolButton()
        self._min_btn.setText("━")
        self._min_btn.setToolTip("最小化")
        self._min_btn.setFixedSize(26, 26)
        self._min_btn.clicked.connect(self._on_minimize)
        top_row.addWidget(self._min_btn)

        self._close_btn = QToolButton()
        self._close_btn.setText("×")
        self._close_btn.setToolTip("关闭")
        self._close_btn.setFixedSize(26, 26)
        self._close_btn.clicked.connect(self.close_clicked.emit)
        top_row.addWidget(self._close_btn)

        main_layout.addLayout(top_row)

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(2, 0, 0, 0)
        bottom_row.setSpacing(4)

        self._title_label = QLabel("未命名")
        self._title_label.setStyleSheet("""
            font-weight: bold; font-size: 13px; color: #444;
            padding: 3px 6px; border-radius: 4px;
        """)
        self._title_label.mouseDoubleClickEvent = self._on_title_double_click
        bottom_row.addWidget(self._title_label)

        self._title_edit = QLineEdit()
        self._title_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 13px;
                font-weight: bold;
                background: rgba(255,255,255,0.9);
            }
        """)
        self._title_edit.hide()
        self._title_edit.returnPressed.connect(self._finish_title_edit)
        bottom_row.addWidget(self._title_edit)

        bottom_row.addStretch()

        self._new_btn = QToolButton()
        self._new_btn.setText("+")
        self._new_btn.setToolTip("新建同类便签")
        self._new_btn.setFixedSize(32, 28)
        self._new_btn.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
                padding: 2px;
            }
            QToolButton:hover { background: rgba(0, 0, 0, 0.1); }
            QToolButton:pressed { background: rgba(0, 0, 0, 0.2); }
        """)
        self._new_btn.clicked.connect(self._on_new_note)
        bottom_row.addWidget(self._new_btn)

        self._sidebar_btn = QToolButton()
        self._sidebar_btn.setText("☰")
        self._sidebar_btn.setToolTip("便签列表")
        self._sidebar_btn.setFixedSize(28, 28)
        self._sidebar_btn.clicked.connect(self.sidebar_toggle_clicked.emit)
        bottom_row.addWidget(self._sidebar_btn)

        main_layout.addLayout(bottom_row)

        self._apply_button_style()

    def _apply_button_style(self):
        style = """
            QToolButton {
                border: none;
                border-radius: 4px;
                font-size: 14px;
                padding: 2px;
            }
            QToolButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
            QToolButton:pressed {
                background: rgba(0, 0, 0, 0.2);
            }
        """
        for btn in [
            self._mode_normal, self._mode_todo, self._mode_timeline,
            self._sidebar_btn, self._pin_btn,
            self._settings_btn, self._min_btn,
        ]:
            btn.setStyleSheet(style)

        self._close_btn.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 2px;
            }
            QToolButton:hover {
                background: #e74c3c;
                color: white;
            }
            QToolButton:pressed {
                background: #c0392b;
                color: white;
            }
        """)

    def set_title(self, title: str):
        display = title if title and title != "新便签" else "未命名"
        self._title_label.setText(display)

    def set_active_mode(self, mode: str):
        self._current_mode = mode
        style_active = """
            QToolButton {
                background: rgba(0,0,0,0.12);
                border: none;
                border-radius: 4px;
                font-size: 14px;
                padding: 2px;
            }
            QToolButton:hover { background: rgba(0,0,0,0.18); }
        """
        style_normal = """
            QToolButton {
                border: none;
                border-radius: 4px;
                font-size: 14px;
                padding: 2px;
            }
            QToolButton:hover { background: rgba(0, 0, 0, 0.1); }
            QToolButton:pressed { background: rgba(0, 0, 0, 0.2); }
        """
        for btn, m in [
            (self._mode_normal, "normal"),
            (self._mode_todo, "todo"),
            (self._mode_timeline, "timeline"),
        ]:
            btn.setStyleSheet(style_active if m == mode else style_normal)

    def set_pinned(self, pinned: bool):
        self._pin_btn.setChecked(pinned)
        if pinned:
            self._pin_btn.setStyleSheet("""
                QToolButton {
                    border: 1px solid #bbb;
                    border-radius: 4px;
                    font-size: 14px;
                    padding: 1px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e0e0e0, stop:1 #c8c8c8);
                }
                QToolButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d5d5d5, stop:1 #bebebe);
                }
            """)
        else:
            self._pin_btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    padding: 2px;
                }
                QToolButton:hover {
                    background: rgba(0, 0, 0, 0.1);
                }
            """)

    def _on_title_double_click(self, event):
        self._editing_title = True
        from PySide6.QtWidgets import QApplication
        QApplication.instance().installEventFilter(self)
        self._title_label.hide()
        self._title_edit.setText(self._title_label.text())
        self._title_edit.show()
        self._title_edit.setFocus()
        self._title_edit.selectAll()

    def _finish_title_edit(self):
        if not self._editing_title:
            return
        self._editing_title = False
        from PySide6.QtWidgets import QApplication
        QApplication.instance().removeEventFilter(self)
        new_title = self._title_edit.text().strip()
        if new_title:
            self._title_label.setText(new_title)
            self.title_changed.emit(new_title)
        self._title_edit.hide()
        self._title_label.show()

    def eventFilter(self, obj, event):
        if self._editing_title and event.type() == event.Type.MouseButtonPress:
            gpos = event.globalPosition().toPoint()
            local = self.mapFromGlobal(gpos)
            if not self._title_edit.geometry().contains(local):
                self._finish_title_edit()
                return True
        return False

    def _on_minimize(self):
        window = self.window()
        if window:
            window.showMinimized()

    def _on_new_note(self):
        self.new_note_clicked.emit(self._current_mode)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().pos()
            self._dragging = False

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            if not self._dragging:
                self._dragging = True
                self.drag_started.emit()
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            from app.core.screen_utils import screen_at, available_geometry
            geo = available_geometry(screen_at(new_pos))
            w = self.window()
            x = max(geo.left(), min(new_pos.x(), geo.right() - w.width()))
            y = max(geo.top(), min(new_pos.y(), geo.bottom() - w.height()))
            w.move(x, y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._dragging:
                self.drag_finished.emit()
            self._drag_pos = None
            self._dragging = False
