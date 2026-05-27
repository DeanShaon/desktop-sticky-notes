import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path

from app.models.note import Note

_SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id          TEXT PRIMARY KEY,
    mode        TEXT NOT NULL DEFAULT 'normal',
    title       TEXT NOT NULL DEFAULT '新便签',
    color       TEXT NOT NULL DEFAULT '#FFF9C4',
    pinned      INTEGER NOT NULL DEFAULT 0,
    x           INTEGER NOT NULL DEFAULT 100,
    y           INTEGER NOT NULL DEFAULT 100,
    width       INTEGER NOT NULL DEFAULT 280,
    height      INTEGER NOT NULL DEFAULT 360,
    docked_edge TEXT DEFAULT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS normal_data (
    note_id  TEXT PRIMARY KEY REFERENCES notes(id) ON DELETE CASCADE,
    content  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS todo_items (
    id         TEXT PRIMARY KEY,
    note_id    TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    text       TEXT NOT NULL,
    done       INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id         TEXT PRIMARY KEY,
    note_id    TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    title      TEXT NOT NULL,
    detail     TEXT NOT NULL DEFAULT '',
    event_time TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: Path):
        self._path = path
        self._conn = sqlite3.connect(str(path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # ---- notes ----

    def create_note(self, mode="normal", color="#FFF9C4") -> str:
        import uuid
        nid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        self._conn.execute(
            "INSERT INTO notes (id, mode, color, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (nid, mode, color, now, now),
        )
        self._conn.commit()
        return nid

    def load_note(self, note_id: str) -> Optional[Note]:
        row = self._conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
        if not row:
            return None
        return Note(
            id=row["id"], mode=row["mode"], title=row["title"], color=row["color"],
            pinned=bool(row["pinned"]), x=row["x"], y=row["y"],
            width=row["width"], height=row["height"],
            docked_edge=row["docked_edge"],
            created_at=row["created_at"], updated_at=row["updated_at"],
        )

    def list_notes(self) -> list[Note]:
        rows = self._conn.execute("SELECT * FROM notes ORDER BY created_at").fetchall()
        return [
            Note(
                id=r["id"], mode=r["mode"], title=r["title"], color=r["color"],
                pinned=bool(r["pinned"]), x=r["x"], y=r["y"],
                width=r["width"], height=r["height"],
                docked_edge=r["docked_edge"],
                created_at=r["created_at"], updated_at=r["updated_at"],
            )
            for r in rows
        ]

    def save_note_position(self, note_id, x, y, w, h, docked_edge=None):
        self._conn.execute(
            "UPDATE notes SET x=?, y=?, width=?, height=?, docked_edge=? WHERE id=?",
            (x, y, w, h, docked_edge, note_id),
        )
        self._conn.commit()

    def update_note(self, note_id, **kwargs):
        if not kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [note_id]
        self._conn.execute(f"UPDATE notes SET {sets} WHERE id=?", vals)
        self._conn.commit()

    def delete_note(self, note_id):
        self._conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self._conn.commit()

    # ---- normal mode ----

    def load_normal_content(self, note_id) -> str:
        row = self._conn.execute(
            "SELECT content FROM normal_data WHERE note_id=?", (note_id,)
        ).fetchone()
        if row:
            return row["content"]
        self._conn.execute(
            "INSERT INTO normal_data (note_id, content) VALUES (?, '')", (note_id,)
        )
        self._conn.commit()
        return ""

    def save_normal_content(self, note_id, content: str):
        self._conn.execute(
            "INSERT OR REPLACE INTO normal_data (note_id, content) VALUES (?, ?)",
            (note_id, content),
        )
        self._conn.commit()

    # ---- todo mode ----

    def add_todo_item(self, note_id, text: str) -> str:
        import uuid
        iid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        row = self._conn.execute(
            "SELECT COALESCE(MAX(sort_order),0)+1 FROM todo_items WHERE note_id=?",
            (note_id,),
        ).fetchone()
        sort_order = row[0]
        self._conn.execute(
            "INSERT INTO todo_items (id, note_id, text, sort_order, created_at) VALUES (?,?,?,?,?)",
            (iid, note_id, text, sort_order, now),
        )
        self._conn.commit()
        return iid

    def get_todo_items(self, note_id, done=False) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM todo_items WHERE note_id=? AND done=? ORDER BY sort_order",
            (note_id, int(done)),
        ).fetchall()
        return [dict(r) for r in rows]

    def toggle_todo_item(self, item_id, done: bool):
        self._conn.execute(
            "UPDATE todo_items SET done=? WHERE id=?", (int(done), item_id)
        )
        self._conn.commit()

    def delete_todo_item(self, item_id):
        self._conn.execute("DELETE FROM todo_items WHERE id=?", (item_id,))
        self._conn.commit()

    # ---- timeline mode ----

    def add_timeline_event(self, note_id, title: str, detail: str, event_time: str) -> str:
        import uuid
        eid = str(uuid.uuid4())
        now = datetime.now().isoformat()
        self._conn.execute(
            "INSERT INTO timeline_events (id, note_id, title, detail, event_time, created_at) VALUES (?,?,?,?,?,?)",
            (eid, note_id, title, detail, event_time, now),
        )
        self._conn.commit()
        return eid

    def get_timeline_events(self, note_id) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM timeline_events WHERE note_id=? ORDER BY event_time DESC",
            (note_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_timeline_event(self, event_id):
        self._conn.execute("DELETE FROM timeline_events WHERE id=?", (event_id,))
        self._conn.commit()

    def close(self):
        self._conn.close()
