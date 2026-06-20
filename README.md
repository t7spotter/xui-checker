# Xray Usage Checker

A tiny web app where a user pastes their **vmess / vless / trojan / ss** link and
sees their own traffic usage — how much they've used, what's left, and when it
expires. It reads the numbers straight from your
[x-ui / 3x-ui](https://github.com/alireza0/x-ui) panel's API.

## How it works

1. The user pastes a config link.
2. The app pulls the client's UUID (vmess/vless) or label (trojan/ss) out of it.
3. It logs into the panel as admin and calls the panel API
   (`getClientTrafficsById` by UUID, falling back to `getClientTraffics` by email).
4. It shows `used`, `remaining`, `total`, and the expiry date.

> The app logs in as the panel admin to read usage, so run it somewhere only you
> control and keep `.env` private.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your panel URL and admin login
```

Set these in `.env`:

| Variable | What it is |
| --- | --- |
| `PANEL_BASE_URL` | Panel URL incl. web base path, e.g. `https://host:2053/path` |
| `PANEL_USERNAME` / `PANEL_PASSWORD` | Panel admin login |
| `PANEL_API_BASE` | `/xui/API/inbounds` for alireza0/x-ui, `/panel/api/inbounds` for 3x-ui |
| `PANEL_VERIFY_TLS` | `false` if the panel uses a self-signed certificate |

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open <http://localhost:8000>.

## Run with Docker

The app reads its config from `.env`, so create it first:

```bash
cp .env.example .env   # then edit .env with your panel URL and admin login
docker compose up -d --build
```

Open <http://localhost:8001>. Stop with `docker compose down`.

> `.env` is gitignored on purpose — it holds your admin password. `.env.example`
> is a committed template, so keep only placeholder values in it.
