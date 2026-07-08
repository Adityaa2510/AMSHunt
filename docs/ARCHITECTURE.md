# Architecture

## Overview

The platform runs five containers, orchestrated by `docker-compose.yml`:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend    │─────▶│  PostgreSQL │
│  React/Vite │ HTTP │   FastAPI    │      │             │
└─────────────┘      └──────┬───────┘      └─────────────┘
                             │ enqueue
                             ▼
                      ┌──────────────┐      ┌─────────────┐
                      │    Redis     │◀────▶│   Worker    │
                      │ (broker/     │      │   Celery +  │
                      │  result store)      │  nmap/nuclei/
                      └──────────────┘      │  subfinder/  │
                                             │  httpx/      │
                                             │  whatweb     │
                                             └─────────────┘
```

**Why split backend and worker into separate images?** The API container
only needs to serve HTTP and talk to Postgres — it should be small and
restart instantly. The worker needs a much heavier image (Go toolchain
byproducts, nmap, whatweb, several hundred MB of Nuclei templates) and runs
long tasks that can take minutes. Keeping them separate means redeploying
the API doesn't require rebuilding the tool-heavy image, and a hung scan
can't take down the API.

## Data model

```
Organization (1) ──── (N) Asset ──── (N) Finding
      │                                    ▲
      └──────── (N) Scan ──────────────────┘
```

- **Organization**: a root domain being monitored (e.g. `example.com`).
- **Asset**: anything discovered under that org — a subdomain, IP, or URL.
- **Scan**: one run of one tool against one target. Tracks status
  (queued/running/completed/failed) and links to a Celery task ID so the
  frontend can poll for progress.
- **Finding**: a single result — an open port, a detected technology, an
  SSL issue, or a vulnerability. Always tied to the asset it was found on,
  and usually to the scan that produced it.

## Scan pipeline

1. Frontend POSTs to `/scans/` with an org, scan type, and target.
2. FastAPI creates a `Scan` row (`status=queued`) and calls `.delay()` on
   the matching Celery task, which returns immediately with a task ID.
3. The Celery worker picks up the task, flips status to `running`, shells
   out to the relevant CLI tool via `asyncio.create_subprocess_exec`,
   parses the output, and writes `Finding` rows.
4. On completion, status flips to `completed` (or `failed`, with the error
   captured) and a `result_summary` JSON blob is stored on the scan.
5. The frontend polls `/scans/` every 5s while scans are in flight.

**Why Celery instead of FastAPI `BackgroundTasks`?** Nmap and Nuclei scans
can run for minutes; `BackgroundTasks` ties execution to the request
worker's lifecycle and has no retry/visibility story. Celery gives us a
durable queue, concurrency control (`SCAN_CONCURRENCY`), and a place to add
retries or scheduling (e.g. nightly re-scans) later without restructuring.

## Recommended scan order

`discovery` → `port_scan` / `tech_detect` → `vuln_scan`. Discovery has to
run first since it's what populates the `Asset` table; the other scan
types require an existing asset as their target (enforced in
`routers/scans.py`).

## Risk scoring

Deliberately simple and explainable rather than a black-box model:
`score = 100 * (1 - 0.9^(weighted_finding_count / 5))`, where each open
finding contributes a fixed weight by severity (critical=25, high=12,
medium=5, low=2, info=0). The exponential decay means the first critical
finding moves the score a lot; the tenth barely moves it further — you're
already at "fix this now" regardless. See `services/risk_score.py`.

## Extension points

- **Amass**: wired in behind `ASM_USE_AMASS=true`, off by default since
  it's slower than subfinder alone.
- **PDF export**: `reports.py` returns structured JSON designed to be fed
  straight into ReportLab (or any templating engine) for a PDF version of
  the executive summary — no schema change needed.
- **Scheduling**: nothing here re-scans automatically. A Celery beat
  schedule could re-run `discovery` nightly per org to catch newly stood-up
  subdomains.
