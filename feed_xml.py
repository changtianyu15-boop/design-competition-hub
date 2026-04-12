from __future__ import annotations

import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from typing import Any


def _local(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def _child_text(parent: ET.Element, names: tuple[str, ...]) -> str:
    for ch in parent:
        if _local(ch.tag) in names:
            return _text(ch) or "".join(ch.itertext()).strip()
    return ""


def _atom_link(parent: ET.Element) -> str:
    for ch in parent:
        if _local(ch.tag) != "link":
            continue
        href = ch.attrib.get("href", "").strip()
        if href:
            return href
        t = _text(ch)
        if t:
            return t
    return ""


def parse_feed_entries(content: bytes) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []
    kind = _local(root.tag)
    out: list[dict[str, Any]] = []

    if kind == "rss":
        channel: ET.Element | None = None
        for ch in root:
            if _local(ch.tag) == "channel":
                channel = ch
                break
        if channel is None:
            return []
        for ch in channel:
            if _local(ch.tag) != "item":
                continue
            title = _child_text(ch, ("title",))
            link = _child_text(ch, ("link",))
            if not link:
                link = _atom_link(ch)
            summary = _child_text(ch, ("description", "summary", "content:encoded"))
            pub = _child_text(ch, ("pubDate", "published", "date"))
            if title or link:
                out.append(
                    {
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "published": pub,
                    }
                )
        return out

    if kind == "feed":
        for ch in root:
            if _local(ch.tag) != "entry":
                continue
            title = _child_text(ch, ("title",))
            link = _atom_link(ch)
            summary = _child_text(ch, ("summary", "content"))
            pub = _child_text(ch, ("published", "updated"))
            if title or link:
                out.append(
                    {
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "published": pub,
                    }
                )
        return out

    return []


def normalize_published(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return "见官网"
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    try:
        return parsedate_to_datetime(s).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OverflowError):
        return s[:32]
