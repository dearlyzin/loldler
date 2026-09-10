# Deploy

Self-hosting guide. The API is a single FastAPI container - any Docker-capable host works (VPS, home server, NAS, PC).

## Run (Docker)

```bash
docker build -t loldler .
docker run -d --name loldler -p 8000:8000 \
  -e LOLDLE_HISTORY_DIR=/data \
  -v loldler-data:/data \
  loldler
```

The API listens on container port `8000`. `LOLDLE_HISTORY_DIR` must point to a writable directory - persist it with a volume to keep the `yesterday` feature across restarts.

## Public exposure (optional)

A domain is only needed for public HTTPS access. Local or LAN use works out of the box at `http://localhost:8000`.

For public exposure, put the container behind any reverse proxy with your own domain:

- Caddy (simplest): `your.domain { reverse_proxy localhost:8000 }`
- Traefik / nginx: route your hostname to port `8000`.

For platform healthchecks (Dokploy, Coolify, Komodo, etc.), use `GET /health` - it is intentionally cheap and touches nothing external.

## Without Docker

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run uvicorn loldle.api:app --host 0.0.0.0 --port 8000
```

## Endpoints

| Endpoint | What it returns |
| --- | --- |
| `GET /health` | `{"status":"ok"}` liveness probe. |
| `GET /` | Service status JSON (name, version, date, region, endpoint list). |
| `GET /answers?region=america` | Full JSON payload: today's answers for all 5 modes plus yesterday. |
| `GET /docs` | Auto-generated Swagger UI. |

The `region` query parameter is optional and defaults to `america`. The `/answers` payload is the decrypted loldle data as-is - consumer apps format it themselves.
