from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Note:
    id: str = ""
    mode: str = "normal"
    title: str = "新便签"
    color: str = "#FFF9C4"
    pinned: bool = False
    x: int = 100
    y: int = 100
    width: int = 280
    height: int = 360
    docked_edge: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
