# 桌面便签应用 — 实现计划

## Context

用户需要一个 Windows 桌面便签小程序，核心特性：贴边隐藏、三种记录模式（普通/待办/时间轴）。要求轻量可分发（打包为 exe），有设置页面（外观、颜色、开机自启动等）。项目从零开始。

---

## 技术选型

- **GUI 框架**: PySide6（Qt6）
  - 贴边动画依赖 `QPropertyAnimation`，Tkinter 会卡顿
  - 无边框透明窗口在 Win10 上表现正常
  - 可访问原生 HWND，便于置顶、系统托盘、开机自启注册

- **数据存储**: SQLite（`sqlite3` 标准库，零依赖）

- **打包**: PyInstaller
  - `pyinstaller --onefile --windowed --icon=icon.ico main.py`
  - 单 exe 文件，双击即用，无需安装 Python
  - 预估 exe 体积 40-60MB（PySide6 剪裁后）
  - 可用 UPX 压缩进一步减小体积

- **依赖**:
  ```
  PySide6
  pyinstaller
  ```

---

## 项目结构

```
demo7-desktop-note/
├── main.py                    # 入口
├── requirements.txt
├── build.spec                 # PyInstaller 打包配置
├── app/
│   ├── __init__.py
│   ├── app.py                 # QApplication 初始化
│   ├── core/
│   │   ├── __init__.py
│   │   ├── edge_docker.py     # 贴边隐藏状态机 + 动画
│   │   ├── screen_utils.py    # 屏幕几何计算
│   │   └── autostart.py       # 开机自启（注册表操作）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py        # SQLite 连接、建表、CRUD
│   │   ├── note.py            # Note 数据类
│   │   └── settings.py        # 应用设置读写
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── note_frame.py      # 无边框主窗口 + 圆角
│   │   ├── title_bar.py       # 自定义标题栏
│   │   ├── normal_widget.py   # 普通模式
│   │   ├── todo_widget.py     # 待办模式
│   │   └── timeline_widget.py # 时间轴模式
│   └── windows/
│       ├── __init__.py
│       ├── note_window.py     # 单个便签窗口
│       ├── note_manager.py    # 多窗口管理 + 系统托盘
│       └── settings_dialog.py # 设置页面
└── data/                      # 运行时创建 notes.db + settings.json
```

---

## 数据存储

### SQLite — 便签数据

```sql
CREATE TABLE notes (
    id          TEXT PRIMARY KEY,
    mode        TEXT NOT NULL DEFAULT 'normal',
    title       TEXT NOT NULL DEFAULT '新便签',
    color       TEXT NOT NULL DEFAULT '#FFF9C4',
    pinned      INTEGER NOT NULL DEFAULT 0,
    x, y, width, height  INTEGER,
    docked_edge TEXT DEFAULT NULL,
    created_at  TEXT, updated_at  TEXT
);

CREATE TABLE normal_data (
    note_id  TEXT PRIMARY KEY REFERENCES notes(id) ON DELETE CASCADE,
    content  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE todo_items (
    id TEXT PRIMARY KEY, note_id TEXT REFERENCES notes(id) ON DELETE CASCADE,
    text TEXT NOT NULL, done INTEGER DEFAULT 0, sort_order INTEGER DEFAULT 0,
    created_at TEXT
);

CREATE TABLE timeline_events (
    id TEXT PRIMARY KEY, note_id TEXT REFERENCES notes(id) ON DELETE CASCADE,
    title TEXT NOT NULL, detail TEXT DEFAULT '', event_time TEXT NOT NULL,
    created_at TEXT
);
```

### settings.json — 应用设置

```json
{
  "appearance": {
    "theme": "light",
    "default_color": "#FFF9C4",
    "font_family": "Microsoft YaHei",
    "font_size": 10,
    "opacity": 0.95,
    "corner_radius": 8
  },
  "behavior": {
    "auto_start": false,
    "dock_threshold": 20,
    "strip_width": 6,
    "hide_delay": 400,
    "show_delay": 150,
    "minimize_to_tray": true
  },
  "advanced": {
    "auto_save_interval": 500,
    "data_dir": ""
  }
}
```

设置用 JSON 文件而非数据库，方便用户手动编辑，也与便签数据分离。

---

## 设置页面设计（SettingsDialog）

用 `QDialog` 实现，分类标签页：

### 外观设置
| 设置项 | 控件 | 说明 |
|--------|------|------|
| 主题 | 下拉框（浅色/深色） | 切换全局 QSS |
| 默认便签颜色 | 颜色选择器 | 新建便签的默认色 |
| 字体 | 字体选择器 | 全局字体 |
| 字号 | 滑块 (8-18) | 全局字号 |
| 窗口透明度 | 滑块 (0.7-1.0) | 便签窗口透明度 |
| 圆角大小 | 滑块 (0-16) | 窗口圆角像素 |

