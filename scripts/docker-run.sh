#!/usr/bin/env bash
set -e

# ==============================
# Variables (can be overridden from Makefile or CLI)
# ==============================
APP_NAME="${APP_NAME:-fastapi-skel}"
PORT="${PORT:-10000}"
STAGE="${STAGE:-development}"
ENV="${ENV:-dev}"

# ==============================
# Stop previous container (if exists)
# ==============================
echo "🛑 Stopping previous container…"
docker stop "$APP_NAME" >/dev/null 2>&1 || true
docker rm "$APP_NAME" >/dev/null 2>&1 || true

# ==============================
# Build Docker image
# ==============================
echo "🔨 Building Docker image '$APP_NAME:$STAGE'…"
docker build --target "$STAGE" -t "$APP_NAME:$STAGE" .

# ==============================
# Run Docker container
# ==============================
echo "🚀 Running container '$APP_NAME' on port $PORT with ENV='$ENV'…"
docker run -d --rm \
    --name "$APP_NAME" \
    -e ENV="$ENV" \
    -p "$PORT:80" \
    "$APP_NAME:$STAGE"

echo "✅ Container running at http://localhost:$PORT"
