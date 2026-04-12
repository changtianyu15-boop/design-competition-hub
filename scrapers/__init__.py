from scrapers.base import Scraper
from scrapers.demo import DemoScraper
from scrapers.json_feed import JsonFeedScraper
from scrapers.registry import build_scrapers
from scrapers.rss import RssScraper

__all__ = ["Scraper", "DemoScraper", "JsonFeedScraper", "RssScraper", "build_scrapers"]
