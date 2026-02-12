# Multi-stage build for lightweight production image
# Stage 1: Builder - Install dependencies
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Create final lightweight image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8080

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Cloud Run will override with PORT env var)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Run with Gunicorn for production with multiple workers
# Using uvicorn workers for async support
CMD gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WORKERS:-4} \
    --threads ${THREADS:-2} \
    --bind 0.0.0.0:${PORT} \
    --timeout ${TIMEOUT:-300} \
    --graceful-timeout ${GRACEFUL_TIMEOUT:-30} \
    --keep-alive ${KEEP_ALIVE:-5} \
    --max-requests ${MAX_REQUESTS:-1000} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info}

