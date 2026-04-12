"""Copy merged competition data into static/ for Netlify (no Python server)."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "competitions.json"
DST = ROOT / "static" / "competitions.json"


def main() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    if SRC.exists():
        shutil.copy(SRC, DST)
    else:
        DST.write_text("[]", encoding="utf-8")


if __name__ == "__main__":
    main()
