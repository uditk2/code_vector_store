import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
os.environ["CHROMA_DB_STORE"] = "/Users/uditkhandelwal/Documents/app_generator/chroma"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
from app.queue_manager import QueueManager
from app.config import Config
import uuid

queue_manager = QueueManager(send_queue_url=Config.VECTOR_STORE_QUEUE, receive_queue_url=Config.VECTOR_STORE_RESPONSE_QUEUE)
collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"

def message_handler(message:dict):
    print(message)

queue_manager.start_background_processing(message_handler=message_handler)

def test_delete_collection():
    """Test creating a collection"""
    collection_name =input("Provide collection name to delete:")
    # Send create collection message
    request_id = queue_manager.send_message({
        "action": "delete_collection",
        "collection_name": collection_name
    })
    print(request_id)

if __name__ == "__main__":
    test_delete_collection()
