from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QCheckBox, QLabel, QFrame, QScrollArea, QToolButton,
)


class TodoItemWidget(QFrame):
    toggled = Signal(object)
    delete_clicked = Signal(object)
    text_edited = Signal(object, str)

    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self._item = item
        self._editing = False
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        self._checkbox = QCheckBox()
        self._checkbox.setChecked(bool(item["done"]))
        self._checkbox.stateChanged.connect(self._on_toggle)
        self._checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 2px solid #aaa;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background: #4caf50;
                border-color: #4caf50;
            }
        """)
        layout.addWidget(self._checkbox)

        self._label = QLabel(item["text"])
        self._label.setWordWrap(True)
        self._label.setStyleSheet("font-size: 13px; padding: 2px 4px;")
        layout.addWidget(self._label, 1)

        self._edit_input = QLineEdit(item["text"])
        self._edit_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 2px 4px;
                font-size: 13px;
                background: rgba(255,255,255,0.8);
            }
        """)
        self._edit_input.returnPressed.connect(self._finish_edit)
        self._edit_input.hide()
        layout.addWidget(self._edit_input, 1)

        self._del_btn = QToolButton()
        self._del_btn.setText("×")
        self._del_btn.setFixedSize(20, 20)
        self._del_btn.setStyleSheet("""
            QToolButton {
                border: none;
                color: #ccc;
                font-size: 14px;
                font-weight: bold;
            }
            QToolButton:hover {
                color: #e74c3c;
            }
        """)
        self._del_btn.clicked.connect(lambda: self.delete_clicked.emit(self))
        layout.addWidget(self._del_btn)

        self._update_style()

    @property
    def item_id(self):
        return self._item["id"]

    @property
    def is_done(self):
        return bool(self._item["done"])

    def mouseDoubleClickEvent(self, event):
        if not self._editing:
            self._start_edit()

    def _start_edit(self):
        self._editing = True
        self._label.hide()
        self._edit_input.setText(self._item["text"])
        self._edit_input.show()
        self._edit_input.setFocus()
        self._edit_input.selectAll()

    def _finish_edit(self):
        new_text = self._edit_input.text().strip()
        if new_text and new_text != self._item["text"]:
            self._item["text"] = new_text
            self._label.setText(new_text)
            self.text_edited.emit(self, new_text)
        self._editing = False
        self._edit_input.hide()
        self._label.show()

    def focusOutEvent(self, event):
        if self._editing:
            self._finish_edit()
        super().focusOutEvent(event)

    def _on_toggle(self, state):
        self._item["done"] = bool(state)
        self._update_style()
        self.toggled.emit(self)

    def _update_style(self):
        if self._item["done"]:
            self._label.setStyleSheet("""
                color: #999;
                text-decoration: line-through;
                font-size: 13px;
                padding: 2px 4px;
            """)
        else:
            self._label.setStyleSheet("font-size: 13px; padding: 2px 4px; color: #333;")


class TodoWidget(QWidget):
    def __init__(self, note_id: str, db, parent=None):
        super().__init__(parent)
        self._note_id = note_id
        self._db = db

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)
        self._input = QLineEdit()
        self._input.setPlaceholderText("添加待办事项，回车确认...")
        self._input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                background: rgba(255,255,255,0.6);
            }
            QLineEdit:focus {
                border-color: #4caf50;
            }
        """)
        self._input.returnPressed.connect(self._add_item)
        input_layout.addWidget(self._input)

        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(32, 32)
        self._add_btn.setStyleSheet("""
            QPushButton {
                background: #4caf50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background: #43a047; }
            QPushButton:pressed { background: #388e3c; }
        """)
        self._add_btn.clicked.connect(self._add_item)
        input_layout.addWidget(self._add_btn)
        layout.addLayout(input_layout)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; }")

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_widget)
        layout.addWidget(self._scroll, 1)

        self._load_items()

    def _load_items(self):
        pending = self._db.get_todo_items(self._note_id, done=False)
        done = self._db.get_todo_items(self._note_id, done=True)

        for item in pending:
            self._add_item_widget(item)
        if done:
            self._add_separator()
            for item in done:
                self._add_item_widget(item)

    def _add_item(self):
        text = self._input.text().strip()
        if not text:
            return
        item_id = self._db.add_todo_item(self._note_id, text)
        item = {"id": item_id, "text": text, "done": False}
        self._add_item_widget(item, before_separator=True)
        self._input.clear()

    def _add_item_widget(self, item, before_separator=False):
        widget = TodoItemWidget(item)
        widget.toggled.connect(self._on_item_toggled)
        widget.delete_clicked.connect(self._on_item_deleted)
        widget.text_edited.connect(self._on_item_edited)
        if before_separator:
            sep_index = self._find_separator_index()
            self._list_layout.insertWidget(sep_index, widget)
        else:
            self._list_layout.insertWidget(self._list_layout.count() - 1, widget)

    def _add_separator(self):
        sep = QLabel("──── 已完成 ────")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep.setStyleSheet("color: #999; font-size: 11px; margin: 8px 0; padding: 4px;")
        self._list_layout.insertWidget(self._list_layout.count() - 1, sep)

    def _find_separator_index(self):
        for i in range(self._list_layout.count()):
            item = self._list_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel):
                return i
        return self._list_layout.count() - 1

    def _on_item_toggled(self, widget: TodoItemWidget):
        self._db.toggle_todo_item(widget.item_id, widget.is_done)
        self._list_layout.removeWidget(widget)
        widget.setParent(None)

        if widget.is_done:
            if self._find_separator_index() == self._list_layout.count() - 1:
                self._add_separator()
            self._list_layout.insertWidget(self._list_layout.count() - 1, widget)
        else:
            sep_index = self._find_separator_index()
            self._list_layout.insertWidget(sep_index, widget)

    def _on_item_deleted(self, widget: TodoItemWidget):
        self._db.delete_todo_item(widget.item_id)
        self._list_layout.removeWidget(widget)
        widget.setParent(None)
        widget.deleteLater()

    def _on_item_edited(self, widget: TodoItemWidget, new_text: str):
        self._db._conn.execute(
            "UPDATE todo_items SET text=? WHERE id=?", (new_text, widget.item_id)
        )
        self._db._conn.commit()

    def save(self):
        pass
