# Production Dockerfile
FROM python:3.11-slim

# Set working directory and Python path
WORKDIR /app
ENV PYTHONPATH=/app \
    TRANSFORMERS_CACHE=/app/.cache \
    HF_HOME=/app/.cache

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc python3-dev libpq-dev \
    wget libnss3 libnspr4 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Create cache directory
RUN mkdir -p /app/.cache && chmod 777 /app/.cache

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium && \
    playwright install-deps

# Copy application code
COPY . .

# Runtime config
ENV MODE=production \
    PORT=8000

EXPOSE $PORT
CMD ["sh", "-c", "uvicorn Runboth:app --host 0.0.0.0 --port ${PORT:-8000}"]
