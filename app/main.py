from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import panel
from .parse import parse_link

app = FastAPI(title="XUI Usage Checker")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class CheckRequest(BaseModel):
    link: str


@app.post("/api/check")
async def check(request: CheckRequest):
    if not request.link.strip():
        return {"ok": False, "error": "Paste a config link first."}

    try:
        client = parse_link(request.link)
    except ValueError as error:
        return {"ok": False, "error": str(error)}

    try:
        traffic = await panel.find_usage(client["client_id"], client["email"])
    except panel.PanelError as error:
        return {"ok": False, "error": str(error)}

    if not traffic:
        return {"ok": False, "error": "No client found for this link on the panel."}

    return {
        "ok": True,
        "protocol": client["protocol"],
        "email": traffic.get("email", ""),
        "enable": traffic.get("enable", True),
        "up": traffic.get("up", 0),
        "down": traffic.get("down", 0),
        "total": traffic.get("total", 0),
        "expiryTime": traffic.get("expiryTime", 0),
    }


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")
