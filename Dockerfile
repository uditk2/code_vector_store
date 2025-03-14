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

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f https://huggingface.co || exit 1
# Expose the API port
EXPOSE 8000

# Set command to run the application
CMD ["python", "-m", "app.main"]
