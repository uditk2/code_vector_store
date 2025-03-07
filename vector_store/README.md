# Vector Store Service

A microservice that provides vector storage capabilities using ChromaDB with a Redis-based messaging interface.

## Overview

This service allows you to:
- Create vector collections
- Add data to collections
- Search across collections using vector similarity

The service uses Redis queues for communication, making it easy to integrate with other services.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)

## Project Structure

1. Start the services:

2. Modify the `.env` file to point to your existing Redis instance:

3. Start the Vector Store service:

### Add Data to a Collection

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| CHROMA_DB_STORE | Path to store ChromaDB data | /chroma |
| REDIS_HOST | Redis host | redis |
| REDIS_PORT | Redis port | 6379 |
| VECTOR_STORE_QUEUE | Queue for incoming requests | vector_store_queue |
| VECTOR_STORE_RESPONSE_QUEUE | Queue for responses | vector_store_response_queue |

## Development

### Local Setup

1. Create a virtual environment:

3. Set up environment variables:

## License

MIT License