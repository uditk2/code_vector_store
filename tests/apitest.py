import requests


def test_get_collection():
    response = requests.get(f"http://localhost:8000/collections")
    print(response)
    assert response.status_code == 200

if __name__ == "__main__":
    test_get_collection()