# loldle-resolver

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Daily auto-solver for all [loldle.net](https://loldle.net) puzzle modes: Classic, Quote, Ability, Emoji, and Splash Art.

## How it works

1. Fetches the encrypted `cache.json` from loldle's CDN
2. Decrypts the payload using AES-CBC (CryptoJS-compatible via `EVP_BytesToKey`)
3. Renders all 5 daily answers in your terminal with Rich

## Install

```bash
# Via uv (recommended)
uv tool install loldle-resolver

# Or run directly
uvx loldle-resolver
```

## Usage

```bash
loldle-resolver
```

Output example:

```
╭──────────────────────────────────╮
│ LOLDLE RESOLVER  |  DD/MM/YYYY  │
╰──────────────────────────────────╯

Yesterday: Aatrox | Jinx | Yasuo | Zed | Lux

───────────────────────────────────

╭─ Classic ────────────────────────╮
│ Champion  Ahri                  │
│ Quote     Vi                    │
│ Ability   Charm                 │
│ Splash    Arcade Ahri           │
╰─────────────────────────────────╯

╭─ Quote ─────────────────────────╮
│ Champion  Jinx                  │
│ Quote     "I'm crazy! Got a..." │
╰─────────────────────────────────╯

... (Ability, Emoji, Splash Art)

───────────────────────────────────
Data from cache.loldle.net
```

## API

The project doubles as a JSON API. Host it with [DEPLOY.md](DEPLOY.md) or run it locally:

```bash
uv run uvicorn loldle.api:app --host 0.0.0.0 --port 8000
```

| Endpoint | Description |
| --- | --- |
| `GET /health` | Liveness probe (`{"status":"ok"}`). |
| `GET /answers?region=america` | Full payload: all 5 modes plus yesterday. |
| `GET /docs` | Auto-generated Swagger UI. |

Example response from `/answers`:

```json
{
  "date": "10/09/2026",
  "region": "america",
  "answers": {
    "classic": {
      "champion_name": "Ahri",
      "clues": {
        "quote": { "name": "Vi" },
        "ability": { "name": "Charm" },
        "splash": { "name": "Arcade Ahri" }
      }
    },
    "quote": {
      "champion_name": "Jinx",
      "question": "I'm crazy! Got a laundry list of bad behaviors?"
    },
    "ability": {
      "champion_name": "Vi",
      "ability_name": "Charm",
      "ability_letter": "Q"
    },
    "emoji": {
      "champion_name": "Lux",
      "title": "the Lady of Luminosity"
    },
    "splash": {
      "champion_name": "Ahri",
      "splash_name": "Arcade Ahri"
    }
  },
  "yesterday": {
    "classic": "Aatrox",
    "quote": "Jinx",
    "ability": "Yasuo",
    "emoji": "Zed",
    "splash": "Lux"
  }
}
```

A mode that fails to decrypt degrades to `{"error": true}` instead of breaking the payload. `yesterday` is `null` on a fresh install.

## Disclaimer

This is an educational project with no affiliation to loldle.net. Use at your own discretion.

## License

[MIT](LICENSE)
