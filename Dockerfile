# ==============================
# Stage 1: Development
# ==============================
FROM python:3.12-slim AS development

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages like psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential curl gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Pipfile for caching
COPY Pipfile Pipfile.lock /app/

# Install pipenv and development dependencies inside project venv
RUN pip install --no-cache-dir pipenv \
    && PIPENV_VENV_IN_PROJECT=1 pipenv install --dev

# Copy source code
COPY src /app/src

# Copy environment files
COPY environments /app/environments

# Expose port for FastAPI
EXPOSE 80

# Default CMD for development (hot reload)
CMD ["pipenv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

# ==============================
# Stage 2: Production
# ==============================
FROM python:3.12-slim AS production

WORKDIR /app

# Install system dependencies for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    build-essential gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Pipfile for caching
COPY Pipfile Pipfile.lock /app/

# Install pipenv and only production dependencies
RUN pip install --no-cache-dir pipenv \
    && PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile

# Copy source code
COPY src /app/src

# Copy environment files
COPY environments /app/environments

# Expose port
EXPOSE 80

# Run production server (no reload)
CMD ["pipenv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
