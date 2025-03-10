import os
class Config:
    VECTOR_STORE_QUEUE = os.getenv("VECTOR_STORE_QUEUE", "vector_store_queue")
    VECTOR_STORE_RESPONSE_QUEUE = os.getenv("VECTOR_STORE_RESPONSE_QUEUE", "vector_store_response_queue")