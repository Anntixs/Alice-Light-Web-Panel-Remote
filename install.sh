#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p data
chmod 700 data
printf 'Installed on PC. Set ALICE_PANEL_TOKEN and run ./start.sh\n'
