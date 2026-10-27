#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ALICE_PANEL_TOKEN:?Set ALICE_PANEL_TOKEN first}"
exec .venv/bin/uvicorn backend.app:app --host "${ALICE_BIND:-127.0.0.1}" --port "${ALICE_PORT:-8765}"
