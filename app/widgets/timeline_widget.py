from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QFrame, QDateTimeEdit, QToolButton,
)


class TimelineEventWidget(QFrame):
    edit_requested = Signal(dict)
    delete_requested = Signal(str)

    def __init__(self, event: dict, parent=None):
        super().__init__(parent)
        self._event = event
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("TimelineEventWidget { padding: 2px 0; }")

        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 4, 2, 4)
        outer.setSpacing(0)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        time_str = event["event_time"]
        try:
            dt = datetime.fromisoformat(time_str)
            formatted = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            formatted = time_str

        self._time_label = QLabel(formatted)
        self._time_label.setStyleSheet("color: #1565C0; font-weight: bold; font-size: 11px;")
        content_layout.addWidget(self._time_label)

        self._title_label = QLabel(event["title"])
        self._title_label.setStyleSheet("font-size: 13px; color: #333; font-weight: 500;")
        content_layout.addWidget(self._title_label)

        if event.get("detail"):
            self._detail_label = QLabel(event["detail"])
            self._detail_label.setStyleSheet("color: #666; font-size: 11px;")
            self._detail_label.setWordWrap(True)
            content_layout.addWidget(self._detail_label)
        else:
            self._detail_label = None

        outer.addWidget(content, 1)

        btn_area = QWidget()
        btn_layout = QVBoxLayout(btn_area)
        btn_layout.setContentsMargins(2, 0, 2, 0)
        btn_layout.setSpacing(2)

        edit_btn = QToolButton()
        edit_btn.setText("✏")
        edit_btn.setToolTip("编辑")
        edit_btn.setFixedSize(20, 20)
        edit_btn.setStyleSheet("""
            QToolButton { border: none; font-size: 10px; color: #999; }
            QToolButton:hover { color: #1565C0; background: rgba(21,101,192,0.1); border-radius: 3px; }
        """)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._event))
        btn_layout.addWidget(edit_btn)

        del_btn = QToolButton()
        del_btn.setText("×")
        del_btn.setToolTip("删除")
        del_btn.setFixedSize(20, 20)
        del_btn.setStyleSheet("""
            QToolButton { border: none; font-size: 12px; font-weight: bold; color: #999; }
            QToolButton:hover { color: #e74c3c; background: rgba(231,76,60,0.1); border-radius: 3px; }
        """)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._event["id"]))
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()

        outer.addWidget(btn_area)

    @property
    def event_id(self):
        return self._event["id"]

    def update_event(self, event: dict):
        self._event = event
        self._title_label.setText(event["title"])
        try:
            dt = datetime.fromisoformat(event["event_time"])
            self._time_label.setText(dt.strftime("%Y-%m-%d %H:%M"))
        except (ValueError, TypeError):
            self._time_label.setText(event["event_time"])
        if self._detail_label:
            self._detail_label.setText(event.get("detail", ""))
        elif event.get("detail"):
            self._detail_label = QLabel(event["detail"])
            self._detail_label.setStyleSheet("color: #666; font-size: 11px;")
            self._detail_label.setWordWrap(True)
            self.layout().itemAt(0).widget().layout().addWidget(self._detail_label)


