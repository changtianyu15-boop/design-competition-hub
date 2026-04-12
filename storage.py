from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models import Competition

DATA_PATH = Path(__file__).resolve().parent / "data" / "competitions.json"
EXCEL_PATH = Path(__file__).resolve().parent / "data" / "competitions.xlsx"


def load_competitions() -> list[Competition]:
    if not DATA_PATH.exists():
        return []
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return [Competition(**item) for item in raw]


def save_competitions(items: list[Competition]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: list[dict[str, Any]] = [c.to_dict() for c in items]
    DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def merge_by_url(existing: list[Competition], incoming: list[Competition]) -> list[Competition]:
    by_url = {c.source_url: c for c in existing if c.source_url}
    for c in incoming:
        if c.source_url and c.source_url in by_url:
            by_url[c.source_url] = c
        elif c.source_url:
            by_url[c.source_url] = c
        else:
            key = f"__nourl__{c.title}|{c.source_name}"
            by_url[key] = c
    return list(by_url.values())
