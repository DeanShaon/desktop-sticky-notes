from enum import Enum, auto
from PySide6.QtCore import QObject, QTimer, QPropertyAnimation, QEasingCurve, QPoint, Signal, Qt
from PySide6.QtWidgets import QWidget
from app.core.screen_utils import screen_at, available_geometry


class DockState(Enum):
    NORMAL = auto()
    DOCKING = auto()
    DOCKED = auto()
    REVEALING = auto()
    REVEALED = auto()
    HIDING = auto()


class EdgeDocker(QObject):
    DOCK_THRESHOLD = 20
    STRIP_WIDTH = 6
    HIDE_DELAY = 400
    ANIM_DURATION = 200
    POLL_INTERVAL = 100

    state_changed = Signal(str)

    def __init__(self, window: QWidget, settings=None):
        super().__init__(window)
        self._window = window
        self._settings = settings
        self._state = DockState.NORMAL
        self._docked_edge = None
        self._saved_pos = QPoint()
        self._sidebar_open = False
        self.pinned = False

        self._slide_anim = QPropertyAnimation(window, b"pos")
        self._slide_anim.setDuration(self.ANIM_DURATION)
        self._slide_anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.OutCubic))
        self._slide_anim.finished.connect(self._on_anim_finished)

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(self.POLL_INTERVAL)
        self._poll_timer.timeout.connect(self._on_poll)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._start_hide)

        if settings:
            self.DOCK_THRESHOLD = settings.get("behavior", "dock_threshold") or 20
            self.STRIP_WIDTH = settings.get("behavior", "strip_width") or 6
            self.HIDE_DELAY = settings.get("behavior", "hide_delay") or 400

    @property
    def state(self):
        return self._state

    @property
    def docked_edge(self):
        return self._docked_edge

    @property
    def sidebar_open(self):
        return self._sidebar_open

    @sidebar_open.setter
    def sidebar_open(self, val: bool):
        old = self._sidebar_open
        self._sidebar_open = val
        if val and not old and self._state == DockState.REVEALED:
            self._hide_timer.stop()
        if not val and old and self._state == DockState.REVEALED:
            self._hide_timer.start(self.HIDE_DELAY)

    def on_drag_start(self):
        if self._state in (DockState.DOCKED,):
            self._poll_timer.stop()
            self._window.move(self._saved_pos)
        if self._state != DockState.NORMAL:
            self._hide_timer.stop()
            self._slide_anim.stop()
            flags = self._window.windowFlags()
            if flags & Qt.WindowType.WindowStaysOnTopHint:
                self._window.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
                self._window.show()
        self._state = DockState.NORMAL
        self._docked_edge = None

    def check_dock_on_release(self):
        if self._sidebar_open or self.pinned:
            return
        if self._state not in (DockState.NORMAL, DockState.REVEALED):
            return
        pos = self._window.pos()
        geo = available_geometry(screen_at(pos))
        threshold = self.DOCK_THRESHOLD

        edge = None
        if pos.x() - geo.left() <= threshold:
            edge = "left"
        elif geo.right() - (pos.x() + self._window.width()) <= threshold:
            edge = "right"
        elif pos.y() - geo.top() <= threshold:
            edge = "top"

        if edge:
            self._start_dock(edge)
        else:
            self._state = DockState.NORMAL
            self._docked_edge = None

    def start_undock(self):
        if self._state != DockState.DOCKED:
            return
        self._poll_timer.stop()
        self._state = DockState.NORMAL
        self._docked_edge = None
        self._window.move(self._saved_pos)
        flags = self._window.windowFlags()
        if flags & Qt.WindowType.WindowStaysOnTopHint:
            self._window.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            self._window.show()

    def _start_dock(self, edge: str):
        self._state = DockState.DOCKING
        self._docked_edge = edge
        self._saved_pos = self._window.pos()
        self.state_changed.emit("docking")

        geo = available_geometry(screen_at(self._window.pos()))
        target = self._compute_target(edge, geo)

        self._slide_anim.stop()
        self._slide_anim.setStartValue(self._window.pos())
        self._slide_anim.setEndValue(target)
        self._slide_anim.start()

    def _start_reveal(self):
        if self._state != DockState.DOCKED:
            return
        self._state = DockState.REVEALING
        self._hide_timer.stop()
        self.state_changed.emit("revealing")

        self._slide_anim.stop()
        self._slide_anim.setStartValue(self._window.pos())
        self._slide_anim.setEndValue(self._saved_pos)
        self._slide_anim.start()

    def _start_hide(self):
        if self._state != DockState.REVEALED:
            return
        if self._sidebar_open:
            return
        self._state = DockState.HIDING
        self.state_changed.emit("hiding")

        geo = available_geometry(screen_at(self._window.pos()))
        target = self._compute_target(self._docked_edge, geo)

        self._slide_anim.stop()
        self._slide_anim.setStartValue(self._window.pos())
        self._slide_anim.setEndValue(target)
        self._slide_anim.start()

    def _compute_target(self, edge: str, geo) -> QPoint:
        strip = self.STRIP_WIDTH
        if edge == "left":
            return QPoint(geo.left() - self._window.width() + strip, self._saved_pos.y())
        elif edge == "right":
            return QPoint(geo.right() - strip, self._saved_pos.y())
        elif edge == "top":
            return QPoint(self._saved_pos.x(), geo.top() - self._window.height() + strip)
        return self._saved_pos

    def _on_anim_finished(self):
        if self._state == DockState.DOCKING:
            self._state = DockState.DOCKED
            self.state_changed.emit("docked")
            flags = self._window.windowFlags()
            if not flags & Qt.WindowType.WindowStaysOnTopHint:
                self._window.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
                self._window.show()
            self._poll_timer.start()
        elif self._state == DockState.REVEALING:
            self._state = DockState.REVEALED
            self.state_changed.emit("revealed")
            flags = self._window.windowFlags()
            if flags & Qt.WindowType.WindowStaysOnTopHint:
                self._window.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
                self._window.show()
            self._window.activateWindow()
        elif self._state == DockState.HIDING:
            self._state = DockState.DOCKED
            self.state_changed.emit("docked")
            flags = self._window.windowFlags()
            if not flags & Qt.WindowType.WindowStaysOnTopHint:
                self._window.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
                self._window.show()
            self._poll_timer.start()

    def _on_poll(self):
        if self._state != DockState.DOCKED:
            return
        if self._sidebar_open or self.pinned:
            return
        cursor_pos = self._window.cursor().pos()
        margin = 15
        if self._docked_edge == "left":
            geo = available_geometry(screen_at(cursor_pos))
            cx = cursor_pos.x()
            if geo.left() <= cx <= geo.left() + self.STRIP_WIDTH + margin:
                self._poll_timer.stop()
                self._start_reveal()
        elif self._docked_edge == "right":
            geo = available_geometry(screen_at(cursor_pos))
            cx = cursor_pos.x()
            if geo.right() - self.STRIP_WIDTH - margin <= cx <= geo.right():
                self._poll_timer.stop()
                self._start_reveal()
        elif self._docked_edge == "top":
            geo = available_geometry(screen_at(cursor_pos))
            cy = cursor_pos.y()
            if geo.top() <= cy <= geo.top() + self.STRIP_WIDTH + margin:
                self._poll_timer.stop()
                self._start_reveal()

    def on_mouse_leave(self):
        if self._state == DockState.REVEALED and not self._sidebar_open:
            self._hide_timer.start(self.HIDE_DELAY)

    def on_mouse_enter(self):
        if self._state == DockState.REVEALED:
            self._hide_timer.stop()
