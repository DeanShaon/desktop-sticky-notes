# Desktop Note

A lightweight Windows desktop note-taking tool with three modes, edge-docking auto-hide, and auto-start.

[中文文档](README_cn.md)

---

### Features

- **Three modes**: Plain text / To-do list / Timeline
- **Edge docking**: Drag to screen edge to auto-hide with a thin strip; hover to reveal (like QQ/WeChat)
- **Pin mode**: Always-on-top with edge docking disabled
- **Note sidebar**: Slide-out panel to browse and switch between notes of the same type
- **Auto-save**: All content saved to local SQLite database in real time
- **Portable**: Single .exe file, no installation required
- **Auto-start**: Optional registry-based boot launch
- **Customizable**: Color, font, opacity, corner radius

### Screenshots

<img width="350" height="450" alt="image" src="https://github.com/user-attachments/assets/413d7667-d213-4a21-8db5-0dfb01848bce" />


### Download

Get the latest `DesktopNote.exe` from the [Releases](../../releases) page.

### Usage

See [USER_GUIDE.md](./USER_GUIDE.md) for full instructions. ([中文](./USER_GUIDE_cn.md))

### Tech Stack

- **Python 3.10+**
- **PySide6** — Qt6 GUI framework
- **SQLite** — Local data storage
- **PyInstaller** — .exe packaging

### Run Locally

```bash
pip install PySide6
python main.py
```

### Build

```bash
pip install pyinstaller
python build.py
# Output: dist/DesktopNote.exe
```

### Project Structure

```
├── main.py              # Entry point
├── app/
│   ├── core/            # Edge docking, screen utils, auto-start
│   ├── models/          # Database, settings, data models
│   ├── widgets/         # UI components (title bar, three modes)
│   └── windows/         # Window management, settings dialog
├── data/                # Runtime data (DB + settings JSON)
└── dist/                # Build output
```
