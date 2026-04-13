from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"

_CORS_PATHS = frozenset({"/api/crawl", "/api/competitions", "/api/download/excel"})


def _cors_headers() -> list[tuple[str, str]]:
    origin = os.environ.get("CORS_ALLOW_ORIGIN", "").strip()
    if not origin:
        return []
    return [
        ("Access-Control-Allow-Origin", origin),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
    ]


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_bytes(
        self,
        code: int,
        body: bytes,
        content_type: str,
        extra_headers: list[tuple[str, str]] | None = None,
        *,
        cors: bool = False,
    ) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if cors:
            for k, v in _cors_headers():
                self.send_header(k, v)
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        parsed = urlparse(self.path)
        req_path = parsed.path or "/"
        ch = _cors_headers()
        if not ch or req_path not in _CORS_PATHS:
            self.send_error(404)
            return
        self.send_response(204)
        for k, v in ch:
            self.send_header(k, v)
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        req_path = parsed.path or "/"
        if req_path == "/":
            index = STATIC / "index.html"
            if index.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(index.stat().st_size))
                self.end_headers()
                return
        self.send_error(404)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        req_path = parsed.path or "/"

        if req_path == "/":
            index = STATIC / "index.html"
            if not index.exists():
                self._send_bytes(
                    500,
                    b"Missing static/index.html",
                    "text/plain; charset=utf-8",
                )
                return
            data = index.read_bytes()
            self._send_bytes(200, data, "text/html; charset=utf-8")
            return

        if req_path == "/api/competitions":
            from storage import load_competitions

            payload = json.dumps(
                [c.to_dict() for c in load_competitions()],
                ensure_ascii=False,
            ).encode("utf-8")
            self._send_bytes(200, payload, "application/json; charset=utf-8", cors=True)
            return

        if req_path == "/competitions.json":
            fp = STATIC / "competitions.json"
            if fp.exists():
                self._send_bytes(
                    200,
                    fp.read_bytes(),
                    "application/json; charset=utf-8",
                )
                return
            self._send_bytes(404, b"{}", "application/json; charset=utf-8")
            return

        if req_path == "/api/download/excel":
            from export_excel import competitions_to_excel
            from storage import load_competitions

            items = load_competitions()
            if not items:
                msg = "暂无数据，请先点击「重新爬取」"
                self._send_bytes(
                    404,
                    msg.encode("utf-8"),
                    "text/plain; charset=utf-8",
                    cors=True,
                )
                return
            xlsx_path = competitions_to_excel(items)
            data = xlsx_path.read_bytes()
            self._send_bytes(
                200,
                data,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                [
                    (
                        "Content-Disposition",
                        'attachment; filename="design-competitions.xlsx"',
                    )
                ],
                cors=True,
            )
            return

        self._send_bytes(404, b"Not Found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if (parsed.path or "") != "/api/crawl":
            self._send_bytes(404, b"Not Found", "text/plain; charset=utf-8")
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length > 0:
            self.rfile.read(length)
        try:
            from crawl_service import run_all_scrapers
            from export_excel import competitions_to_excel

            items = run_all_scrapers()
            competitions_to_excel(items)
            body = json.dumps({"ok": True, "count": len(items)}, ensure_ascii=False).encode(
                "utf-8"
            )
            self._send_bytes(200, body, "application/json; charset=utf-8", cors=True)
        except Exception as e:
            body = json.dumps({"detail": str(e)}, ensure_ascii=False).encode("utf-8")
            self._send_bytes(500, body, "application/json; charset=utf-8", cors=True)


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"设计比赛看板: http://{host}:{port}/", flush=True)
    if _cors_headers():
        print("已启用 CORS（CORS_ALLOW_ORIGIN），可供静态页跨域调用 API。", flush=True)
    print("按 Ctrl+C 停止服务", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    # 避免部分环境证书过旧导致对外爬取 HTTPS 失败（可选，Render 一般不需要）
    if os.environ.get("PYTHONHTTPSVERIFY", "").strip() == "0":
        import ssl

        ssl._create_default_https_context = ssl._create_unverified_context  # noqa: SLF001
    main()
