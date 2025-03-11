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
import requests

queue_manager = QueueManager(send_queue_url=Config.VECTOR_STORE_QUEUE, receive_queue_url=Config.VECTOR_STORE_RESPONSE_QUEUE)
collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
def message_handler(message:dict):
    print(message)
    action = message["action"]
    if action == "search":
        test_delete_collection()

queue_manager.start_background_processing(message_handler=message_handler)

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


def test_delete_collection():
    """Test creating a collection"""
    collection_name =input("Provide collection name to delete:")
    # Send create collection message
    request_id = queue_manager.send_message({
        "action": "delete_collection",
        "collection_name": collection_name
    })
    print(request_id)

def test_add_document_to_collection(message):
        # Send create collection message
    request_id = queue_manager.send_message(message)
    print(request_id)

def test_search_in_collection(collection_name, query):
    request_id = queue_manager.send_message({
        "action": "search",
        "collection_name": collection_name,
        "query": query
    })
    print(request_id)

if __name__ == "__main__":
    test_create_collection(collection_name)
    test_add_document_to_collection({'action': 'add_data', 'data': {'/workspace/uditk2@gmail.com/MagentoEcommerceWebsite/Dockerfile': "The Dockerfile for the Magento project is designed to create a containerized environment that facilitates the running of a Magento eCommerce website. It performs several tasks including setting up the PHP environment with version 8.1 and installing various essential system dependencies like libicu-dev, libxml2-dev, and others necessary for Magento's operation. This is accomplished through commands that update the package list and install the required libraries, followed by enabling specific PHP extensions such as intl, soap, and pdo_mysql using the docker-php-ext-install command. Additionally, it configures Apache by enabling the rewrite module and sets the working directory to /var/www/html, which is where the Magento files will reside. Composer, a dependency manager for PHP, is also installed to manage project libraries efficiently. The Dockerfile further increases the PHP memory limit to 2G to accommodate Magento's resource requirements, and it exposes port 80 for web access. Lastly, it ensures that the Apache server runs in the foreground when the container starts. This entire setup is supported by the docker-compose.yml file in the project structure, which orchestrates the container's deployment and networking, ensuring that all components work seamlessly together.", '/workspace/uditk2@gmail.com/MagentoEcommerceWebsite/.dockerignore': 'The project structure of the Magento eCommerce website includes several important files that serve distinct purposes. The `.gitignore` file plays a key role in specifying which files should be excluded from version control, such as temporary files and environment directories, thus maintaining a clean repository. The `Dockerfile` is designed to define the application environment by detailing the base image, necessary dependencies, and commands for setting up the application. Meanwhile, the `docker-compose.yml` file orchestrates the integration of multiple Docker containers, ensuring that different services, such as the web server and database, function cohesively. The `.env` file stores environment variables used to configure the application, allowing sensitive information to be managed securely without hardcoding it. Additionally, the `README.md` file provides essential documentation and guidance for developers and users on setting up and using the project. Together, these files contribute to a streamlined development and deployment process, with each file fulfilling a specific role that enhances collaboration and efficiency within the project.', '/workspace/uditk2@gmail.com/MagentoEcommerceWebsite/.env': "The provided file is an environment variables configuration file (.env) that plays a crucial role in the Magento Ecommerce website project by storing sensitive credentials and configuration settings necessary for various external services and APIs. Its primary tasks include securely managing API keys for services such as OpenAI, Google Cloud, AWS, and Azure, as well as setting configurations for Redis and Docker. It accomplishes these tasks through key-value pairs, which the application can access at runtime, ensuring that critical information remains separate from the codebase for enhanced security and maintainability. In the current project structure, the `src/` directory likely contains the application code that interacts with these environment variables to connect with external services and handle functionalities like chat history and deployment updates. Furthermore, the configuration supports the Docker environment by specifying settings for services like Redis and SQS queues, which are essential for the project's microservices architecture, facilitating efficient communication and data management within the application.", '/workspace/uditk2@gmail.com/MagentoEcommerceWebsite/docker-compose.yml': 'The provided code file is a Docker Compose configuration that orchestrates multiple services for a Magento eCommerce website. It primarily sets up a web service using Flask in development mode, enabling debugging and defining server settings and workspace paths via environmental variables. The web service utilizes mounted volumes for application code, logs, and Docker socket access, which facilitate container communication and file sharing. Additionally, it specifies dependencies on Redis, MariaDB, and Elasticsearch services, ensuring these components are available before the web service starts. Redis manages caching, while MariaDB serves as the database, configured with specific user credentials and data persistence through a volume. Elasticsearch is employed for search functionalities, with memory settings to optimize performance. All services are organized under a single network called "webnet" to ensure seamless communication among them. Overall, this configuration file is essential for deploying and managing the entire application stack, leveraging Docker\'s capabilities to create an efficient development environment, while the services defined within the file work collaboratively to support the Magento eCommerce website.'}, 'collection_name': collection_name})
    test_search_in_collection(collection_name=collection_name, query="How do I update redis?")
