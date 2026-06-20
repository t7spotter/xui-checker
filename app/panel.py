"""Talk to the x-ui / 3x-ui panel.

The panel has no per-user auth, so this service logs in once as the admin
and reuses the session cookie. When the session expires the panel answers
API calls with the login HTML instead of JSON; we detect that and log in
again, retrying the call once.
"""

import httpx

from . import config

_client = httpx.AsyncClient(
    verify=config.PANEL_VERIFY_TLS,
    timeout=15.0,
    follow_redirects=False,
)


class PanelError(Exception):
    pass


def _url(path):
    # Build the full URL ourselves so a panel web base path (e.g.
    # https://host/secretpath) is preserved. httpx base_url joining would
    # drop it when the request path starts with "/".
    return config.PANEL_BASE_URL + path


async def _login():
    try:
        response = await _client.post(
            _url("/login"),
            data={"username": config.PANEL_USERNAME, "password": config.PANEL_PASSWORD},
        )
    except httpx.HTTPError as error:
        raise PanelError(f"Cannot reach the panel: {error}")

    body = _as_json(response)
    if not body or not body.get("success"):
        raise PanelError("Panel login failed. Check PANEL_USERNAME / PANEL_PASSWORD.")


async def _get(path):
    try:
        return await _client.get(_url(path))
    except httpx.HTTPError as error:
        raise PanelError(f"Cannot reach the panel: {error}")


async def _api_get(path):
    """GET a panel API path as JSON, logging in again if the session lapsed."""
    response = await _get(path)
    body = _as_json(response)
    if body is None:
        await _login()
        response = await _get(path)
        body = _as_json(response)
        if body is None:
            raise PanelError("Panel did not return usage data (unexpected response).")
    return body


def _as_json(response):
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type:
        return None
    try:
        return response.json()
    except ValueError:
        return None


def _first_record(obj):
    if isinstance(obj, list):
        return obj[0] if obj else None
    return obj or None


async def get_client_traffic_by_id(client_id):
    body = await _api_get(f"{config.PANEL_API_BASE}/getClientTrafficsById/{client_id}")
    return _first_record(body.get("obj"))


async def get_client_traffic_by_email(email):
    body = await _api_get(f"{config.PANEL_API_BASE}/getClientTraffics/{email}")
    return _first_record(body.get("obj"))


async def find_usage(client_id, email):
    """Look up a client's traffic by UUID first, then by email."""
    if client_id:
        traffic = await get_client_traffic_by_id(client_id)
        if traffic:
            return traffic
    if email:
        return await get_client_traffic_by_email(email)
    return None
