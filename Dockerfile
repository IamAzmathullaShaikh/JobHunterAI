# Multi-stage Dockerfile for production-ready TypeScript + Vite full-stack app

# Stage 1: Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first to leverage Docker layer caching
COPY package*.json ./

# Install all dependencies (including devDependencies)
RUN npm ci

# Copy application source code
COPY . .

# Build the client static assets and bundle the server using esbuild
RUN npm run build

# Stage 2: Production runtime stage
FROM node:20-bookworm-slim AS runner

# Python runtime for the real scraper fleet (Playwright needs a glibc base,
# so we use Debian slim rather than Alpine/musl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV DB_PATH=/app/data/db.json

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --omit=dev

# Python scraper dependencies + Chromium browser for the fleet
COPY requirements.txt ./
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt \
    && python3 -m playwright install --with-deps chromium
COPY scrapers ./scrapers
COPY schemas ./schemas
COPY scripts ./scripts
COPY config ./config

# Copy compiled production assets and bundled server from the builder stage
COPY --from=builder /app/dist ./dist

# Create directory for persistent data
RUN mkdir -p /app/data

# Expose port 3000 for server traffic
EXPOSE 3000

# Start the application
CMD ["node", "dist/server.cjs"]
