# Attack Surface Management Platform

A self-hosted ASM tool: point it at a root domain, and it discovers
subdomains, scans ports, fingerprints tech stacks, checks TLS health, and
runs vulnerability templates against everything it finds — then rolls it
all up into a risk score and an executive summary.

## Stack

| Layer     | Tech                                                             |
|-----------|-------------------------------------------------------------------|
| Frontend  | React + Vite + Tailwind                                          |
| Backend   | FastAPI (async), SQLAlchemy 2.0                                  |
| Queue     | Celery + Redis                                                   |
| Database  | PostgreSQL 16                                                    |
| Tools     | Nmap, Subfinder, httpx, Nuclei, WhatWeb, Amass (optional)        |

See `docs/ARCHITECTURE.md` for how the pieces fit together and why.

## Prerequisites

- Docker + Docker Compose
- That's it — the Go tools, nmap, and whatweb are all baked into the
  worker image at build time.

## Running it

```bash
cp .env.example .env
# edit .env: at minimum set a real POSTGRES_PASSWORD and SECRET_KEY

docker compose up --build
```

This will take a while the *first* time — the worker image compiles
subfinder/httpx/nuclei/amass from source and downloads Nuclei's CVE
template set. Subsequent builds are cached.

Once it's up:
- Frontend: http://localhost:5173
- Backend API docs (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432 (credentials from `.env`)

## First run

1. Open the frontend — you'll be prompted to register an organization
   (name + root domain).
2. Go to **Scans**, run a **Discovery** scan against that root domain.
   This populates the Assets table with live subdomains.
3. Run **Port Scan**, **Tech + SSL**, or **Vulnerability Scan** against any
   discovered asset.
4. Check **Findings** for triage, **Dashboard** for the at-a-glance risk
   score, **Reports** for the executive summary.

## A note on scope and ethics

Only point this at domains you own or have explicit authorization to test.
Nmap and Nuclei against infrastructure you don't control is unauthorized
scanning in most jurisdictions, full stop.

## Repo layout

```
asm-platform/
├── docker-compose.yml
├── backend/          # FastAPI app (API only, no scan tools)
│   └── app/
│       ├── models/       # SQLAlchemy models
│       ├── schemas/       # Pydantic request/response schemas
│       ├── routers/       # HTTP endpoints
│       ├── services/      # CLI tool wrappers + risk scoring
│       └── workers/       # Celery app + tasks
├── worker/            # Celery worker image (nmap, nuclei, subfinder, etc.)
├── frontend/          # React + Tailwind SPA
├── db/                # Postgres init script
└── docs/
    └── ARCHITECTURE.md
```

