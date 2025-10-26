# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies used by common plugins and MongoDB clients
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining application source
COPY . ./

# Ensure the startup script is executable
RUN chmod +x /app/start.sh

EXPOSE 5000

ENV FLASK_APP=app \
    FLASK_ENV=production

CMD ["/app/start.sh"]
