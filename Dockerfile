# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for Chroma DB persistence
RUN mkdir -p /chroma

# Set environment variables from .env file
ENV CHROMA_DB_STORE=/chroma
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV VECTOR_STORE_QUEUE=vector_store_queue
ENV VECTOR_STORE_RESPONSE_QUEUE=vector_store_response_queue

# Create entrypoint script
RUN echo '#!/bin/bash\n\necho "Waiting for Redis to be ready..."\n\nuntil python -c "import redis; redis.Redis(host=\\"$REDIS_HOST\\", port=$REDIS_PORT).ping()" 2>/dev/null; do\n\n  echo "Redis not ready yet, waiting..."\n\n  sleep 1\n\n\ndone\necho "Redis is ready, starting application..."\nexec python -m app.main\n' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]