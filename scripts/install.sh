#!/usr/bin/env bash
set -e

# ----------------------------------------
# Step 0: Clean previous venv
# ----------------------------------------
if [ -d ".venv" ]; then
    echo "🧹 Cleaning existing .venv..."
    rm -rf .venv
fi

# Optional: ensure pipenv creates venv inside project
export PIPENV_VENV_IN_PROJECT=1

# ----------------------------------------
# Step 1: Check pipenv
# ----------------------------------------
if ! command -v pipenv &> /dev/null; then
    echo "❌ pipenv not found. Install it first: pip install --user pipenv"
    exit 1
fi

# ----------------------------------------
# Step 2: Install Python version from pyenv
# ----------------------------------------
PYTHON_VERSION=$(cat .python-version)
echo "🐍 Installing Python $PYTHON_VERSION via pyenv (if not already installed)..."
pyenv install -s $PYTHON_VERSION

# ----------------------------------------
# Step 3: Create pipenv environment using pyenv Python
# ----------------------------------------
echo "🔧 Creating pipenv environment with Python $PYTHON_VERSION..."
pipenv --python $(pyenv which python)

# ----------------------------------------
# Step 4: Install project dependencies
# ----------------------------------------
echo "📦 Installing project dependencies..."
pipenv install --dev

echo "✅ Dependencies installed successfully!"
