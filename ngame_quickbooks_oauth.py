#!/usr/bin/env python3
"""
QuickBooks OAuth helper for NGAME.

- Refreshes access tokens automatically (and persists rotated tokens to config).
- If refresh fails with invalid_grant, runs an interactive OAuth login via local callback
  and persists the new tokens (no manual JSON edits required after initial app setup).

Environment (optional; overrides values in the JSON file when set):

- QBO_CONFIG_PATH / NGAME_QUICKBOOKS_CONFIG — path to quickbooks_config.json
- QBO_CLIENT_ID, QBO_CLIENT_SECRET — Intuit app credentials (not written back to disk)
- QBO_REDIRECT_URI, QBO_ENVIRONMENT — sandbox or production

Interactive browser OAuth is disabled when CI-style env vars are set (CI, GITHUB_ACTIONS, …).

Credential rotation (if secrets were committed, shared, or leaked):

- In the Intuit Developer Portal, rotate the app’s **client secret** and revoke or replace **refresh tokens** as needed.
- Re-run local OAuth (``ensure_quickbooks_auth`` with interactive login) or paste new tokens using your secure process.
- Prefer **QBO_CLIENT_ID** / **QBO_CLIENT_SECRET** via environment or a secrets manager so the JSON file holds only tokens, not app secrets.
"""

from __future__ import annotations

import json
import os
import socket
import stat
import threading
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs


class QuickBooksOAuthError(RuntimeError):
    pass


def default_quickbooks_config_path() -> str:
    """Path to QuickBooks JSON config; override with QBO_CONFIG_PATH or NGAME_QUICKBOOKS_CONFIG."""
    p = (os.getenv("QBO_CONFIG_PATH") or os.getenv("NGAME_QUICKBOOKS_CONFIG") or "quickbooks_config.json").strip()
    return p or "quickbooks_config.json"


def _running_in_ci() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "CI",
            "CONTINUOUS_INTEGRATION",
            "GITHUB_ACTIONS",
            "GITLAB_CI",
            "BUILDKITE",
            "TF_BUILD",
        )
    )


def _strip_secrets_for_persist(
    api: Dict[str, Any],
    *,
    client_id_from_env: bool,
    client_secret_from_env: bool,
) -> None:
    """Drop app credentials from the dict before writing JSON if they came from the environment."""
    if client_secret_from_env:
        api.pop("client_secret", None)
    if client_id_from_env:
        api.pop("client_id", None)


def _restrict_config_file_permissions(path: str) -> None:
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


@dataclass
class QuickBooksAuthBundle:
    auth_client: Any  # intuitlib.client.AuthClient
    realm_id: str


def _atomic_write_json(path: str, data: Dict[str, Any]) -> None:
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp_path, path)
    _restrict_config_file_permissions(path)


def load_quickbooks_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise QuickBooksOAuthError(
            f"QuickBooks config not found: {config_path!r}. "
            "Copy quickbooks_config.example.json to quickbooks_config.json or set QBO_CONFIG_PATH."
        ) from e


def save_quickbooks_config(config_path: str, config: Dict[str, Any]) -> None:
    _atomic_write_json(config_path, config)


def _pick_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return int(s.getsockname()[1])


def _run_local_callback_server(host: str, port: int, callback_path: str, timeout_s: int) -> Dict[str, str]:
    """
    Minimal HTTP server that captures Intuit redirect query params.
    Returns dict containing at least `code` and potentially `realmId`.
    """
    captured: Dict[str, str] = {}
    done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (BaseHTTPRequestHandler naming)
            parsed = urlparse(self.path)
            if parsed.path != callback_path:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not found")
                return

            qs = parse_qs(parsed.query)
            # Intuit typically uses `code` and `realmId`
            code = (qs.get("code") or [None])[0]
            realm_id = (qs.get("realmId") or [None])[0]
            error = (qs.get("error") or [None])[0]
            error_description = (qs.get("error_description") or [None])[0]

            if error:
                captured["error"] = error
                if error_description:
                    captured["error_description"] = error_description
            if code:
                captured["code"] = code
            if realm_id:
                captured["realmId"] = realm_id

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"NGAME: OAuth complete. You can close this tab.")
            done.set()

        def log_message(self, format: str, *args: Any) -> None:  # silence default logging
            return

    httpd = HTTPServer((host, port), Handler)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    finished = done.wait(timeout=timeout_s)
    httpd.shutdown()
    httpd.server_close()

    if not finished:
        raise QuickBooksOAuthError(f"Timed out waiting for OAuth callback on http://{host}:{port}{callback_path}")

    if "error" in captured:
        raise QuickBooksOAuthError(
            f"OAuth callback returned error={captured.get('error')} "
            f"error_description={captured.get('error_description', '')}".strip()
        )

    if "code" not in captured:
        raise QuickBooksOAuthError("OAuth callback did not include an authorization code.")

    return captured


