# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# Multi-stage build for Next.js + FastAPI with dual server setup

# Stage 1: Build Next.js frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY securecheck-pro/frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY securecheck-pro/frontend/ ./

# Set environment variable for production build
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Stage 2: Full stack setup with supervisor
FROM node:18-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Python and supervisor
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    supervisor \
    nginx \
    curl \
    git \
    wget \
    fonts-liberation \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Create user and setup permissions
RUN useradd -m -u 1001 appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

# Setup Git configuration
RUN git config --global --add safe.directory '*' || true
RUN git config --global user.name "Hugging Face User" || true
RUN git config --global user.email "user@huggingface.co" || true

# Copy backend requirements and install Python dependencies
COPY securecheck-pro/backend/requirements.txt ./backend/
RUN pip3 install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code
COPY securecheck-pro/backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
COPY --from=frontend-builder /app/frontend/next.config.ts ./frontend/
COPY securecheck-pro/frontend/src ./frontend/src

# Install frontend production dependencies
WORKDIR /app/frontend
RUN npm ci --only=production
WORKDIR /app

# Create nginx configuration
RUN echo 'server { \
    listen 7860; \
    location / { \
        proxy_pass http://localhost:3000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_cache_bypass $http_upgrade; \
    } \
    location /api/v1/ { \
        proxy_pass http://localhost:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/sites-available/default

# Create supervisor configuration
RUN echo '[supervisord] \
nodaemon=true \
user=root \
\
[program:nginx] \
command=nginx -g "daemon off;" \
autostart=true \
autorestart=true \
\
[program:nextjs] \
command=npm start \
directory=/app/frontend \
user=appuser \
environment=PORT=3000 \
autostart=true \
autorestart=true \
\
[program:fastapi] \
command=python3 main.py \
directory=/app/backend \
user=appuser \
environment=PYTHONPATH=/app/backend \
autostart=true \
autorestart=true' > /etc/supervisor/conf.d/supervisord.conf

# Set proper ownership
RUN chown -R appuser:appuser /app

# Create temp directories with proper permissions
RUN mkdir -p /tmp/reports /tmp/screenshots && chmod 777 /tmp/reports /tmp/screenshots

# Expose port (Hugging Face Spaces standard)
EXPOSE 7860

# Run supervisor to manage all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]