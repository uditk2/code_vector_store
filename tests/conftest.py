import pytest

@pytest.fixture()
def test_fixture():
    # existing code
    pass

import os
import time
import subprocess
import signal
import socket
import redis

def is_port_in_use(port, host='localhost'):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def wait_for_redis(host='localhost', port=6379, timeout=30):
    """Wait for Redis to be available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            client = redis.Redis(host=host, port=port)
            client.ping()
            return True
        except redis.exceptions.ConnectionError:
            time.sleep(1)
    return False

@pytest.fixture(scope="session", autouse=True)
def ensure_redis_running():
    """Ensure Redis is running for tests"""
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = int(os.environ.get("REDIS_PORT", 6379))

    # Check if Redis is already running
    redis_running = wait_for_redis(host=redis_host, port=redis_port, timeout=5)

    if not redis_running:
        # Start Redis in a container for testing
        print("Starting Redis container for testing...")
        redis_process = subprocess.Popen(
            ["docker", "run", "--rm", "-p", f"{redis_port}:6379", "redis:latest"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

        # Wait for Redis to start
        if not wait_for_redis(host=redis_host, port=redis_port, timeout=30):
            os.killpg(os.getpgid(redis_process.pid), signal.SIGTERM)
            raise Exception("Failed to start Redis container")

        yield

        # Stop Redis container
        print("Stopping Redis container...")
        os.killpg(os.getpgid(redis_process.pid), signal.SIGTERM)
    else:
        yield

@pytest.fixture(scope="session", autouse=True)
def start_vector_store_service():
    """Start the vector store service for testing"""
    # Import here to avoid circular imports
    from app.startup import start_service
    import threading

    # Start the service in a separate thread
    service_thread = threading.Thread(target=start_service)
    service_thread.daemon = True
    service_thread.start()

    # Give the service time to start
    time.sleep(2)

    yield