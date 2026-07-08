
# Worker image: Celery consumer with every CLI security tool baked in.
# Build context is the repo root (see docker-compose.yml) so this can pull
# in backend/app directly without duplicating source or requirements.txt.

# ---- Stage 1: build Go-based recon tools ----
FROM golang:1.24-bookworm AS tools

ENV GOPATH=/go
ENV PATH=$GOPATH/bin:$PATH
# projectdiscovery tools bump their minimum Go version often; if a future
# release needs newer than the base image ships, let Go fetch it rather
# than hard-failing the build.
ENV GOTOOLCHAIN=auto

RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/owasp-amass/amass/v4/...@master

# ---- Stage 2: runtime image ----
FROM python:3.12-slim

WORKDIR /app

# nmap: port scanning | whatweb: deep tech fingerprinting (Ruby-based, apt is simplest)
# ca-certificates: needed for nuclei's HTTPS template downloads
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    whatweb \
    libpq-dev \
    gcc \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pull compiled Go binaries from stage 1
COPY --from=tools /go/bin/subfinder /usr/local/bin/subfinder
COPY --from=tools /go/bin/httpx /usr/local/bin/httpx
COPY --from=tools /go/bin/nuclei /usr/local/bin/nuclei
COPY --from=tools /go/bin/amass /usr/local/bin/amass

# Pre-fetch nuclei templates at build time so the first scan isn't slow.
# In production, re-run this periodically (cron/CI) to catch new CVE templates.
RUN nuclei -update-templates || true

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --retries 5 --timeout 100 -r requirements.txt

COPY backend/app ./app

CMD ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"]



