"""HTTP bridge to a local xiaohongshu-mcp server — the Xiaohongshu anti-bot FALLBACK path.

(XHS is multi-path: the real-Chrome webbridge-mcp / kimi-webbridge transport is preferred; this
bridge is the MCP fallback used on anti-bot / headless EOF.)

This is the fallback transport for when the runtime has not exposed the xiaohongshu-mcp server as a
native MCP tool. It forwards explicit agent requests to an already-running local MCP Streamable-HTTP
endpoint (the server holds the user's XHS login/cookie session). It does NOT scrape pages, infer
meaning, or write ResearchOS data. Loopback-only by default; destructive tools blocked unless opted
in. Ported verbatim from AStockOS lib/xiaohongshu_mcp_bridge.py (env var renamed).

Endpoint override: ROS_XHS_MCP_URL (default http://localhost:18060/mcp).
"""
from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from . import social_pacing

DEFAULT_ENDPOINT = "http://localhost:18060/mcp"
BRIDGE_TRANSPORT = "streamable_http_jsonrpc"
MCP_PROTOCOL_VERSION = "2025-03-26"
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}

# Map xiaohongshu-mcp tool name → pacing op, so the min-gap fits the risk of the call
# (detail/get_feed_detail is the higher-risk op → longer gap). See ros/lib/social_pacing.py.
_OP_FOR_TOOL = {"search_feeds": "search", "get_feed_detail": "detail"}


class XiaohongshuMcpBridgeError(RuntimeError):
    """Base bridge error with audit-friendly message text."""


class BridgeConfigError(XiaohongshuMcpBridgeError):
    pass


class BridgeHTTPError(XiaohongshuMcpBridgeError):
    pass


class BridgeProtocolError(XiaohongshuMcpBridgeError):
    pass


class DestructiveToolBlocked(XiaohongshuMcpBridgeError):
    pass


def default_endpoint() -> str:
    return os.environ.get("ROS_XHS_MCP_URL", DEFAULT_ENDPOINT)


def _is_loopback_host(host: str | None) -> bool:
    if not host:
        return False
    clean = host.strip("[]").lower()
    if clean in LOOPBACK_HOSTS:
        return True
    try:
        return bool(socket.getaddrinfo(clean, None, flags=socket.AI_NUMERICHOST)) and (
            clean.startswith("127.") or clean == "::1"
        )
    except socket.gaierror:
        return False


def validate_endpoint(endpoint: str, *, allow_remote: bool = False) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise BridgeConfigError("xhs MCP endpoint must be an http(s) URL")
    if not allow_remote and not _is_loopback_host(parsed.hostname):
        raise BridgeConfigError(
            "xhs MCP bridge only allows loopback endpoints by default; "
            "pass --allow-remote to override")
    return endpoint


def _header(headers: Any, name: str) -> str | None:
    value = headers.get(name)
    if value:
        return str(value).strip()
    wanted = name.lower()
    for key, raw in headers.items():
        if str(key).lower() == wanted:
            return str(raw).strip()
    return None


