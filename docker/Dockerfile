# Multi-stage Dockerfile for JobHunterAI Ecosystem

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci
COPY frontend/ ./frontend/
RUN cd frontend && npx vite build

# Stage 2: Production runner with optimized Python
FROM python:3.11-slim-bookworm AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Production Optimizations
ENV PYTHONOPTIMIZE=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN groupadd -r jobhunter && useradd -r -g jobhunter jobhunter

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium

# Copy Core and Backend modules
COPY core ./core
COPY backend ./backend

# Copy static frontend assets
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create directory for persistent data and logs
RUN mkdir -p /app/data /app/logs && chown -R jobhunter:jobhunter /app

# Switch to non-root user
USER jobhunter

# Environment variables
ENV PYTHONPATH=/app/core
ENV DATABASE_URL=sqlite:////app/data/jobhunter.db
ENV PORT=8000

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
