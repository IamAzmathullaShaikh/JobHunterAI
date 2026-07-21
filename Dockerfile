# Multi-stage Dockerfile for JobHunterAI Ecosystem

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Note: Ensure vite.config.ts is set up to build to /dist
RUN npx vite build

# Stage 2: Production runtime with Python & Playwright
FROM python:3.11-slim-bookworm AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium

# Copy Core and Backend modules
COPY core ./core
COPY backend ./backend

# Copy static frontend assets
COPY --from=frontend-builder /app/dist ./frontend

# Create directory for persistent data
RUN mkdir -p /app/data

# Environment variables
ENV PYTHONPATH=/app/core
ENV DATABASE_URL=sqlite:////app/data/jobhunter.db
ENV PORT=8000

EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
