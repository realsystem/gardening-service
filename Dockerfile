# Multi-stage build for production-ready container
# Base image: Python 3.12 slim (minimal dependencies)
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for Python packages
# - gcc: for building Python extensions (passlib, psycopg2)
# - libpq-dev: PostgreSQL development libraries for psycopg2
# - postgresql-client: for database connectivity
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies with retry logic and timeout
# Use multiple attempts with fallback mirrors for reliability
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        --retries 10 \
        --timeout 120 \
        --index-url https://pypi.org/simple \
        --extra-index-url https://pypi.python.org/simple \
        -r requirements.txt


# Production stage - minimal image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies for psycopg2 and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port (configurable via environment)
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()"

# Startup script runs migrations then starts server
CMD ["./start.sh"]
