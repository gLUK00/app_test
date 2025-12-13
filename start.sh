#!/usr/bin/env bash
set -euo pipefail

# Allow overriding the bind address and port through environment variables
APP_HOST="${FLASK_HOST:-0.0.0.0}"
APP_PORT="${FLASK_PORT:-8080}"

if [ -f "/app/.env" ]; then
    # shellcheck disable=SC1091
    source /app/.env
fi

exec flask run --host="${APP_HOST}" --port="${APP_PORT}"
