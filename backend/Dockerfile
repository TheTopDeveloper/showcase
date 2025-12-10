# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Fix line endings and install dependencies
RUN dos2unix requirements.txt && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Fix any Windows line endings in Python files (exclude venv if it somehow got copied)
RUN find . -name "*.py" -not -path "*/venv/*" -not -path "*/env/*" -exec dos2unix {} \; 2>/dev/null || true

# Create directories (if needed for future use)
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Cloud Run sets PORT environment variable, default to 8000 for local
ENV PORT=8000
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Use PORT environment variable for Cloud Run compatibility
# Shell form to expand $PORT (Cloud Run sets PORT=8080)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
