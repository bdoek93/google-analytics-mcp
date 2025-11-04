#!/usr/bin/env python3

# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entry point for the Google Analytics MCP server."""

from __future__ import annotations

import logging
import os
from typing import Final

from analytics_mcp.coordinator import mcp

# The following imports are necessary to register the tools with the `mcp`
# object, even though they are not directly used in this file.
# The `# noqa: F401` comment tells the linter to ignore the "unused import"
# warning.
from analytics_mcp.tools.admin import info  # noqa: F401
from analytics_mcp.tools.reporting import realtime  # noqa: F401
from analytics_mcp.tools.reporting import core  # noqa: F401

_TRANSPORT_ALIASES: Final[dict[str, str]] = {
    "stdio": "stdio",
    "sse": "sse",
    "streamable-http": "streamable-http",
    "streamable_http": "streamable-http",
    "http": "streamable-http",
}


def _resolve_transport() -> str:
    """Return the transport declared through ``MCP_TRANSPORT``.

    Defaults to ``stdio`` when the variable is unset.  Common aliases such as
    ``http`` or ``streamable_http`` are accepted for convenience.
    """

    raw_transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    try:
        return _TRANSPORT_ALIASES[raw_transport]
    except KeyError as exc:  # pragma: no cover - defensive branch
        supported = ", ".join(sorted(set(_TRANSPORT_ALIASES.values())))
        msg = (
            "Unsupported MCP transport %r. Supported transports are: %s"
            % (raw_transport, supported)
        )
        raise SystemExit(msg) from exc


def _apply_runtime_settings(transport: str) -> None:
    """Mutate the FastMCP settings based on environment variables."""

    host = os.getenv("MCP_HOST")
    if not host and transport != "stdio":
        # Cloud platforms (Railway, Fly.io, etc.) require the server to bind to
        # all interfaces to make the HTTP transport reachable.  We keep the
        # local-friendly default (127.0.0.1) for stdio-only runs.
        host = "0.0.0.0"
    if host:
        mcp.settings.host = host

    port_value = os.getenv("MCP_PORT")
    if port_value:
        try:
            port = int(port_value)
        except ValueError as exc:  # pragma: no cover - defensive branch
            raise SystemExit(f"Invalid MCP_PORT value {port_value!r}") from exc
        mcp.settings.port = port

    log_level = os.getenv("MCP_LOG_LEVEL")
    if log_level:
        normalized = log_level.upper()
        mcp.settings.log_level = normalized
        logging.getLogger().setLevel(normalized)

    mount_path = os.getenv("MCP_MOUNT_PATH")
    if mount_path:
        mcp.settings.mount_path = mount_path

    if transport != "stdio":
        logging.info(
            "Starting Google Analytics MCP with %s transport on %s:%s",
            transport,
            mcp.settings.host,
            mcp.settings.port,
        )


def run_server() -> None:
    """Runs the server.

    Serves as the entrypoint for the ``runmcp`` command.
    """

    transport = _resolve_transport()
    _apply_runtime_settings(transport)

    mount_path = mcp.settings.mount_path if transport == "sse" else None
    mcp.run(transport=transport, mount_path=mount_path)


if __name__ == "__main__":
    run_server()
