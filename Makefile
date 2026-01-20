# Default environment (can be overridden from CLI)
ENV ?= dev

# Source code directories
SRC := src

APP_NAME=fastapi_app
VENV_DIR=.venv

.PHONY: help install run dev shell docker-run clean

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install project dependencies"
	@echo "  make run            Run FastAPI server"
	@echo "  make format         Format project"
	@echo "  make lint           Project lint scan"
	@echo "  make typecheck      Type errors in project"
	@echo "  make check          Check lint, typecheck and test code and format project"

	@echo "  make shell          Enter pipenv shell"
	@echo "  make docker-run     Run project in Docker"
	@echo "  make clean          Cleanup project"
	@echo ""

install:
	./scripts/install.sh

run:
	./scripts/run.sh

shell:
	pipenv shell

docker-run:
	ENV=$(ENV) ./scripts/docker-run.sh

# -----------------------------
# Format code using black & isort
# -----------------------------
format:
	@echo "📦 Formatting code with black and isort..."
	isort $(SRC)
	black $(SRC)

# -----------------------------
# Lint code using pylint
# -----------------------------
lint:
	@echo "🧹 Linting code with pylint..."
	pylint $(SRC)

# -----------------------------
# Type checking using mypy
# -----------------------------
typecheck:
	@echo "🔍 Running mypy type checks..."
	mypy $(SRC)

# -----------------------------
# Run all checks (format, lint, typecheck)
# -----------------------------
check: format lint typecheck
	@echo "✅ All checks passed!"


clean:
	@echo "🧹 Cleaning project…"

	# Remove pipenv virtualenv
	-pipenv --rm >/dev/null 2>&1 || true

	# Remove local venv if exists
	rm -rf $(VENV_DIR)

	# Remove Python cache files
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -type f -delete
	find . -name "*.pyo" -type f -delete

	# Stop and remove docker container (optional)
	-docker stop $(APP_NAME) >/dev/null 2>&1 || true
	-docker rm $(APP_NAME) >/dev/null 2>&1 || true

	@echo "✅ Project cleaned"
