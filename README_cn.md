# 桌面便签 — Desktop Note

一款轻量级 Windows 桌面便签工具，支持三种记录模式、贴边隐藏、开机自启动。

[English](README.md)

---

### 特性

- **三种记录模式**：普通记事本 / 待办清单 / 时间轴
- **贴边隐藏**：拖到屏幕边缘自动隐藏，留一条细边，鼠标靠近即展开（类似 QQ/微信）
- **置顶固定**：一键置顶并锁定位置，不贴边不隐藏
- **便签列表**：右侧滑出面板，浏览和切换同类便签
- **自动保存**：所有内容实时自动保存到本地数据库
- **便携分发**：单 exe 文件，双击即用，无需安装
- **开机自启**：支持注册开机启动项
- **外观可定制**：支持调整颜色、字体、透明度、圆角

### 截图

> 运行后按 `Win+Shift+S` 截图替换此处

### 下载

从 [Releases](../../releases) 页面下载最新版 `桌面便签.exe`。

### 使用

详见 [USER_GUIDE_cn.md](./USER_GUIDE_cn.md)（[English](./USER_GUIDE.md)）

### 技术栈

- **Python 3.10+**
- **PySide6** — Qt6 界面框架
- **SQLite** — 本地数据存储
- **PyInstaller** — 打包为 exe

### 本地运行

```bash
pip install PySide6
python main.py
```

### 打包

```bash
pip install pyinstaller
python build.py
# 输出: dist/桌面便签.exe
```

### 项目结构

```
├── main.py              # 入口
├── app/
│   ├── core/            # 贴边隐藏、屏幕计算、开机自启
│   ├── models/          # 数据库、设置、数据模型
│   ├── widgets/         # 界面组件（标题栏、三种模式）
│   └── windows/         # 窗口管理、设置对话框
├── data/                # 运行时生成（数据库 + 设置）
└── dist/                # 打包输出
```
