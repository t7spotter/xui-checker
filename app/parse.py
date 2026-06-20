"""Pull the lookup keys out of a pasted share link.

A client in the panel is found either by its UUID (vmess/vless, stored as
`$.id` in the inbound settings) or by its email/remark (everything else).
We extract whichever we can; the panel lookup tries the UUID first, then
falls back to the email.
"""

import base64
import binascii
import json
from urllib.parse import urlparse, unquote


def _b64decode(text):
    # Share links use base64 without padding, sometimes url-safe.
    padded = text + "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(padded)


def parse_link(link):
    """Return {"protocol", "client_id", "email"} or raise ValueError.

    client_id is the UUID when the link carries one, otherwise None.
    email is the link's remark/label when present, otherwise None.
    """
    link = link.strip()

    if link.startswith("vmess://"):
        return _parse_vmess(link)
    if link.startswith("vless://"):
        return _parse_userinfo_link(link, "vless")
    if link.startswith("trojan://"):
        # The trojan password is not stored as $.id, so don't use it as a
        # client_id; rely on the remark instead.
        parsed = _parse_userinfo_link(link, "trojan")
        parsed["client_id"] = None
        return parsed
    if link.startswith("ss://"):
        return _parse_shadowsocks(link)

    raise ValueError("Unsupported link. Paste a vmess://, vless://, trojan:// or ss:// link.")


def _parse_vmess(link):
    try:
        config = json.loads(_b64decode(link[len("vmess://"):]))
    except (binascii.Error, ValueError, UnicodeDecodeError):
        raise ValueError("Could not read this vmess link.")
    return {
        "protocol": "vmess",
        "client_id": config.get("id") or None,
        "email": config.get("ps") or None,
    }


def _parse_userinfo_link(link, protocol):
    parsed = urlparse(link)
    return {
        "protocol": protocol,
        "client_id": parsed.username or None,
        "email": unquote(parsed.fragment) or None,
    }


def _parse_shadowsocks(link):
    # ss links carry no UUID; the remark (fragment) is our only key.
    parsed = urlparse(link)
    return {
        "protocol": "shadowsocks",
        "client_id": None,
        "email": unquote(parsed.fragment) or None,
    }
