# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# Multi-stage build optimized for Hugging Face Spaces

# Stage 1: Build Next.js frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY securecheck-pro/frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY securecheck-pro/frontend/ ./

# Set environment variables for production build
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=""

# Build the application
RUN npm run build

# Stage 2: Python backend with static files
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including those needed for PDF generation
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    git \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Create user and home directory to avoid permission issues
RUN useradd -m -u 1000 appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

# Setup Git configuration with proper permissions
RUN git config --global --add safe.directory '*' || true
RUN git config --global user.name "Hugging Face User" || true
RUN git config --global user.email "user@huggingface.co" || true

# Copy requirements first for better caching
COPY securecheck-pro/backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY securecheck-pro/backend/ .

# Copy built frontend files (Next.js standalone build)
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
COPY --from=frontend-builder /app/frontend/public ./public

# Set proper ownership for the app directory
RUN chown -R appuser:appuser /app

# Create reports and temp directories with proper permissions
RUN mkdir -p /tmp/reports /tmp/screenshots && chmod 777 /tmp/reports /tmp/screenshots

# Set environment variables
ENV HOME=/home/appuser
ENV PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Expose port (Hugging Face Spaces standard)
EXPOSE 7860

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]