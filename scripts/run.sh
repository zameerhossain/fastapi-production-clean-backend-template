#!/usr/bin/env bash
set -e

# Ensure pipenv creates venv inside project
export PIPENV_VENV_IN_PROJECT=1

# Go to project root
cd "$(dirname "$0")/.."

# Check if pipenv venv exists
VENV=$(pipenv --venv 2>/dev/null || true)
if [[ -z "$VENV" ]]; then
  echo "🚀 Please run 'make install' first"
  exit 1
fi

echo "🚀 Starting FastAPI server..."
pipenv run uvicorn src.main:app --reload-dir src --reload --port 8000