class TimelineEditDialog(QWidget):
    saved = Signal(dict)
    cancelled = Signal()

    def __init__(self, event: dict, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background: white; border: 1px solid #ddd; border-radius: 8px;")
        self.setMinimumWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title_label = QLabel("编辑事件")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #333;")
        layout.addWidget(title_label)

        self._title_input = QLineEdit(event.get("title", ""))
        self._title_input.setPlaceholderText("事件标题")
        self._title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: #1565C0; }
        """)
        layout.addWidget(self._title_input)

        self._detail_input = QLineEdit(event.get("detail", ""))
        self._detail_input.setPlaceholderText("描述（可选）")
        self._detail_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: #1565C0; }
        """)
        layout.addWidget(self._detail_input)

        time_str = event.get("event_time", datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(time_str)
        except (ValueError, TypeError):
            dt = datetime.now()

        self._time_edit = QDateTimeEdit(dt)
        self._time_edit.setCalendarPopup(True)
        self._time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._time_edit.setStyleSheet("""
            QDateTimeEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self._time_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
                background: white;
            }
            QPushButton:hover { background: #f5f5f5; }
        """)
        cancel_btn.clicked.connect(self.cancelled.emit)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #1565C0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
            }
            QPushButton:hover { background: #1256A8; }
        """)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_save(self):
        event = {
            "title": self._title_input.text().strip(),
            "detail": self._detail_input.text().strip(),
            "event_time": self._time_edit.dateTime().toString("yyyy-MM-ddTHH:mm:ss"),
        }
        if not event["title"]:
            return
        self.saved.emit(event)


class TimelineWidget(QWidget):
    def __init__(self, note_id: str, db, parent=None):
        super().__init__(parent)
        self._note_id = note_id
        self._db = db

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        input_frame = QWidget()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(4)

        row1 = QHBoxLayout()
        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("事件标题...")
        self._title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                background: rgba(255,255,255,0.6);
            }
            QLineEdit:focus { border-color: #1565C0; }
        """)
        row1.addWidget(self._title_input)
        input_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(4)
        self._detail_input = QLineEdit()
        self._detail_input.setPlaceholderText("描述（可选）...")
        self._detail_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                background: rgba(255,255,255,0.6);
            }
            QLineEdit:focus { border-color: #1565C0; }
        """)
        row2.addWidget(self._detail_input)

        self._time_edit = QDateTimeEdit(datetime.now())
        self._time_edit.setCalendarPopup(True)
        self._time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._time_edit.setStyleSheet("""
            QDateTimeEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                background: rgba(255,255,255,0.6);
            }
        """)
        row2.addWidget(self._time_edit)

        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(32, 32)
        self._add_btn.setStyleSheet("""
            QPushButton {
                background: #1565C0;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background: #1256A8; }
            QPushButton:pressed { background: #0D47A1; }
        """)
        self._add_btn.clicked.connect(self._add_event)
        row2.addWidget(self._add_btn)
        input_layout.addLayout(row2)

        layout.addWidget(input_frame)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; }")

        self._list_widget = TimelineListWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(8, 4, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_widget)
        layout.addWidget(self._scroll, 1)

        self._load_events()

    def _load_events(self):
        events = self._db.get_timeline_events(self._note_id)
        for event in events:
            self._add_event_widget(event)

    def _add_event(self):
        title = self._title_input.text().strip()
        if not title:
            return
        detail = self._detail_input.text().strip()
        event_time = self._time_edit.dateTime().toString("yyyy-MM-ddTHH:mm:ss")
        event_id = self._db.add_timeline_event(self._note_id, title, detail, event_time)

        event = {"id": event_id, "title": title, "detail": detail, "event_time": event_time}
        self._add_event_widget(event, prepend=True)
        self._title_input.clear()
        self._detail_input.clear()

    def _add_event_widget(self, event, prepend=False):
        widget = TimelineEventWidget(event)
        widget.edit_requested.connect(self._on_edit_event)
        widget.delete_requested.connect(self._on_delete_event)
        if prepend:
            self._list_layout.insertWidget(0, widget)
        else:
            self._list_layout.insertWidget(self._list_layout.count() - 1, widget)
        self._list_widget.update()

    def _on_edit_event(self, event: dict):
        dlg = TimelineEditDialog(event, self)
        dlg.saved.connect(lambda e: self._do_save_edit(event["id"], e))
        dlg.cancelled.connect(dlg.close)

        cursor_pos = self.cursor().pos()
        dlg.move(cursor_pos)
        dlg.show()

    def _do_save_edit(self, event_id: str, data: dict):
        self._db._conn.execute(
            "UPDATE timeline_events SET title=?, detail=?, event_time=? WHERE id=?",
            (data["title"], data["detail"], data["event_time"], event_id),
        )
        self._db._conn.commit()

        for i in range(self._list_layout.count()):
            item = self._list_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), TimelineEventWidget):
                w = item.widget()
                if w.event_id == event_id:
                    updated = {**data, "id": event_id}
                    w.update_event(updated)
                    break
        self._list_widget.update()

    def _on_delete_event(self, event_id: str):
        self._db.delete_timeline_event(event_id)
        for i in range(self._list_layout.count()):
            item = self._list_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), TimelineEventWidget):
                w = item.widget()
                if w.event_id == event_id:
                    self._list_layout.removeWidget(w)
                    w.setParent(None)
                    w.deleteLater()
                    break
        self._list_widget.update()

    def save(self):
        pass


class TimelineListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = self.layout()
        if not layout:
            painter.end()
            return

        x = 10
        line_color = QColor("#1565C0")
        dot_color = QColor("#1565C0")

        event_widgets = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), TimelineEventWidget):
                event_widgets.append(item.widget())

        if not event_widgets:
            painter.end()
            return

        pen = QPen(line_color, 2)
        painter.setPen(pen)

        first_y = event_widgets[0].geometry().center().y()
        last_y = event_widgets[-1].geometry().center().y()
        if first_y != last_y:
            painter.drawLine(x, first_y, x, last_y)

        painter.setBrush(QBrush(dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        for w in event_widgets:
            cy = w.geometry().center().y()
            painter.drawEllipse(x - 5, cy - 5, 10, 10)

        painter.end()
