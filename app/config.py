import os

from dotenv import load_dotenv

load_dotenv()

PANEL_BASE_URL = os.environ.get("PANEL_BASE_URL", "").rstrip("/")
PANEL_USERNAME = os.environ.get("PANEL_USERNAME", "")
PANEL_PASSWORD = os.environ.get("PANEL_PASSWORD", "")
PANEL_API_BASE = os.environ.get("PANEL_API_BASE", "/xui/API/inbounds")
PANEL_VERIFY_TLS = os.environ.get("PANEL_VERIFY_TLS", "true").lower() != "false"
