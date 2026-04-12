from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from scrapers.base import Scraper
from scrapers.demo import DemoScraper
from scrapers.json_feed import JsonFeedScraper
from scrapers.rss import RssScraper


def _load_config() -> dict[str, Any]:
    root = Path(__file__).resolve().parent.parent
    path = root / "config" / "feeds.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_scrapers() -> List[Scraper]:
    cfg = _load_config()
    scrapers: List[Scraper] = []
    if not cfg:
        scrapers.append(DemoScraper())
        return scrapers
    for item in cfg.get("rss_feeds", []) or []:
        url = item.get("url")
        if not url:
            continue
        scrapers.append(
            RssScraper(
                name=item.get("name", "RSS"),
                feed_url=url,
                keyword_filter=item.get("keyword_filter"),
                region=item.get("region", ""),
            )
        )
    for item in cfg.get("json_feeds", []) or []:
        p = item.get("path_or_url")
        if not p:
            continue
        scrapers.append(
            JsonFeedScraper(
                name=item.get("name", "JSON"),
                path_or_url=p,
            )
        )
    if cfg.get("include_demo", True):
        scrapers.append(DemoScraper())
    return scrapers
