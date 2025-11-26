# Dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Dependencias del sistema para psycopg2 y similares
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations

# Exponer puerto de FastAPI
EXPOSE 8000

# Solo levantar la API (las tablas se crean en startup)
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000

