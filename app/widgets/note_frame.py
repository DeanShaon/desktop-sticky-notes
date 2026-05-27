from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect

from app.widgets.title_bar import TitleBar


class NoteFrame(QWidget):
    closed = Signal()

    def __init__(self, note_id: str, color: str = "#FFF9C4", parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self._color = QColor(color)
        self._corner_radius = 10
        self._border_color = QColor(color).darker(115)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(220, 200)
        self.resize(300, 380)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))

        self._container = QWidget(self)
        self._container.setGraphicsEffect(shadow)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 12, 12, 12)
        self._layout.setSpacing(0)

        self._inner_layout = QVBoxLayout(self._container)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(0)

        self.title_bar = TitleBar(self._container)
        self._inner_layout.addWidget(self.title_bar)

        self._content_area = QWidget()
        self._content_layout = QVBoxLayout(self._content_area)
        self._content_layout.setContentsMargins(10, 6, 10, 10)
        self._inner_layout.addWidget(self._content_area, 1)

        self._layout.addWidget(self._container)

        self.title_bar.close_clicked.connect(self._on_close)

    def set_content(self, widget: QWidget):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._content_layout.addWidget(widget)

    def set_color(self, color: str):
        self._color = QColor(color)
        self._border_color = QColor(color).darker(115)
        self.update()

    def set_corner_radius(self, radius: int):
        self._corner_radius = radius
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self._container.geometry()
        path = QPainterPath()
        path.addRoundedRect(rect, self._corner_radius, self._corner_radius)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        lighter = QColor(self._color)
        lighter.setAlpha(250)
        gradient.setColorAt(0, lighter)
        base = QColor(self._color)
        base.setAlpha(240)
        gradient.setColorAt(1, base)
        painter.fillPath(path, gradient)

        pen = QPen(self._border_color, 1)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.end()

    def _on_close(self):
        self.closed.emit()
        self.close()
