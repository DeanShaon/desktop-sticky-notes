from PySide6.QtCore import QPoint
from PySide6.QtGui import QScreen


def screen_at(pos: QPoint) -> QScreen:
    from PySide6.QtGui import QGuiApplication
    screen = QGuiApplication.screenAt(pos)
    return screen or QGuiApplication.primaryScreen()


def available_geometry(screen: QScreen):
    return screen.availableGeometry()
