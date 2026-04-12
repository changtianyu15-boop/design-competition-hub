from __future__ import annotations

import re
from typing import List
from urllib.parse import urlparse

from feed_xml import normalize_published, parse_feed_entries
from http_util import http_get
from models import Competition
from scrapers.base import Scraper


def _guess_type(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    if any(k in text for k in ("ui", "ux", "interface", "界面")):
        return "UI/UX"
    if any(k in text for k in ("graphic", "visual", "平面", "视觉")):
        return "视觉传达"
    if any(k in text for k in ("product", "工业", "产品")):
        return "产品设计"
    if any(k in text for k in ("student", "学生")):
        return "学生赛"
    return "综合/其他"


def _matches_keywords(title: str, summary: str, keywords: list[str] | None) -> bool:
    if not keywords:
        return True
    blob = (title + " " + summary).lower()
    return any(k.lower() in blob for k in keywords)


class RssScraper(Scraper):
    def __init__(
        self,
        name: str,
        feed_url: str,
        keyword_filter: list[str] | None = None,
        region: str = "",
    ) -> None:
        self.name = name
        self.feed_url = feed_url
        self.keyword_filter = keyword_filter
        self.region = region

    def fetch(self) -> List[Competition]:
        raw = http_get(self.feed_url)
        if not raw:
            return []
        entries = parse_feed_entries(raw)
        out: list[Competition] = []
        for entry in entries:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            summary = re.sub(r"<[^>]+>", "", str(entry.get("summary") or ""))
            summary = summary.strip()[:500]
            if not title or not link:
                continue
            if not _matches_keywords(title, summary, self.keyword_filter):
                continue
            deadline = normalize_published(str(entry.get("published") or ""))
            host = urlparse(link).netloc or self.name
            out.append(
                Competition(
                    title=title,
                    competition_type=_guess_type(title, summary),
                    deadline=deadline,
                    source_name=self.name,
                    source_url=link,
                    description=summary,
                    organizer=host,
                    region=self.region or ("国际" if host.endswith((".com", ".org", ".net")) else ""),
                    prize="见原文",
                )
            )
        return out
