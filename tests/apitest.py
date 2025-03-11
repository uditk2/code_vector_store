import requests
import sys
import time

def test_get_collection():
    try:
        print("Attempting to connect to vector store API...")
        response = requests.get("http://localhost:8000/collections", timeout=10)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        assert response.status_code == 200
        print("Test passed!")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        print("Make sure the vector store service is running on localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("Request timed out. The server might be overloaded or not responding.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def test_create_collection(collection_name):
    try:
        print("Attempting to connect to vector store API...")
        response = requests.get(f"http://localhost:8000/create_collection/{collection_name}", timeout=10)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.json()}")
        assert response.status_code == 200
        print("Test passed!")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        print("Make sure the vector store service is running on localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("Request timed out. The server might be overloaded or not responding.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False



def test_search_collection(collection_name):
    try:
        import requests
        api = "http://localhost:8000/"
        query = "update the redis store"
        data = {
                "query": query,
                "collection_name": collection_name,
                "n_results": 25
            }
        response = requests.post(f"{api}/search", json=data)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.json()}")
        assert response.status_code == 200
        print("Test passed!")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        print("Make sure the vector store service is running on localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("Request timed out. The server might be overloaded or not responding.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
if __name__ == "__main__":
    success = test_get_collection()
    if not success:
        sys.exit(1)
    collection_name=input("Provide a collection name to create:")
    success = test_create_collection(collection_name=collection_name)
    if not success:
        sys.exit(1)
    collection_name=input("Provide collection name to search in:")
    success = test_search_collection(collection_name)
    if not success:
        sys.exit(1)