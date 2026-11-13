"""Minimal client for the Felicity Wi-Fi module local protocol (TCP 53970).

The module answers an ASCII command with one or more JSON objects. Large replies
are split into several objects glued together (``{...}{...}``). The client never
sends anything that changes device state.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any


class FelicityError(Exception):
    """Communication or protocol error."""


def split_objects(raw: str) -> list[dict[str, Any]]:
    """Split a ``{..}{..}`` stream into JSON objects (brace-depth scan)."""
    out: list[dict[str, Any]] = []
    depth = 0
    start: int | None = None
    in_str = False
    esc = False
    for i, ch in enumerate(raw):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                out.append(json.loads(raw[start : i + 1]))
                start = None
    return out


def merge(objs: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for obj in objs:
        merged.update(obj)
    return merged


class FelicityClient:
    """One request per TCP connection — the module closes idle sockets anyway."""

    def __init__(self, host: str, port: int, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._lock = asyncio.Lock()

    async def query(self, cmd: bytes, expect_key: str | None = None) -> dict[str, Any]:
        async with self._lock:
            try:
                return await self._query(cmd, expect_key)
            except FelicityError:
                raise
            except (OSError, asyncio.TimeoutError, ValueError) as err:
                raise FelicityError(f"{type(err).__name__}: {err}") from err

    async def _query(self, cmd: bytes, expect_key: str | None) -> dict[str, Any]:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), self.timeout
        )
        try:
            writer.write(cmd)
            await writer.drain()
            loop = asyncio.get_running_loop()
            deadline = loop.time() + self.timeout
            buf = b""
            while (left := deadline - loop.time()) > 0:
                try:
                    # after the first bytes, a short silence means the reply is complete
                    chunk = await asyncio.wait_for(reader.read(4096), min(left, 0.6) if buf else left)
                except asyncio.TimeoutError:
                    break
                if not chunk:
                    break
                buf += chunk
                if expect_key:
                    try:
                        data = merge(split_objects(buf.decode("utf-8", "ignore")))
                    except ValueError:
                        continue  # partial JSON — keep reading
                    if expect_key in data:
                        return data
            objs = split_objects(buf.decode("utf-8", "ignore"))
            if not objs:
                raise FelicityError(f"no JSON in reply ({len(buf)} bytes)")
            return merge(objs)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass
