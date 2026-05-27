from PySide6.QtCore import Qt, Signal, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QStackedWidget, QApplication, QVBoxLayout, QWidget, QHBoxLayout,
    QLabel, QToolButton, QInputDialog, QScrollArea, QFrame, QSizePolicy,
)

from app.widgets.note_frame import NoteFrame
from app.widgets.normal_widget import NormalWidget
from app.widgets.todo_widget import TodoWidget
from app.widgets.timeline_widget import TimelineWidget
from app.core.edge_docker import EdgeDocker, DockState


class SidebarItem(QFrame):
    rename_clicked = Signal(str, str)
    delete_clicked = Signal(str)

    def __init__(self, note_id: str, title: str, is_current: bool, parent=None):
        super().__init__(parent)
        self._note_id = note_id
        self.setFrameShape(QFrame.Shape.NoFrame)
        bg = "rgba(21,101,192,0.1)" if is_current else "transparent"
        self.setStyleSheet(f"""
            SidebarItem {{
                background: {bg};
                border-radius: 6px;
                margin: 1px 0;
            }}
            SidebarItem:hover {{ background: rgba(0,0,0,0.06); }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 5, 6, 5)
        layout.setSpacing(4)

        display = title if title and title != "新便签" else "未命名"
        self._title_label = QLabel(display)
        self._title_label.setStyleSheet("""
            font-size: 12px; color: #444; background: transparent; border: none;
        """)
        self._title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self._title_label, 1)

        rename_btn = QToolButton()
        rename_btn.setText("✏")
        rename_btn.setToolTip("修改名称")
        rename_btn.setFixedSize(24, 24)
        rename_btn.setStyleSheet("""
            QToolButton { border: none; font-size: 11px; color: #999; background: transparent; }
            QToolButton:hover { color: #333; background: rgba(0,0,0,0.1); border-radius: 4px; }
        """)
        rename_btn.clicked.connect(lambda: self.rename_clicked.emit(self._note_id, self._title_label.text()))
        layout.addWidget(rename_btn)

        del_btn = QToolButton()
        del_btn.setText("×")
        del_btn.setToolTip("删除")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet("""
            QToolButton { border: none; font-size: 14px; font-weight: bold; color: #999; background: transparent; }
            QToolButton:hover { color: #e74c3c; background: rgba(231,76,60,0.1); border-radius: 4px; }
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._note_id))
        layout.addWidget(del_btn)

    def set_title(self, title: str):
        self._title_label.setText(title)


class SidebarPanel(QFrame):
    note_selected = Signal(str)
    note_renamed = Signal(str, str)
    note_deleted = Signal(str)
    create_clicked = Signal()

    def __init__(self, main_window):
        super().__init__(None)
        self._main_window = main_window
        self._width = 220
        self._visible = False
        self._mode = "normal"
        self.setObjectName("sidebarPanel")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(self._width)

        inner = QWidget()
        inner.setObjectName("sidebarInner")
        inner.setStyleSheet("""
            #sidebarInner {
                background: rgba(255,255,255,0.97);
                border: 1px solid #e0e0e0;
                border-left: none;
                border-radius: 0 10px 10px 0;
            }
        """)
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(8, 6, 8, 6)
        inner_layout.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(4)
        self._header_label = QLabel("便签列表")
        self._header_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #333;")
        header.addWidget(self._header_label, 1)

        create_btn = QToolButton()
        create_btn.setText("+")
        create_btn.setToolTip("新建")
        create_btn.setFixedSize(26, 26)
        create_btn.setStyleSheet("""
            QToolButton {
                border: none; border-radius: 4px; font-size: 18px;
                font-weight: bold; color: #4caf50;
            }
            QToolButton:hover { background: rgba(76,175,80,0.1); }
        """)
        create_btn.clicked.connect(self.create_clicked.emit)
        header.addWidget(create_btn)
        inner_layout.addLayout(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_widget)
        inner_layout.addWidget(self._scroll, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(inner)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))
        self._anim.valueChanged.connect(self._on_anim_step)

    @property
    def is_visible(self):
        return self._visible

    def set_mode(self, mode: str):
        self._mode = mode
        names = {"normal": "普通便签", "todo": "待办便签", "timeline": "时间线便签"}
        self._header_label.setText(names.get(mode, "便签列表"))

    def _on_anim_step(self, val):
        self.setFixedWidth(int(val))

    def show_panel(self):
        self._visible = True
        self._position()
        self.setFixedWidth(0)
        self.show()
        self._anim.stop()
        self._anim.setStartValue(0)
        self._anim.setEndValue(self._width)
        self._anim.start()

    def hide_panel(self):
        self._visible = False
        self._anim.stop()
        self.setFixedWidth(self._width)
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(0)
        self._anim.start()
        self._anim.finished.connect(self._on_hide_anim_done)

    def _on_hide_anim_done(self):
        try:
            self._anim.finished.disconnect(self._on_hide_anim_done)
        except (TypeError, RuntimeError):
            pass
        self.setFixedWidth(self._width)
        self.hide()

    def _position(self):
        pos = self._main_window.pos()
        x = pos.x() + self._main_window.width()
        y = pos.y()
        self.move(x, y)
        self.setFixedHeight(self._main_window.height())

    def rebuild(self, note_ids: list, current_id: str, db=None):
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        for nid in reversed(note_ids):
            title = "未命名"
            if db:
                note = db.load_note(nid)
                if note:
                    title = note.title
            item = SidebarItem(nid, title, nid == current_id)
            item.mousePressEvent = self._make_item_click_handler(nid, item.mousePressEvent, item)
            item.rename_clicked.connect(self.note_renamed.emit)
            item.delete_clicked.connect(self.note_deleted.emit)
            self._list_layout.insertWidget(0, item)

    def _make_item_click_handler(self, nid, original_handler, item_widget):
        def handler(event):
            if event.button() == Qt.LeftButton:
                pos = event.position().toPoint()
                child = item_widget.childAt(pos)
                if not isinstance(child, QToolButton):
                    self.note_selected.emit(nid)
                    return
            if original_handler:
                original_handler(event)
        return handler


class NoteWindow(NoteFrame):
    minimize_to_tray = Signal()
    quit_app = Signal()

    def __init__(self, note_id: str, db, settings=None):
        color = settings.get("appearance", "default_color") if settings else "#FFF9C4"
        super().__init__(note_id, color)

        self._db = db
        self._settings = settings
        self._current_note_id = note_id
        self._mode = "normal"
        self._mode_note_ids = {"normal": [], "todo": [], "timeline": []}
        self._loaded_widgets = {}

        self._stack = QStackedWidget()
        self.set_content(self._stack)

        self._docker = EdgeDocker(self, settings)

        note = db.load_note(note_id)
        if note:
            self._mode = note.mode
            self.title_bar.set_title(note.title)
            self.title_bar.set_active_mode(note.mode)
            self.title_bar.set_pinned(note.pinned)
            if note.color != "#FFF9C4":
                self.set_color(note.color)
            self.move(note.x, note.y)
            self.resize(note.width, note.height)
            if note.docked_edge:
                self._docker._docked_edge = note.docked_edge
                self._docker._saved_pos = self.pos()

        self._sidebar = SidebarPanel(self)
        self._sidebar.note_selected.connect(self._on_sidebar_select)
        self._sidebar.note_renamed.connect(self._on_sidebar_rename)
        self._sidebar.note_deleted.connect(self._on_sidebar_delete)
        self._sidebar.create_clicked.connect(lambda: self._on_new_note_in_mode(self._mode))

        self._sidebar.set_mode(self._mode)
        self._load_notes_for_mode(self._mode)
        self._select_note(note_id)

        self.title_bar.mode_changed.connect(self._switch_mode)
        self.title_bar.pin_clicked.connect(self._toggle_pin)
        self.title_bar.settings_clicked.connect(self._open_settings)
        self.title_bar.drag_finished.connect(self._on_drag_finished)
        self.title_bar.drag_started.connect(self._on_drag_started)
        self.title_bar.sidebar_toggle_clicked.connect(self._toggle_sidebar)
        self.title_bar.close_clicked.disconnect()
        self.title_bar.close_clicked.connect(self._on_close_clicked)
        self.title_bar._min_btn.clicked.disconnect()
        self.title_bar._min_btn.clicked.connect(self._on_minimize_clicked)
        self.title_bar.new_note_clicked.connect(self._on_new_note_in_mode)
        self.title_bar.title_changed.connect(self._on_title_changed)

        self._apply_opacity()
        self.installEventFilter(self)

    @property
    def docker(self):
        return self._docker

    def eventFilter(self, obj, event):
        if event.type() == event.Type.MouseButtonPress and self._sidebar.is_visible:
            global_pos = event.globalPosition().toPoint()
            pos_in_sidebar = self._sidebar.mapFromGlobal(global_pos)
            pos_in_main = self.mapFromGlobal(global_pos)
            if not self._sidebar.rect().contains(pos_in_sidebar) and not self.rect().contains(pos_in_main):
                from PySide6.QtWidgets import QInputDialog as Dlg
                if QApplication.activeModalWidget() is None:
                    self._toggle_sidebar()
                    return True
        if event.type() == event.Type.Move:
            if self._sidebar.is_visible:
                self._sidebar._position()
        return super().eventFilter(obj, event)

    def _toggle_sidebar(self):
        if self._sidebar.is_visible:
            self._sidebar.hide_panel()
            self._docker.sidebar_open = False
            self._on_drag_finished()
        else:
            self._rebuild_sidebar()
            self._sidebar.show_panel()
            self._docker.sidebar_open = True
            if self._docker.state == DockState.DOCKED:
                self._docker.start_undock()
            if self._docker.state == DockState.REVEALED:
                self._docker._hide_timer.stop()

    def _rebuild_sidebar(self):
        self._sidebar.rebuild(
            self._mode_note_ids.get(self._mode, []),
            self._current_note_id,
            self._db
        )

    def _on_drag_started(self):
        self._docker.on_drag_start()

    def _load_notes_for_mode(self, mode: str):
        all_notes = self._db.list_notes()
        ids = [n.id for n in all_notes if n.mode == mode]
        self._mode_note_ids[mode] = ids

    def _select_note(self, note_id: str):
        self._current_note_id = note_id
        self._ensure_widget(note_id, self._mode)
        widget = self._loaded_widgets[note_id]
        self._stack.setCurrentWidget(widget)
        note = self._db.load_note(note_id)
        if note:
            self.title_bar.set_title(note.title)

    def _ensure_widget(self, note_id: str, mode: str):
        if note_id in self._loaded_widgets:
            return
        if mode == "normal":
            w = NormalWidget(note_id, self._db, self._settings)
        elif mode == "todo":
            w = TodoWidget(note_id, self._db)
        elif mode == "timeline":
            w = TimelineWidget(note_id, self._db)
        else:
            return
        self._loaded_widgets[note_id] = w
        self._stack.addWidget(w)

    def _on_sidebar_select(self, note_id: str):
        if note_id == self._current_note_id:
            self._toggle_sidebar()
            return
        self._save_current_widget()
        self._select_note(note_id)
        self._sidebar.hide_panel()
        self._docker.sidebar_open = False
        self._on_drag_finished()

    def _on_sidebar_rename(self, note_id: str, current_title: str):
        title, ok = QInputDialog.getText(self, "修改名称", "新名称：", text=current_title)
        if ok and title.strip():
            self._db.update_note(note_id, title=title.strip())
            if note_id == self._current_note_id:
                self.title_bar.set_title(title.strip())
            self._rebuild_sidebar()

    def _on_sidebar_delete(self, note_id: str):
        ids = self._mode_note_ids.get(self._mode, [])
        if len(ids) <= 1:
            return
        self._db.delete_note(note_id)
        widget = self._loaded_widgets.pop(note_id, None)
        if widget:
            self._stack.removeWidget(widget)
            widget.deleteLater()
        self._load_notes_for_mode(self._mode)
        ids = self._mode_note_ids.get(self._mode, [])
        if note_id == self._current_note_id and ids:
            self._select_note(ids[0])
        self._rebuild_sidebar()

    def _on_new_note_in_mode(self, mode: str):
        self._save_current_widget()
        color = self._settings.get("appearance", "default_color") or "#FFF9C4"
        new_id = self._db.create_note(mode, color)
        self._load_notes_for_mode(mode)
        self._select_note(new_id)
        if self._sidebar.is_visible:
            self._rebuild_sidebar()

    def _on_title_changed(self, new_title: str):
        self._db.update_note(self._current_note_id, title=new_title)
        if self._sidebar.is_visible:
            self._rebuild_sidebar()

    def _on_close_clicked(self):
        self.quit_app.emit()

    def _on_minimize_clicked(self):
        self.minimize_to_tray.emit()

    def _on_drag_finished(self):
        self._docker.check_dock_on_release()

    def apply_settings(self):
        if not self._settings:
            return
        color = self._settings.get("appearance", "default_color") or "#FFF9C4"
        self.set_color(color)
        radius = self._settings.get("appearance", "corner_radius") or 10
        self.set_corner_radius(radius)
        self._apply_opacity()
        font_family = self._settings.get("appearance", "font_family") or "Microsoft YaHei"
        font_size = self._settings.get("appearance", "font_size") or 10
        self.setFont(QFont(font_family, font_size))
        self._docker.DOCK_THRESHOLD = self._settings.get("behavior", "dock_threshold") or 20
        self._docker.STRIP_WIDTH = self._settings.get("behavior", "strip_width") or 6
        self._docker.HIDE_DELAY = self._settings.get("behavior", "hide_delay") or 400
        self.update()

    def _apply_opacity(self):
        if self._settings:
            opacity = self._settings.get("appearance", "opacity") or 0.95
            self.setWindowOpacity(opacity)

    def _switch_mode(self, mode: str):
        if mode == self._mode:
            return
        self._save_current_widget()
        self._mode = mode
        self.title_bar.set_active_mode(mode)
        self._sidebar.set_mode(mode)
        self._load_notes_for_mode(mode)
        ids = self._mode_note_ids[mode]
        if ids:
            self._select_note(ids[0])
        else:
            color = self._settings.get("appearance", "default_color") or "#FFF9C4"
            new_id = self._db.create_note(mode, color)
            self._load_notes_for_mode(mode)
            self._select_note(new_id)
        if self._sidebar.is_visible:
            self._rebuild_sidebar()

    def _toggle_pin(self):
        note = self._db.load_note(self._current_note_id)
        pinned = not (note and note.pinned)
        self._db.update_note(self._current_note_id, pinned=int(pinned))
        self.title_bar.set_pinned(pinned)
        if pinned:
            self._docker._poll_timer.stop()
            self._docker._hide_timer.stop()
            self._docker._slide_anim.stop()
            if self._docker._state != DockState.NORMAL:
                self._docker._state = DockState.NORMAL
                self._docker._docked_edge = None
                self.move(self._docker._saved_pos)
            self._docker.pinned = True
            flags = self.windowFlags()
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            self.activateWindow()
        else:
            self._docker.pinned = False
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()

    def _open_settings(self):
        from app.windows.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._settings, self)
        dlg.settings_changed.connect(self.apply_settings)
        dlg.exec()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._docker.on_mouse_enter()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._docker.on_mouse_leave()

    def _save_current_widget(self):
        widget = self._loaded_widgets.get(self._current_note_id)
        if widget and hasattr(widget, "save"):
            widget.save()

    def closeEvent(self, event):
        self._save_current_widget()
        self._db.save_note_position(
            self.note_id,
            self._docker._saved_pos.x() if self._docker._docked_edge else self.x(),
            self._docker._saved_pos.y() if self._docker._docked_edge else self.y(),
            self.width(), self.height(),
            self._docker._docked_edge,
        )
        if self._sidebar.is_visible:
            self._sidebar.hide_panel()
        super().closeEvent(event)

    def save_current(self):
        self._save_current_widget()
        self._db.save_note_position(
            self.note_id,
            self._docker._saved_pos.x() if self._docker._docked_edge else self.x(),
            self._docker._saved_pos.y() if self._docker._docked_edge else self.y(),
            self.width(), self.height(),
            self._docker._docked_edge,
        )
