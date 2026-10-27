#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
rm -rf .venv
printf 'Application environment removed. PC settings in data/ retained.\n'
