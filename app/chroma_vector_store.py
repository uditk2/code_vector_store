import chromadb
from typing import Dict, List, Any, Optional, Union
import uuid
from chromadb.utils import embedding_functions
import os
from app.logging.logging_config import get_logger

logger = get_logger()

class Config:
    CHROMA_DB_STORE = os.getenv("CHROMA_DB_STORE", "/chroma")

class ChromaVectorStore:
    """
    A vector store class that uses ChromaDB underneath to manage collections
    and provides simplified methods for adding data and searching across collections.
    """

    def __init__(self, client=None, embedding_function=None):
        """
        Initialize the ChromaVectorStore with an optional client and embedding function.

        Args:
            client: Optional ChromaDB client. If not provided, a new in-memory client will be created.
            embedding_function: Optional embedding function to use with ChromaDB.
        """
        self.client = client if client else chromadb.PersistentClient(Config.CHROMA_DB_STORE)
        if embedding_function is not None:
            self.embedding_function = embedding_function
        else:
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                                        model_name="all-mpnet-base-v2")
        self.collections = {}  # Dictionary to track created collections

    def create_collection(self, collection_name: str) -> Any:
        """
        Create a new collection in ChromaDB.

        Args:
            collection_name: Name of the collection to create

        Returns:
            The created collection object
        """
        if collection_name in self.collections:
            logger.info(f"Collection '{collection_name}' already exists. Returning existing collection.")
            return self.collections[collection_name]

        collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

        self.collections[collection_name] = collection
        return collection

    def get_collection(self, collection_name: str) -> Any:
        """
        Get an existing collection by name.

        Args:
            collection_name: Name of the collection to retrieve

        Returns:
            The collection object if it exists, None otherwise
        """
        if collection_name in self.collections:
            return self.collections[collection_name]

        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            self.collections[collection_name] = collection
            return collection
        except:
            print(f"Collection '{collection_name}' does not exist.")
            return None

    def add_dictionary(self, collection_name: str, dictionary: Dict[str, str]) -> None:
        """
        Add items from a dictionary to a collection. The keys will be stored in metadata
        and the values will be stored as documents.

        Args:
            collection_name: Name of the collection to add items to
            dictionary: Dictionary with keys as metadata and values as documents
        """
        collection = self.get_collection(collection_name)
        if not collection:
            collection = self.create_collection(collection_name)

        # Prepare data for batch addition
        ids = []
        documents = []
        metadatas = []

        for key, value in dictionary.items():
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
            documents.append(value)
            metadatas.append({"source": key})

        # Add data to collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        logger.info(f"Added {len(dictionary)} items to collection '{collection_name}'")

    def search(self, query: str, n_results: int = 25, collection_name=None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search the query across all collections.

        Args:
            query: The query string to search for
            n_results: Number of results to return from each collection

        Returns:
            Dictionary with collection names as keys and search results as values
        """
        if not self.collections:
            print("No collections available to search.")
            return {}
        if collection_name is None:
            raise ValueError("Please provide a collection name to search in.")
        collection = self.collections[collection_name]
        query_results = collection.query(
                query_texts=[query],
                n_results=n_results
            )

        # Format results for easier consumption
        formatted_results = []
        for i in range(len(query_results['ids'][0])):
            result = {
                "id": query_results['ids'][0][i],
                "document": query_results['documents'][0][i],
                "metadata": query_results['metadatas'][0][i],
                "distance": query_results.get('distances', [[]])[0][i] if query_results.get('distances') else None
            }
            formatted_results.append(result)

        return formatted_results

    def search_in_project(self, query: str, n_results: int = 25, user_id=None, project_base_path=None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search the query across all collections.

        Args:
            query: The query string to search for
            n_results: Number of results to return from each collection

        Returns:
            Dictionary with collection names as keys and search results as values
        """
        collection_name = self.get_collection_name(user_id=user_id, project_base_path=project_base_path)
        return self.search(query=query, n_results=n_results,collection_name=collection_name)

    def list_collections(self) -> List[str]:
        """List all collection names stored in this vector store.

        Returns:
            List of collection names
        """
        try:
            # Get all collections from the ChromaDB client
            all_collections = self.client.list_collections()
            # Update our local cache with any collections we didn't know about
            for collection in all_collections:
                collection_name = collection.name
                if collection_name not in self.collections:
                    self.collections[collection_name] = collection
            return [collection.name for collection in all_collections]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            # Fallback to the cached collections if there's an error
            return list(self.collections.keys())

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection by name.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        if collection_name in self.collections:
            self.client.delete_collection(collection_name)
            del self.collections[collection_name]
            return True
        return False

    def get_collection_name(self, user_id, project_base_path):
        sanitized_project_base_path = project_base_path.replace(os.sep, "_")
        collection_name = (sanitized_project_base_path + "_" + user_id).lower()[:60]
        return collection_name

    def is_collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in the vector store.

        Args:
            collection_name: Name of the collection to check

        Returns:
            True if the collection exists, False otherwise
        """
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            # Update the collections cache
            self.collections[collection_name] = collection
            return True
        except Exception:
            return False

chroma_vector_store = ChromaVectorStore()