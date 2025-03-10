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
    action = message["action"]
    if action == "search":
        test_delete_collection(collection_name=collection_name)

queue_manager.start_background_processing(message_handler=message_handler)

def test_create_collection(collection_name):
    """Test creating a collection"""

    # Send create collection message
    request_id = queue_manager.send_message({
        "action": "create_collection",
        "collection_name": collection_name
    })
    print(request_id)

def test_delete_collection(collection_name):
    """Test creating a collection"""

    # Send create collection message
    request_id = queue_manager.send_message({
        "action": "delete_collection",
        "collection_name": collection_name
    })
    print(request_id)

def test_add_document_to_collection(collection_name, data):
        # Send create collection message
    request_id = queue_manager.send_message({
        "action": "add_data",
        "collection_name": collection_name,
        "data": data
    })
    print(request_id)

def test_search_in_collection(collection_name, query):
    request_id = queue_manager.send_message({
        "action": "search",
        "collection_name": collection_name,
        "query": query
    })
    print(request_id)

if __name__ == "__main__":
    test_delete_collection("test_collection_6346e99f")
    test_delete_collection("test_collection_e3fa0076")
    
    test_create_collection(collection_name)
    test_add_document_to_collection(collection_name=collection_name, data= {
        "testfile1": "This is storing just the temp data",
        "test_file2": "This is storing another temp data"
    })
    test_search_in_collection(collection_name=collection_name, query="I need temp")
