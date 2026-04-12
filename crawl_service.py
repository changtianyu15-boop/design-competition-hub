from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from models import Competition
from scrapers.registry import build_scrapers
from storage import load_competitions, merge_by_url, save_competitions


def run_all_scrapers() -> List[Competition]:
    scrapers = build_scrapers()
    merged: list[Competition] = []
    if not scrapers:
        existing = load_competitions()
        save_competitions(existing)
        return existing
    workers = min(10, len(scrapers))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(s.fetch): s.name for s in scrapers}
        for fut in as_completed(futures):
            try:
                merged.extend(fut.result())
            except Exception:
                continue
    existing = load_competitions()
    combined = merge_by_url(existing, merged)
    save_competitions(combined)
    return combined
