"""Authentication helpers for the Google Analytics MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence
from urllib.parse import urljoin

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings


class StaticTokenVerifier(TokenVerifier):
    """Simple :class:`TokenVerifier` that checks a single bearer token."""

    def __init__(
        self,
        expected_token: str,
        *,
        client_id: str,
        scopes: Sequence[str],
        resource: str | None = None,
    ) -> None:
        self._expected_token = expected_token
        self._client_id = client_id
        self._scopes = list(scopes)
        self._resource = resource

    async def verify_token(self, token: str) -> AccessToken | None:  # noqa: D401
        if token != self._expected_token:
            return None

        return AccessToken(
            token=token,
            client_id=self._client_id,
            scopes=self._scopes,
            resource=self._resource,
        )


@dataclass(frozen=True, slots=True)
class AuthConfiguration:
    """Container bundling the auth settings and verifier for FastMCP."""

    settings: AuthSettings
    verifier: StaticTokenVerifier


def _comma_separated_list(value: str | None, *, default: Sequence[str]) -> list[str]:
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def build_auth_configuration() -> AuthConfiguration:
    """Create the ``AuthConfiguration`` using environment variables.

    Raises:
        SystemExit: If the ``MCP_TOKEN`` environment variable is missing.
    """

    token = os.getenv("MCP_TOKEN")
    if not token:
        raise SystemExit(
            "MCP_TOKEN environment variable must be set to secure the MCP server."
        )

    client_id = os.getenv("MCP_CLIENT_ID", "google-analytics-mcp")
    scopes = _comma_separated_list(
        os.getenv("MCP_REQUIRED_SCOPES"), default=("mcp:invoke",)
    )

    issuer_url = os.getenv("MCP_AUTH_ISSUER_URL", "https://mcp.local/issuer")

    # Prefer an explicit resource server URL so the WWW-Authenticate header can
    # point clients to OAuth metadata. When unset, derive a sensible default
    # based on the configured host/port.
    resource_url = os.getenv("MCP_RESOURCE_SERVER_URL")
    if not resource_url:
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = os.getenv("MCP_PORT", "8000")
        base = f"http://{host}:{port}"
        default_path = os.getenv("MCP_STREAMABLE_HTTP_PATH", "/mcp")
        resource_url = urljoin(base, default_path.lstrip("/"))

    settings = AuthSettings(
        issuer_url=issuer_url,
        resource_server_url=resource_url,
        required_scopes=scopes,
    )

    verifier = StaticTokenVerifier(
        token,
        client_id=client_id,
        scopes=scopes or ["mcp:invoke"],
        resource=(
            str(settings.resource_server_url)
            if settings.resource_server_url is not None
            else None
        ),
    )

    return AuthConfiguration(settings=settings, verifier=verifier)
