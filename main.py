from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

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

    def _send_bytes(
        self,
        code: int,
        body: bytes,
        content_type: str,
        extra_headers: list[tuple[str, str]] | None = None,
    ) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

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
            self._send_bytes(200, payload, "application/json; charset=utf-8")
            return

        if req_path == "/api/download/excel":
            from export_excel import competitions_to_excel
            from storage import load_competitions

            items = load_competitions()
            if not items:
                msg = "暂无数据，请先点击「重新爬取」"
                self._send_bytes(404, msg.encode("utf-8"), "text/plain; charset=utf-8")
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
            self._send_bytes(200, body, "application/json; charset=utf-8")
        except Exception as e:
            body = json.dumps({"detail": str(e)}, ensure_ascii=False).encode("utf-8")
            self._send_bytes(500, body, "application/json; charset=utf-8")


def main() -> None:
    host = "127.0.0.1"
    port = 8765
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"设计比赛看板: http://{host}:{port}/", flush=True)
    print("按 Ctrl+C 停止服务", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
