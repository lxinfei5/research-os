#!/usr/bin/env python3
"""Loopback same-origin proxy for the ResearchOS travel demo.

Browsers block page JS from calling Groq / OpenAI / Tavily (CORS).
This process is the legitimate fix: the page and the API hop share
http://127.0.0.1:<port>, keys stay on the machine, vendor traffic
uses the user's IP.

Not a generic CORS-anywhere. Hosts are allowlisted. Bind is loopback.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_BODY = 1_000_000
TIMEOUT = 90

# Security boundary: only these hosts may be contacted.
ALLOWED_HOSTS = frozenset(
    {
        "api.groq.com",
        "api.openai.com",
        "openrouter.ai",
        "api.deepseek.com",
        "api.siliconflow.cn",
        "api.moonshot.cn",
        "api.moonshot.ai",
        "api.tavily.com",
        "api.search.brave.com",
        "127.0.0.1",
        "localhost",
    }
)

PROVIDERS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "siliconflow": "https://api.siliconflow.cn/v1/chat/completions",
    "moonshot": "https://api.moonshot.cn/v1/chat/completions",
    "ollama": "http://127.0.0.1:11434/v1/chat/completions",
}

SEARCH_PROVIDERS = {
    "tavily": "https://api.tavily.com/search",
    "brave": "https://api.search.brave.com/res/v1/web/search",
}

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".md": "text/plain; charset=utf-8",
    ".ico": "image/x-icon",
}

SSL_CTX = ssl.create_default_context()


def _json_ok(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("https", "http"):
        raise ValueError("only http(s) is allowed")
    if parsed.scheme == "http" and parsed.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("http is only allowed for localhost")
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"host not allowlisted: {parsed.hostname}")
    if parsed.username or parsed.password:
        raise ValueError("userinfo in URL is not allowed")


def _forward(url: str, method: str, headers: dict, body: bytes | None) -> tuple[int, str, bytes]:
    _json_ok(url)
    req = urllib.request.Request(url, data=body, method=method)
    for key, value in headers.items():
        if value is None:
            continue
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CTX) as resp:
            return resp.status, resp.headers.get("Content-Type", "application/json"), resp.read()
    except urllib.error.HTTPError as exc:
        payload = exc.read()
        return exc.code, exc.headers.get("Content-Type", "application/json"), payload


class Handler(BaseHTTPRequestHandler):
    server_version = "researchos-travel-demo/0.4"

    def log_message(self, fmt: str, *args) -> None:
        # Do not log bodies or Authorization.
        sys.stderr.write("%s - %s\n" % (self.log_date_time_string(), fmt % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, obj: dict) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(status, raw, "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0 or length > MAX_BODY:
            raise ValueError("body missing or too large")
        raw = self.rfile.read(length)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON object required")
        return data

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json(
                200,
                {
                    "ok": True,
                    "bind": "127.0.0.1",
                    "allowed_hosts": sorted(ALLOWED_HOSTS),
                    "providers": sorted(PROVIDERS),
                    "search": sorted(SEARCH_PROVIDERS),
                },
            )
            return
        self._static(parsed.path)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        try:
            data = self._read_json()
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": "bad_request", "detail": str(exc)})
            return
        if parsed.path == "/api/llm":
            self._llm(data)
            return
        if parsed.path == "/api/search":
            self._search(data)
            return
        self._send_json(404, {"error": "not_found"})

    def _llm(self, data: dict) -> None:
        key = (data.get("api_key") or "").strip()
        if not key:
            self._send_json(400, {"error": "missing_api_key"})
            return
        provider = (data.get("provider") or "").strip().lower()
        model = (data.get("model") or "").strip()
        messages = data.get("messages")
        if not model or not isinstance(messages, list) or not messages:
            self._send_json(400, {"error": "model_and_messages_required"})
            return
        url = PROVIDERS.get(provider)
        if not url:
            base = (data.get("base_url") or "").strip().rstrip("/")
            if not base:
                self._send_json(400, {"error": "unknown_provider"})
                return
            url = base if base.endswith("/chat/completions") else base + "/v1/chat/completions"
        try:
            _json_ok(url)
        except ValueError as exc:
            self._send_json(400, {"error": "url_rejected", "detail": str(exc)})
            return
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
            "User-Agent": self.server_version,
        }
        if provider == "openrouter":
            headers["HTTP-Referer"] = "http://127.0.0.1"
            headers["X-Title"] = "ResearchOS travel demo"
        status, ctype, raw = _forward(
            url, "POST", headers, json.dumps(payload).encode("utf-8")
        )
        self._send(status, raw, ctype or "application/json")

    def _search(self, data: dict) -> None:
        key = (data.get("api_key") or "").strip()
        query = (data.get("query") or "").strip()
        provider = (data.get("provider") or "tavily").strip().lower()
        if not key or not query:
            self._send_json(400, {"error": "key_and_query_required"})
            return
        if len(query) > 300:
            self._send_json(400, {"error": "query_too_long"})
            return
        if provider == "tavily":
            url = SEARCH_PROVIDERS["tavily"]
            body = json.dumps(
                {
                    "api_key": key,
                    "query": query,
                    "max_results": 5,
                    "search_depth": "basic",
                }
            ).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "User-Agent": self.server_version,
            }
            status, ctype, raw = _forward(url, "POST", headers, body)
            self._send(status, raw, ctype or "application/json")
            return
        if provider == "brave":
            url = SEARCH_PROVIDERS["brave"] + "?" + urllib.parse.urlencode({"q": query, "count": 5})
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": key,
                "User-Agent": self.server_version,
            }
            status, ctype, raw = _forward(url, "GET", headers, None)
            self._send(status, raw, ctype or "application/json")
            return
        self._send_json(400, {"error": "unknown_search_provider"})

    def _static(self, path: str) -> None:
        rel = path.lstrip("/") or "index.html"
        target = (ROOT / rel).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            self._send_json(403, {"error": "forbidden"})
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            self._send_json(404, {"error": "not_found"})
            return
        data = target.read_bytes()
        self._send(200, data, MIME.get(target.suffix, "application/octet-stream"))


def main() -> None:
    parser = argparse.ArgumentParser(description="ResearchOS travel demo (loopback only)")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"ResearchOS travel demo  http://127.0.0.1:{args.port}", flush=True)
    print("Loopback only. Keys are forwarded to allowlisted hosts and never stored.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye", flush=True)


if __name__ == "__main__":
    main()
