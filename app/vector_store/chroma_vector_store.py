import chromadb
from typing import Dict, List, Any, Optional, Union
import uuid
from sentence_transformers import SentenceTransformer
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
        self.client = client if client else chromadb.PersistentClient(path=Config.CHROMA_DB_STORE)
        if embedding_function is not None:
            self.embedding_function = embedding_function
        else:
            self.embedding_function = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    def create_collection(self, collection_name: str) -> Any:
        """
        Create a new collection in ChromaDB.

        Args:
            collection_name: Name of the collection to create

        Returns:
            The created collection object
        """
        collection = self.get_collection(collection_name=collection_name)
        if collection is not None:
            logger.warning(f"Collection '{collection_name}' already exists. Returning existing collection.")
            return collection

        collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

        return collection

    def get_collection(self, collection_name: str) -> Any:
        """
        Get an existing collection by name.

        Args:
            collection_name: Name of the collection to retrieve

        Returns:
            The collection object if it exists, None otherwise
        """
        if collection_name in self.client.list_collections():
            return self.client.get_collection(name=collection_name)
        logger.warning(f"Collection '{collection_name}' does not exist.")
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
        if  len(self.list_collections()) == 0:
            logger.warning("No collections available to search.")
            return {}
        if collection_name is None or self.get_collection(collection_name=collection_name) is None:
            raise ValueError("Please provide a valid collection to search in.")
        collection = self.get_collection(collection_name=collection_name)

        query_results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
        logger.info(f"Results {query_results}")
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
        """
        List all collection names stored in this vector store.

        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        if collections is None or len(collections)== 0:
            return []
        return collections

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection by name.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        collection = self.get_collection(collection_name=collection_name)
        if collection is None:
            logger.warning(f"Collection with {collection_name} does not exist")
            return False
        self.client.delete_collection(name=collection_name)
        logger.info("Collection deleted successfully")
        return True

    def get_collection_name(self, user_id, project_base_path):
        sanitized_project_base_path = project_base_path.replace(os.sep, "_")
        collection_name = (sanitized_project_base_path + "_" + user_id).lower()[:60]
        return collection_name

chroma_vector_store = ChromaVectorStore()