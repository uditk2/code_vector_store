import requests
import sys
import time

def test_create_collection(collection_name):
    try:
        print("Attempting to connect to vector store API...")
        params = {"collection_name": collection_name}
        url = "http://localhost:8000/collections"
        response = requests.post(url, params=params, timeout=10)
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
def test_collection_exists(collection_name):
    try:
        print("Attempting to connect to vector store API...")
        response = requests.get(f"http://localhost:8000/collections/{collection_name}/exists", timeout=10)
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
def test_get_collections():
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


def test_add_to_collection(collection_name):
    try:
        import requests
        api = "http://localhost:8000/"
        test_data = {
        "item_dict": {
            "id1": "test item 1",
            "id2": "test item 2"
        }
        }
        response = requests.post(f"{api}/collections/{collection_name}/items", json=test_data)
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


def test_search_collection(collection_name):
    try:
        import requests
        api = "http://localhost:8000/"
        query = "update the redis store"
        data = {
                "query": query,
                "n_results": 25
            }
        response = requests.post(f"{api}/collections/{collection_name}/search", json=data)
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
    
def test_delete_collection(collection_name):
    try:
        print("Attempting to connect to vector store API...")
        response = requests.delete(f"http://localhost:8000/collections/{collection_name}", timeout=10)
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

if __name__ == "__main__":
    collection_name = "test_collection"
    test_create_collection(collection_name=collection_name)
    test_get_collections()
    test_collection_exists(collection_name=collection_name)
    test_add_to_collection(collection_name=collection_name)
    test_search_collection(collection_name=collection_name)
    test_delete_collection(collection_name=collection_name)