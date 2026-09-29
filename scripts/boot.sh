#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
cp -n backend/.env.example backend/.env || true
if command -v docker >/dev/null 2>&1; then
  exec docker compose -f infra/docker-compose.yml up -d --build
fi
exec python3 backend/serve.py
