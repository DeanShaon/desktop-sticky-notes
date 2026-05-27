# Desktop Note — User Guide

[中文版](USER_GUIDE_cn.md)

---

### Overview

Desktop Note is a lightweight Windows desktop utility with three note-taking modes, edge-docking auto-hide, and auto-start support. All data is stored locally — no internet required.

### Quick Start

1. Double-click `DesktopNote.exe` to launch
2. A note window appears, and a tray icon shows in the bottom-right corner
3. The window does not appear in the taskbar — manage it via the tray icon

### Three Modes

Switch modes via the top-row buttons on the title bar:

| Icon | Mode | Description |
|------|------|-------------|
| 📝 | Normal | Plain text notepad with auto-save |
| ☑ | To-Do | Checklist with auto-move to completed section |
| 🕐 | Timeline | Events ordered chronologically |

### Note Operations

- **New note**: Click the `+` button on the bottom row to create a new note in the current mode
- **Switch note**: Click the `☰` button — a sidebar slides out from the right listing all notes in the current mode. Click one to switch
- **Rename note**: Click the ✏ button on a sidebar item, or double-click the title text on the title bar
- **Delete note**: Click the × button on a sidebar item (at least one note must remain)

### To-Do Mode

- **Add item**: Type in the input field, press Enter or click +
- **Complete item**: Check the checkbox — item moves to "Completed" with strikethrough
- **Edit item**: Double-click the item text, press Enter to save
- **Delete item**: Click the × button on the right of the item

### Timeline Mode

- **Add event**: Fill in title, description (optional), and time, then click +
- **Edit event**: Click the ✏ button on an event to edit title, description, or time
- **Delete event**: Click the × button on an event

### Edge Docking

Drag the window near the left, right, or top screen edge (within 20px) and release — the window will slide off-screen, leaving a thin visible strip. Hover over the strip to reveal the window. It auto-hides 400ms after the mouse leaves.

### Pin (Always on Top)

Click the 📌 button on the top row:
- **Inactive**: Normal window behavior
- **Active** (pressed-in look): Window stays on top and will not auto-hide at screen edges

### Minimize & Exit

- **━** button: Minimize to system tray; click the tray icon to restore
- **×** button: Quit the application

### Settings

Click the ⚙ button on the top row to open the settings dialog:
- **Appearance**: Default color, font, font size, opacity, corner radius
- **Behavior**: Auto-start on boot, dock threshold, strip width, hide delay
- **Data**: Auto-save interval, data directory, import/export
