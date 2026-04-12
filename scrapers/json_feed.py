from __future__ import annotations

import json
from pathlib import Path
from typing import List

from http_util import http_get
from models import Competition
from scrapers.base import Scraper


class JsonFeedScraper(Scraper):
    """从本地或远程 JSON 拉取比赛列表，便于自行维护数据源。"""

    def __init__(self, name: str, path_or_url: str) -> None:
        self.name = name
        self.path_or_url = path_or_url

    def fetch(self) -> List[Competition]:
        raw: str | None
        if self.path_or_url.startswith("http://") or self.path_or_url.startswith("https://"):
            data = http_get(self.path_or_url)
            if not data:
                return []
            raw = data.decode("utf-8", errors="replace")
        else:
            p = Path(self.path_or_url)
            if not p.is_absolute():
                p = Path(__file__).resolve().parent.parent / p
            if not p.exists():
                return []
            raw = p.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if not isinstance(data, list):
            return []
        out: list[Competition] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            url = str(item.get("source_url", item.get("url", ""))).strip()
            if not title:
                continue
            out.append(
                Competition(
                    title=title,
                    competition_type=str(item.get("competition_type", "未分类")),
                    deadline=str(item.get("deadline", "见官网")),
                    source_name=str(item.get("source_name", self.name)),
                    source_url=url or "#",
                    description=str(item.get("description", "")),
                    organizer=str(item.get("organizer", "")),
                    region=str(item.get("region", "")),
                    prize=str(item.get("prize", "")),
                )
            )
        return out