def _decode_response(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8", errors="replace").strip() if isinstance(raw, bytes) else str(raw).strip()
    if not text:
        raise BridgeProtocolError("empty MCP response")
    if text.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise BridgeProtocolError(f"invalid JSON-RPC response: {exc}") from exc
        if not isinstance(data, dict):
            raise BridgeProtocolError("JSON-RPC response must be an object")
        return data

    # Streamable HTTP may return text/event-stream. Keep the last JSON data frame.
    frames: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            if current:
                frames.append("\n".join(current))
                current = []
            continue
        if line.startswith("data:"):
            current.append(line.split(":", 1)[1].lstrip())
    if current:
        frames.append("\n".join(current))
    for frame in reversed(frames):
        try:
            data = json.loads(frame)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    raise BridgeProtocolError("MCP response was neither JSON nor JSON SSE data")


def _jsonrpc_error_text(error: Any) -> str:
    if not isinstance(error, dict):
        return str(error)
    message = error.get("message") or error.get("code") or error
    if error.get("data") is not None:
        return f"{message}; data={error.get('data')}"
    return str(message)


@dataclass
class XiaohongshuMcpBridge:
    endpoint: str | None = None
    allow_remote: bool = False
    timeout_sec: float = 20

    def __post_init__(self) -> None:
        self.endpoint = validate_endpoint(
            self.endpoint or default_endpoint(), allow_remote=self.allow_remote)
        self.session_id: str | None = None
        self._request_id = 0
        self._tool_cache: list[dict[str, Any]] | None = None

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {},
        }).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(
            self.endpoint or default_endpoint(), data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                raw = resp.read()
                session = _header(resp.headers, "Mcp-Session-Id")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise BridgeHTTPError(f"HTTP {exc.code} from xhs MCP endpoint: {detail[:500]}") from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            raise BridgeHTTPError(f"failed to reach xhs MCP endpoint: {exc}") from exc

        data = _decode_response(raw)
        if "error" in data:
            raise BridgeProtocolError(_jsonrpc_error_text(data.get("error")))
        if method == "initialize":
            if not session:
                raise BridgeProtocolError("initialize response missing Mcp-Session-Id header")
            self.session_id = session
        return data

    def initialize(self) -> dict[str, Any]:
        data = self._post("initialize", {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "researchos-xhs-mcp-bridge", "version": "1.0"},
        })
        return data.get("result") or {}

    def ensure_initialized(self) -> None:
        if not self.session_id:
            self.initialize()

    def list_tools(self) -> dict[str, Any]:
        self.ensure_initialized()
        data = self._post("tools/list")
        result = data.get("result") or {}
        tools = result.get("tools") or []
        if not isinstance(tools, list):
            raise BridgeProtocolError("tools/list result.tools must be a list")
        self._tool_cache = [t for t in tools if isinstance(t, dict)]
        return {
            "bridge_transport": BRIDGE_TRANSPORT,
            "endpoint": self.endpoint,
            "count": len(self._tool_cache),
            "tools": self._tool_cache,
            "raw_result": result,
        }

    def _tools(self) -> list[dict[str, Any]]:
        if self._tool_cache is None:
            self.list_tools()
        return self._tool_cache or []

    def _tool_info(self, name: str) -> dict[str, Any]:
        for tool in self._tools():
            if tool.get("name") == name:
                return tool
        raise BridgeProtocolError(f"xhs MCP tool not found: {name}")

    @staticmethod
    def _is_destructive(tool: dict[str, Any]) -> bool:
        annotations = tool.get("annotations") or {}
        if not isinstance(annotations, dict):
            return False
        return annotations.get("destructiveHint") is True

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None, *,
                  allow_destructive: bool = False, source: str = "xiaohongshu",
                  op: str | None = None) -> dict[str, Any]:
        self.ensure_initialized()
        tool = self._tool_info(name)
        if self._is_destructive(tool) and not allow_destructive:
            raise DestructiveToolBlocked(
                f"xhs MCP tool '{name}' is marked destructive; pass --allow-destructive")
        # W-02 circuit breaker: refuse to dispatch while the source is in cooldown. Retrying a
        # throttled source is exactly what escalates a soft limit (empty result / EOF) into a hard
        # ban (扫码 wall) — "狂刷正是把软限流升级成硬封的元凶". Auto-expires; do NOT loop.
        cd = social_pacing.in_cooldown(source)
        if cd:
            until, reason = cd
            raise BridgeHTTPError(
                f"source '{source}' is in COOLDOWN until {until} ({reason}). A risk-control signal "
                f"was seen on a prior call; retrying now risks an irreversible account ban. Wait for "
                f"it to expire, or clear it via ros.lib.social_pacing.clear_cooldown('{source}').")
        # W-04 pacing: enforce the min inter-call gap (with jitter) before touching the account.
        # A fixed/machine cadence is itself a bot fingerprint; the gap humanizes it.
        resolved_op = op or _OP_FOR_TOOL.get(name)
        social_pacing.enforce_min_gap(source, resolved_op)
        data = self._post("tools/call", {"name": name, "arguments": arguments or {}})
        result = data.get("result") or {}
        if not isinstance(result, dict):
            raise BridgeProtocolError("tools/call result must be an object")
        ret = {
            "bridge_transport": BRIDGE_TRANSPORT,
            "endpoint": self.endpoint,
            "tool": name,
            "is_error": bool(result.get("isError") or result.get("is_error")),
            "content": result.get("content") or [],
            "raw_result": result,
        }
        # W-02 detect a risk-control marker (扫码 / EOF / empty-error / etc.) in the result → set
        # cooldown so the NEXT call refuses to dispatch. Pattern match only, not a judgement.
        marker = social_pacing.looks_like_risk_signal(ret)
        if marker is not None:
            reason = f"risk marker '{marker}'" if marker else "MCP error / empty result"
            social_pacing.set_cooldown(source, reason=reason)
        return ret
