from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import requests

@dataclass(slots=True)
class HttpResult:
    status: int
    text: str
    headers: dict[str, str]

class HttpClient:
    def __init__(self, session: requests.Session | None = None, proxies: dict[str, str] | None = None):
        self.session = session or requests.Session()
        self.proxies = proxies

    def get_text(self, url: str, *, headers: dict[str, str] | None = None, connect_timeout: float, read_timeout: float, max_body_bytes: int | None = None) -> str:
        response = self.session.get(url, headers=headers or {}, timeout=(connect_timeout, read_timeout), allow_redirects=True, proxies=self.proxies)
        response.raise_for_status()
        data = response.content
        if max_body_bytes is not None:
            data = data[:max_body_bytes]
        return data.decode(response.encoding or "utf-8", errors="replace")

    def post_json(self, url: str, payload: dict[str, Any], *, headers: dict[str, str], connect_timeout: float, read_timeout: float) -> dict[str, Any]:
        response = self.session.post(url, json=payload, headers=headers, timeout=(connect_timeout, read_timeout), allow_redirects=True, proxies=self.proxies)
        response.raise_for_status()
        if not response.text:
            raise ValueError("empty response")
        return response.json()
