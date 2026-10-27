#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
.venv/bin/pip install -r requirements.txt
printf 'Dependencies updated. Update source with git pull when desired.\n'
