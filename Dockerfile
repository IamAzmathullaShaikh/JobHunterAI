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
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV DB_PATH=/app/data/db.json

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --omit=dev

# Copy compiled production assets and bundled server from the builder stage
COPY --from=builder /app/dist ./dist

# Create directory for persistent data
RUN mkdir -p /app/data

# Expose port 3000 for server traffic
EXPOSE 3000

# Start the application
CMD ["node", "dist/server.cjs"]
