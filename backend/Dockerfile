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

# Fix any Windows line endings in Python files
RUN find . -name "*.py" -exec dos2unix {} \;

# Create directories
RUN mkdir -p /app/chroma_db /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