### 行为设置
| 设置项 | 控件 | 说明 |
|--------|------|------|
| 开机自启动 | 复选框 | 写入/删除注册表启动项 |
| 贴边触发距离 | 滑块 (10-40px) | 离边缘多近触发贴边 |
| 贴边条宽度 | 滑块 (4-12px) | 隐藏后露出多宽 |
| 自动隐藏延迟 | 滑块 (200-1000ms) | 鼠标离开多久后隐藏 |
| 关闭时最小化到托盘 | 复选框 | 关闭按钮=最小化到托盘 |

### 数据设置
| 设置项 | 控件 | 说明 |
|--------|------|------|
| 自动保存间隔 | 滑块 (300-2000ms) | 文字变更后多久保存 |
| 数据目录 | 文件夹选择器 | 自定义数据存储位置 |
| 导出数据 | 按钮 | 导出为 JSON 备份 |
| 导入数据 | 按钮 | 从 JSON 恢复 |

**开机自启动实现** (`autostart.py`):
- 写注册表: `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- 键名: `DesktopNote`，值为 exe 完整路径
- 用 `ctypes` 调用 `winreg` 操作，无需额外依赖

**入口**: 标题栏增加齿轮图标按钮，或在系统托盘菜单中加"设置"选项

---

## 核心设计

### 1. 贴边隐藏（EdgeDocker 状态机）

```
NORMAL → 拖拽释放距边缘 ≤20px → DOCKING(动画滑出) → DOCKED(仅6px条可见)
DOCKED → 鼠标靠近条 → REVEALING(动画滑入) → REVEALED(完全显示)
REVEALED → 鼠标离开 400ms → HIDING(动画滑回) → DOCKED
```

- 动画: `QPropertyAnimation` + `OutCubic` 缓动，200ms
- 悬停检测: `QCursor.pos()` 100ms 轮询
- 停靠时 `WindowStaysOnTopHint`，展开后取消
- 贴边参数（触发距离、条宽度、隐藏延迟）均可在设置中调整

### 2. 窗口架构

- 每个便签独立窗口，可分别贴到不同边缘
- `NoteFrame`: 无边框 + `WA_TranslucentBackground` + 圆角
- `TitleBar`: 拖动 / 模式切换 / 置顶 / 设置 / 最小化 / 关闭
- `QStackedWidget` 切换三种模式

### 3. 三种模式

**普通模式**: `QPlainTextEdit`，防抖自动保存

**待办模式**:
```
[+] 添加待办...
☐ 买牛奶
☐ 写周报
──── 已完成 ────
☑ 交水电费              ← 灰色+删除线
```

**时间轴模式**:
```
● 2026-05-27 09:00
│ 晨会
│ 讨论项目进度
● 2026-05-27 14:00
│ 客户演示
```

### 4. NoteManager

- 系统托盘菜单：新建便签 / 新建待办 / 新建时间线 / 设置 / 显示全部 / 退出
- 启动时恢复便签窗口
- 管理便签生命周期

---

## 打包分发

使用 PyInstaller 打包为单个 exe：

```bash
pyinstaller --onefile --windowed --name "桌面便签" --icon=icon.ico main.py
```

- `--onefile`: 打包为单个 exe
- `--windowed`: 不弹出控制台黑窗口
- `--icon`: 自定义图标
- `--name`: exe 文件名

打出的 exe 发给别人直接双击运行，无需安装 Python。首次运行会在 exe 同目录下创建 `data/` 文件夹存放数据库和设置。

---

## 开发阶段

1. **骨架** — 项目结构 + Database + Settings + NoteFrame + TitleBar + 系统托盘
2. **普通模式** — NormalWidget + 自动保存 + 恢复
3. **贴边隐藏** — EdgeDocker 状态机 + 动画 + 悬停检测
4. **待办模式** — TodoWidget + 勾选 + 删除线 + 已完成区
5. **时间轴模式** — TimelineWidget + 时间线绘制
6. **设置页面** — SettingsDialog（外观/行为/数据三个标签页）+ 开机自启
7. **打包测试** — PyInstaller 打包 exe，在干净环境测试运行

---

## 验证方式

- 阶段 1：创建无边框窗口，系统托盘可见，设置能读写
- 阶段 2：输入文字 → 关闭 → 重开 → 文字仍在
- 阶段 3：拖到边缘 → 滑出 → 鼠标靠近 → 滑回 → 离开 → 再滑出
- 阶段 4：添加待办 → 勾选 → 移到已完成区
- 阶段 5：添加事件 → 时间线正确绘制
- 阶段 6：设置页面修改主题/颜色/字号即时生效，开机自启注册表项正确
- 阶段 7：打包后的 exe 在无 Python 环境的电脑上正常运行
