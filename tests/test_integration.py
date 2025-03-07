import pytest
import json
import time
import os
import uuid
import redis
from typing import Dict, Any

# Set environment variables for testing
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["CHROMA_DB_STORE"] = "/tmp/chroma_test"

# Test configuration
TEST_VECTOR_STORE_QUEUE = "vector_store_queue_test"
TEST_VECTOR_STORE_RESPONSE_QUEUE = "vector_store_response_queue_test"

class TestVectorStoreIntegration:
    @pytest.fixture(scope="session", autouse=True)
    def setup_environment(self):
        """Set up environment variables for testing"""
        original_queue = os.environ.get("VECTOR_STORE_QUEUE")
        original_response_queue = os.environ.get("VECTOR_STORE_RESPONSE_QUEUE")

        os.environ["VECTOR_STORE_QUEUE"] = TEST_VECTOR_STORE_QUEUE
        os.environ["VECTOR_STORE_RESPONSE_QUEUE"] = TEST_VECTOR_STORE_RESPONSE_QUEUE

        yield

        # Restore original environment variables
        if original_queue:
            os.environ["VECTOR_STORE_QUEUE"] = original_queue
        else:
            del os.environ["VECTOR_STORE_QUEUE"]

        if original_response_queue:
            os.environ["VECTOR_STORE_RESPONSE_QUEUE"] = original_response_queue
        else:
            del os.environ["VECTOR_STORE_RESPONSE_QUEUE"]

    @pytest.fixture(scope="class")
    def redis_client(self):
        """Create a Redis client for testing"""
        client = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=int(os.environ["REDIS_PORT"])
        )

        # Clear test queues
        client.delete(TEST_VECTOR_STORE_QUEUE)
        client.delete(TEST_VECTOR_STORE_RESPONSE_QUEUE)

        yield client

        # Clean up
        client.delete(TEST_VECTOR_STORE_QUEUE)
        client.delete(TEST_VECTOR_STORE_RESPONSE_QUEUE)

    def send_message(self, redis_client, message: Dict[str, Any]) -> str:
        """Send a message to the vector store queue"""
        request_id = str(uuid.uuid4())
        message["request_id"] = request_id

        redis_client.rpush(
            TEST_VECTOR_STORE_QUEUE,
            json.dumps(message)
        )

        return request_id

    def get_response(self, redis_client, request_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Get response from the vector store response queue"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check for responses
            result = redis_client.blpop(TEST_VECTOR_STORE_RESPONSE_QUEUE, timeout=1)
            if result is None:
                continue

            _, data = result
            if isinstance(data, bytes):
                data = data.decode('utf-8')

            response = json.loads(data)

            if response.get("request_id") == request_id:
                return response

        raise TimeoutError(f"No response received for request {request_id} within {timeout} seconds")

    def test_create_collection(self, redis_client):
        """Test creating a collection"""
        collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"

        # Send create collection message
        request_id = self.send_message(redis_client, {
            "action": "create_collection",
            "collection_name": collection_name
        })

        # Get response
        response = self.get_response(redis_client, request_id)

        # Verify response
        assert response["status"] == "success"
        assert f"Collection {collection_name} created" in response["message"]
import pytest
import json
import time
import os
import uuid
import redis
from typing import Dict, Any

# Set environment variables for testing
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["CHROMA_DB_STORE"] = "/tmp/chroma_test"

# Test configuration
TEST_VECTOR_STORE_QUEUE = "vector_store_queue_test"
TEST_VECTOR_STORE_RESPONSE_QUEUE = "vector_store_response_queue_test"

class TestVectorStoreIntegration:
    @pytest.fixture(scope="session", autouse=True)
    def setup_environment(self):
        """Set up environment variables for testing"""
        original_queue = os.environ.get("VECTOR_STORE_QUEUE")
        original_response_queue = os.environ.get("VECTOR_STORE_RESPONSE_QUEUE")

        os.environ["VECTOR_STORE_QUEUE"] = TEST_VECTOR_STORE_QUEUE
        os.environ["VECTOR_STORE_RESPONSE_QUEUE"] = TEST_VECTOR_STORE_RESPONSE_QUEUE

        yield

        # Restore original environment variables
        if original_queue:
            os.environ["VECTOR_STORE_QUEUE"] = original_queue
        else:
            del os.environ["VECTOR_STORE_QUEUE"]

        if original_response_queue:
            os.environ["VECTOR_STORE_RESPONSE_QUEUE"] = original_response_queue
        else:
            del os.environ["VECTOR_STORE_RESPONSE_QUEUE"]

    @pytest.fixture(scope="class")
    def redis_client(self):
        """Create a Redis client for testing"""
        client = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=int(os.environ["REDIS_PORT"])
        )

        # Clear test queues
        client.delete(TEST_VECTOR_STORE_QUEUE)
        client.delete(TEST_VECTOR_STORE_RESPONSE_QUEUE)

        yield client

        # Clean up
        client.delete(TEST_VECTOR_STORE_QUEUE)
        client.delete(TEST_VECTOR_STORE_RESPONSE_QUEUE)

    def send_message(self, redis_client, message: Dict[str, Any]) -> str:
        """Send a message to the vector store queue"""
        request_id = str(uuid.uuid4())
        message["request_id"] = request_id

        redis_client.rpush(
            TEST_VECTOR_STORE_QUEUE,
            json.dumps(message)
        )

        return request_id

    def get_response(self, redis_client, request_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Get response from the vector store response queue"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check for responses
            result = redis_client.blpop(TEST_VECTOR_STORE_RESPONSE_QUEUE, timeout=1)
            if result is None:
                continue

            _, data = result
            if isinstance(data, bytes):
                data = data.decode('utf-8')

            response = json.loads(data)

            if response.get("request_id") == request_id:
                return response

        raise TimeoutError(f"No response received for request {request_id} within {timeout} seconds")

    def test_create_collection(self, redis_client):
        """Test creating a collection"""
        collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"

        # Send create collection message
        request_id = self.send_message(redis_client, {
            "action": "create_collection",
            "collection_name": collection_name
        })

        # Get response
        response = self.get_response(redis_client, request_id)

        # Verify response
        assert response["status"] == "success"
        assert f"Collection {collection_name} created" in response["message"]

    def test_add_data_to_collection(self, redis_client):
        """Test adding data to a collection"""
        collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"

        # First create the collection
        request_id = self.send_message(redis_client, {
            "action": "create_collection",
            "collection_name": collection_name
        })
        self.get_response(redis_client, request_id)

        # Add data to the collection
        test_data = {
            "doc1": "This is a test document about artificial intelligence.",
            "doc2": "Vector databases are useful for semantic search.",
            "doc3": "ChromaDB is a vector database for AI applications."
        }

        request_id = self.send_message(redis_client, {
            "action": "add_data",
            "collection_name": collection_name,
            "data": test_data
        })

        # Get response
        response = self.get_response(redis_client, request_id)

        # Verify response
        assert response["status"] == "success"
        assert f"Added {len(test_data)} items to {collection_name}" in response["message"]

    def test_search_in_collection(self, redis_client):
        """Test searching in a collection"""
        collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"

        # First create the collection
        request_id = self.send_message(redis_client, {
            "action": "create_collection",
            "collection_name": collection_name
        })
        self.get_response(redis_client, request_id)

        # Add data to the collection
        test_data = {
            "doc1": "This is a test document about artificial intelligence.",
            "doc2": "Vector databases are useful for semantic search.",
            "doc3": "ChromaDB is a vector database for AI applications."
        }

        request_id = self.send_message(redis_client, {
            "action": "add_data",
            "collection_name": collection_name,
            "data": test_data
        })
        self.get_response(redis_client, request_id)

        # Search in the collection
        search_query = "AI and machine learning"
        request_id = self.send_message(redis_client, {
            "action": "search",
            "collection_name": collection_name,
            "query": search_query,
            "n_results": 2
        })

        # Get response
        response = self.get_response(redis_client, request_id)

        # Verify response
        assert response["status"] == "success"
        assert "results" in response
        assert len(response["results"]) <= 2  # Should return at most 2 results

        # Verify that results contain expected fields
        for result in response["results"]:
            assert "id" in result
            assert "document" in result
            assert "metadata" in result
            assert "distance" in result

    def test_error_handling_missing_collection(self, redis_client):
        """Test error handling when collection name is missing"""
        request_id = self.send_message(redis_client, {
            "action": "search",
            "query": "test query"
            # Missing collection_name
        })

        # Get response
        response = self.get_response(redis_client, request_id)

        # Verify error response
        assert response["status"] == "error"
        assert "Missing collection_name" in response["error"]

    def test_error_handling_unknown_action(self, redis_client):
        """Test error handling for unknown action"""
        request_id = self.send_message(redis_client, {
            "action": "invalid_action",
            "collection_name": "test_collection"
        })

        # Get response
        response = self.get_response(redis_client, request_id)

        # Verify error response
        assert response["status"] == "error"
        assert "Unknown action" in response["error"]
    # existing code