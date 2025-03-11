from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.vector_store.chroma_vector_store import chroma_vector_store
from app.startup import start_service
from pydantic import BaseModel
from app.logging.logging_config import get_logger
import uvicorn
logger = get_logger()

app = FastAPI(title="Vector Store API", description="API for interacting with ChromaDB vector store")

class SearchRequest(BaseModel):
    query: str
    collection_name: str
    n_results: int = 25

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]

@app.get("/is_collection_exists/{collection_name}")
async def is_collection_exists(collection_name: str):
    """
    Check if a collection exists in the vector store.

    Args:
        collection_name: Name of the collection to check

    Returns:
        JSON response indicating if the collection exists
    """
    collection = chroma_vector_store.get_collection(collection_name)
    return {"exists": collection is not None}

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for documents in a collection.

    Args:
        request: Search request containing query, collection name, and number of results

    Returns:
        Search results from the vector store
    """
    try:
        results = chroma_vector_store.search(
            query=request.query,
            n_results=request.n_results,
            collection_name=request.collection_name
        )
        return {"results": results}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Collection '{request.collection_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def list_collections():
    """"
    List all collections in the vector store.

    Returns:
        List of collection names
    """
    try:
        collections = chroma_vector_store.list_collections()
        return {"collections": collections}
    except Exception as e:
        logger.error(f"Error in list_collections endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


def start_api_service():
    """
    Start the FastAPI service for the vector store
    """
    logger.info("Starting the application on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
if __name__ == "__main__":
    # Initialize the vector store
    start_service()
    # Start the API server
    start_api_service()
