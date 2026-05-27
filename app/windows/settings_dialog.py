from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QComboBox, QCheckBox, QSlider, QFontComboBox,
    QPushButton, QFileDialog, QFormLayout, QSpinBox, QGroupBox,
)
from PySide6.QtGui import QFont

from app.models.settings import Settings
from app.core.autostart import is_auto_start, set_auto_start


class SettingsDialog(QDialog):
    settings_changed = Signal()

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("设置")
        self.setMinimumSize(420, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._tabs.addTab(self._build_appearance_tab(), "外观")
        self._tabs.addTab(self._build_behavior_tab(), "行为")
        self._tabs.addTab(self._build_data_tab(), "数据")

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._save_btn = QPushButton("保存")
        self._save_btn.clicked.connect(self._save)
        btn_layout.addWidget(self._save_btn)

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)
        layout.addLayout(btn_layout)

    def _build_appearance_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["浅色", "深色"])
        theme = self._settings.get("appearance", "theme")
        self._theme_combo.setCurrentIndex(0 if theme == "light" else 1)
        form.addRow("主题:", self._theme_combo)

        self._color_btn = QPushButton()
        color = self._settings.get("appearance", "default_color") or "#FFF9C4"
        self._color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid gray; min-width: 60px; min-height: 24px;")
        self._color_btn.clicked.connect(self._pick_color)
        self._selected_color = color
        form.addRow("默认便签颜色:", self._color_btn)

        self._font_combo = QFontComboBox()
        font_family = self._settings.get("appearance", "font_family") or "Microsoft YaHei"
        self._font_combo.setCurrentFont(QFont(font_family))
        form.addRow("字体:", self._font_combo)

        self._font_size = QSpinBox()
        self._font_size.setRange(8, 18)
        self._font_size.setValue(self._settings.get("appearance", "font_size") or 10)
        form.addRow("字号:", self._font_size)

        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(70, 100)
        self._opacity_slider.setValue(int((self._settings.get("appearance", "opacity") or 0.95) * 100))
        self._opacity_label = QLabel(f"{self._opacity_slider.value()}%")
        self._opacity_slider.valueChanged.connect(lambda v: self._opacity_label.setText(f"{v}%"))
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(self._opacity_slider)
        opacity_row.addWidget(self._opacity_label)
        form.addRow("透明度:", opacity_row)

        self._radius_slider = QSlider(Qt.Orientation.Horizontal)
        self._radius_slider.setRange(0, 16)
        self._radius_slider.setValue(self._settings.get("appearance", "corner_radius") or 8)
        self._radius_label = QLabel(str(self._radius_slider.value()))
        self._radius_slider.valueChanged.connect(lambda v: self._radius_label.setText(str(v)))
        radius_row = QHBoxLayout()
        radius_row.addWidget(self._radius_slider)
        radius_row.addWidget(self._radius_label)
        form.addRow("圆角大小:", radius_row)

        return w

    def _build_behavior_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        self._autostart_cb = QCheckBox("开机自启动")
        self._autostart_cb.setChecked(is_auto_start())
        form.addRow(self._autostart_cb)

        self._dock_threshold = QSpinBox()
        self._dock_threshold.setRange(10, 40)
        self._dock_threshold.setValue(self._settings.get("behavior", "dock_threshold") or 20)
        self._dock_threshold.setSuffix(" px")
        form.addRow("贴边触发距离:", self._dock_threshold)

        self._strip_width = QSpinBox()
        self._strip_width.setRange(4, 12)
        self._strip_width.setValue(self._settings.get("behavior", "strip_width") or 6)
        self._strip_width.setSuffix(" px")
        form.addRow("贴边条宽度:", self._strip_width)

        self._hide_delay = QSpinBox()
        self._hide_delay.setRange(200, 1000)
        self._hide_delay.setSingleStep(50)
        self._hide_delay.setValue(self._settings.get("behavior", "hide_delay") or 400)
        self._hide_delay.setSuffix(" ms")
        form.addRow("自动隐藏延迟:", self._hide_delay)

        self._minimize_to_tray = QCheckBox("关闭时最小化到托盘")
        self._minimize_to_tray.setChecked(
            self._settings.get("behavior", "minimize_to_tray") is not False
        )
        form.addRow(self._minimize_to_tray)

        return w

    def _build_data_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        self._autosave_interval = QSpinBox()
        self._autosave_interval.setRange(300, 2000)
        self._autosave_interval.setSingleStep(100)
        self._autosave_interval.setValue(self._settings.get("advanced", "auto_save_interval") or 500)
        self._autosave_interval.setSuffix(" ms")
        form.addRow("自动保存间隔:", self._autosave_interval)

        self._data_dir_btn = QPushButton(
            self._settings.get("advanced", "data_dir") or "默认目录"
        )
        self._data_dir_btn.clicked.connect(self._pick_data_dir)
        form.addRow("数据目录:", self._data_dir_btn)

        export_btn = QPushButton("导出数据")
        export_btn.clicked.connect(self._export_data)
        form.addRow(export_btn)

        import_btn = QPushButton("导入数据")
        import_btn.clicked.connect(self._import_data)
        form.addRow(import_btn)

        return w

    def _pick_color(self):
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self._selected_color = color.name()
            self._color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid gray; min-width: 60px; min-height: 24px;"
            )

    def _pick_data_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择数据目录")
        if d:
            self._data_dir_btn.setText(d)

    def _export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出数据", "notes_backup.json", "JSON (*.json)")
        if not path:
            return
        import json, shutil
        from app.app import DATA_DIR
        db_path = DATA_DIR / "notes.db"
        if db_path.exists():
            shutil.copy2(str(db_path), path.replace(".json", ".db"))
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"settings": self._settings._data}, f, indent=2, ensure_ascii=False)

    def _import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入数据", "", "JSON (*.json)")
        if not path:
            return

    def _save(self):
        s = self._settings
        s.set("appearance", "theme", "light" if self._theme_combo.currentIndex() == 0 else "dark")
        s.set("appearance", "default_color", self._selected_color)
        s.set("appearance", "font_family", self._font_combo.currentFont().family())
        s.set("appearance", "font_size", self._font_size.value())
        s.set("appearance", "opacity", self._opacity_slider.value() / 100.0)
        s.set("appearance", "corner_radius", self._radius_slider.value())

        s.set("behavior", "dock_threshold", self._dock_threshold.value())
        s.set("behavior", "strip_width", self._strip_width.value())
        s.set("behavior", "hide_delay", self._hide_delay.value())
        s.set("behavior", "minimize_to_tray", self._minimize_to_tray.isChecked())

        s.set("advanced", "auto_save_interval", self._autosave_interval.value())

        data_dir = self._data_dir_btn.text()
        if data_dir != "默认目录":
            s.set("advanced", "data_dir", data_dir)
        else:
            s.set("advanced", "data_dir", "")

        set_auto_start(self._autostart_cb.isChecked())

        self.settings_changed.emit()
        self.accept()