def ensure_quickbooks_auth(config_path: str, *, interactive_on_invalid_grant: bool = True, timeout_s: int = 180) -> QuickBooksAuthBundle:
    """
    Returns an AuthClient with a valid access token, persisting refreshed/rotated tokens.
    If the refresh token is invalid and interactive_on_invalid_grant=True, runs OAuth login.
    """
    from ngame_env import load_ngame_dotenv

    load_ngame_dotenv()

    from intuitlib.client import AuthClient
    from intuitlib.enums import Scopes

    config = load_quickbooks_config(config_path)
    api = config.get("quickbooks_api") or {}

    # Environment variables override file (safer rotation and CI injection).
    raw_id_env = os.getenv("QBO_CLIENT_ID")
    raw_secret_env = os.getenv("QBO_CLIENT_SECRET")
    client_id_from_env = bool((raw_id_env or "").strip())
    client_secret_from_env = bool((raw_secret_env or "").strip())
    client_id = (raw_id_env or "").strip() or (api.get("client_id") or "").strip() or None
    client_secret = (raw_secret_env or "").strip() or (api.get("client_secret") or "").strip() or None
    redirect_uri = (os.getenv("QBO_REDIRECT_URI") or "").strip() or (api.get("redirect_uri") or "").strip() or "http://localhost:8000/callback"
    env_raw = (os.getenv("QBO_ENVIRONMENT") or "").strip() or (api.get("environment") or "").strip() or "sandbox"
    environment = env_raw.lower()
    if environment not in ("sandbox", "production"):
        raise QuickBooksOAuthError(
            f"Invalid QuickBooks environment {env_raw!r}; use sandbox or production (QBO_ENVIRONMENT or quickbooks_api.environment)."
        )

    if not client_id or not client_secret:
        raise QuickBooksOAuthError(
            "Missing QuickBooks app credentials. Set quickbooks_api.client_id/client_secret "
            "in quickbooks_config.json (or env vars QBO_CLIENT_ID / QBO_CLIENT_SECRET)."
        )

    parsed_redirect = urlparse(redirect_uri)
    callback_path = parsed_redirect.path or "/callback"
    callback_host = parsed_redirect.hostname or "localhost"
    callback_port = parsed_redirect.port

    access_token = (api.get("access_token") or "").strip()
    refresh_token = (api.get("refresh_token") or "").strip()

    auth_client = AuthClient(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token or None,
        refresh_token=refresh_token or None,
        environment=environment,
        redirect_uri=redirect_uri,
    )

    # 1) Try refresh (best path; no UI) — skip when tokens were cleared for re-auth
    need_interactive = not refresh_token
    if not need_interactive:
        try:
            auth_client.refresh()
            api["access_token"] = auth_client.access_token
            api["refresh_token"] = auth_client.refresh_token or api.get("refresh_token")
            api["environment"] = environment
            api["redirect_uri"] = redirect_uri
            _strip_secrets_for_persist(
                api,
                client_id_from_env=client_id_from_env,
                client_secret_from_env=client_secret_from_env,
            )
            config["quickbooks_api"] = api
            save_quickbooks_config(config_path, config)
            realm_id = str(api.get("realm_id") or auth_client.realm_id or "")
            if not realm_id:
                raise QuickBooksOAuthError("Missing realm_id in config (and not provided by refresh).")
            return QuickBooksAuthBundle(auth_client=auth_client, realm_id=realm_id)
        except Exception as e:
            msg = str(e)
            invalid_grant = ("invalid_grant" in msg) or ("Token invalid" in msg) or ("token invalid" in msg)
            invalid_request = "invalid_request" in msg
            if interactive_on_invalid_grant and (invalid_grant or invalid_request):
                need_interactive = True
            else:
                raise

    if _running_in_ci():
        raise QuickBooksOAuthError(
            "QuickBooks refresh failed and interactive OAuth is not available in CI. "
            "Provide valid tokens in the config file or inject QBO_CLIENT_ID / QBO_CLIENT_SECRET "
            "and a working refresh_token, or run locally once to re-authorize."
        )

    # 2) Interactive OAuth login (one-time UI)
    # If redirect_uri has a fixed port, use it; otherwise, pick a free one.
    if callback_port is None:
        callback_port = _pick_free_port(callback_host)
        redirect_uri = f"{parsed_redirect.scheme or 'http'}://{callback_host}:{callback_port}{callback_path}"
        auth_client.redirect_uri = redirect_uri

    auth_url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    webbrowser.open(auth_url)

    captured = _run_local_callback_server(
        host=callback_host,
        port=int(callback_port),
        callback_path=callback_path,
        timeout_s=timeout_s,
    )
    code = captured["code"]
    realm_id = str(captured.get("realmId") or api.get("realm_id") or "")
    if not realm_id:
        raise QuickBooksOAuthError("OAuth callback did not include realmId and config has no realm_id.")

    auth_client.get_bearer_token(code, realm_id=realm_id)

    api["access_token"] = auth_client.access_token
    api["refresh_token"] = auth_client.refresh_token
    api["realm_id"] = realm_id
    api["environment"] = environment
    api["redirect_uri"] = redirect_uri
    if not client_id_from_env:
        api["client_id"] = client_id
    if not client_secret_from_env:
        api["client_secret"] = client_secret
    _strip_secrets_for_persist(
        api,
        client_id_from_env=client_id_from_env,
        client_secret_from_env=client_secret_from_env,
    )
    config["quickbooks_api"] = api
    save_quickbooks_config(config_path, config)

    return QuickBooksAuthBundle(auth_client=auth_client, realm_id=realm_id)

