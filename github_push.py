"""可选：爬取完成后把 data/competitions.json 推回 GitHub，减轻云端磁盘被回收后丢数据的问题。

环境变量（在 Render 等平台的 Environment 里配置）：
  GITHUB_TOKEN   经典 PAT，需勾选 repo 范围
  GITHUB_REPO    形如 owner/repo，例如 changtianyu15-boop/design-competition-hub

未配置时本模块不执行任何网络请求。
"""
from __future__ import annotations

import base64
import json
import os
import ssl
import urllib.error
import urllib.request

from storage import DATA_PATH


def push_competitions_json_to_github_if_configured() -> None:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPO", "").strip()
    if not token or not repo or "/" not in repo:
        return
    if not DATA_PATH.exists():
        return
    path = "data/competitions.json"
    api = f"https://api.github.com/repos/{repo}/contents/{path}"
    content_b64 = base64.b64encode(DATA_PATH.read_bytes()).decode("ascii")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "design-competition-hub-crawl",
    }

    sha: str | None = None
    get_req = urllib.request.Request(api, headers=headers, method="GET")
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(get_req, timeout=45, context=ctx) as r:
            meta = json.loads(r.read().decode("utf-8"))
            sha = meta.get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    body_obj: dict = {
        "message": "chore: update competitions.json from cloud crawl",
        "content": content_b64,
    }
    if sha:
        body_obj["sha"] = sha

    put_req = urllib.request.Request(
        api,
        data=json.dumps(body_obj).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(put_req, timeout=90, context=ctx) as r:
        r.read()
