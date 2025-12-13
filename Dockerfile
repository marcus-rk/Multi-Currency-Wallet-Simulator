# Dockerfile for Multi-Currency Wallet Simulator
# Small, repeatable container build that can run the Flask API locally.

FROM python:3.11-slim

# Why these env vars:
# - keep containers stateless (no .pyc files),
# - make logs show up immediately in Docker logs,
# - avoid accidentally loading a host-specific DATABASE path from a committed .env.
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	FLASK_DEBUG=0 \
	DATABASE=/app/instance/wallet.db

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# SQLite file lives under /app/instance by default; ensure the directory exists.
RUN mkdir -p /app/instance

EXPOSE 5000

# Use the Flask application factory.
CMD ["flask", "--app", "app:create_app", "run", "--host=0.0.0.0", "--port=5000"]