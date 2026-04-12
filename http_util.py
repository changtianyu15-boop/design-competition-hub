from __future__ import annotations

import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def http_get(url: str, timeout: float = 12.0) -> bytes | None:
    req = Request(url, headers={"User-Agent": DEFAULT_UA})
    ctx = ssl.create_default_context()
    try:
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read()
    except (HTTPError, URLError, TimeoutError, OSError):
        return None
