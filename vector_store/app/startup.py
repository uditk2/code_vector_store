import os
import time
from app.chroma_vector_store import chroma_vector_store
from app.queue_manager import QueueManager
from app.logging.logging_config import get_logger
import json

logger = get_logger()

class Config:
    VECTOR_STORE_QUEUE = os.getenv("VECTOR_STORE_QUEUE", "vector_store_queue")
    VECTOR_STORE_RESPONSE_QUEUE = os.getenv("VECTOR_STORE_RESPONSE_QUEUE", "vector_store_response_queue")

def message_handler(message):
    """
    Handle incoming messages from the queue

    Args:
        message: The message received from the queue
    """
    try:
        logger.info(f"Received message: {message}")

        if isinstance(message, str):
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse message as JSON: {message}")
                return

        # Process message based on action
        action = message.get('action')
        if not action:
            logger.error("Message missing 'action' field")
            return

        response = {"request_id": message.get("request_id", "unknown")}

        if action == "create_collection":
            collection_name = message.get('collection_name')
            if not collection_name:
                response["status"] = "error"
                response["error"] = "Missing collection_name"
            else:
                chroma_vector_store.create_collection(collection_name)
                response["status"] = "success"
                response["message"] = f"Collection {collection_name} created"

        elif action == "add_data":
            collection_name = message.get('collection_name')
            data = message.get('data')
            if not collection_name or not data:
                response["status"] = "error"
                response["error"] = "Missing collection_name or data"
            else:
                chroma_vector_store.add_dictionary(collection_name, data)
                response["status"] = "success"
                response["message"] = f"Added {len(data)} items to {collection_name}"

        elif action == "search":
            collection_name = message.get('collection_name')
            query = message.get('query')
            n_results = message.get('n_results', 25)
            if not collection_name or not query:
                response["status"] = "error"
                response["error"] = "Missing collection_name or query"
            else:
                results = chroma_vector_store.search(query, n_results, collection_name)
                response["status"] = "success"
                response["results"] = results

        else:
            response["status"] = "error"
            response["error"] = f"Unknown action: {action}"

        # Send response if response queue is configured
        if Config.VECTOR_STORE_RESPONSE_QUEUE:
            queue_manager = QueueManager(send_queue_url=Config.VECTOR_STORE_RESPONSE_QUEUE)
            queue_manager.send_message(response)

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)

        # Try to send error response
        if Config.VECTOR_STORE_RESPONSE_QUEUE:
            try:
                error_response = {
                    "request_id": message.get("request_id", "unknown") if isinstance(message, dict) else "unknown",
                    "status": "error",
                    "error": str(e)
                }
                queue_manager = QueueManager(send_queue_url=Config.VECTOR_STORE_RESPONSE_QUEUE)
                queue_manager.send_message(error_response)
            except Exception:
                logger.error("Failed to send error response", exc_info=True)

def start_service():
    """
    Start the vector store service
    """
    logger.info("Starting Vector Store service...")

    # Wait for Redis to be available
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = os.getenv("REDIS_PORT", "6379")

    logger.info(f"Connecting to Redis at {redis_host}:{redis_port}")

    # Initialize queue manager for receiving messages
    queue_manager = QueueManager(receive_queue_url=Config.VECTOR_STORE_QUEUE)

    # Start listening for messages
    logger.info(f"Starting to listen for messages on queue: {Config.VECTOR_STORE_QUEUE}")
    queue_manager.start_background_processing(message_handler)

    logger.info("Vector Store service started successfully")

    # Keep the service running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down Vector Store service...")