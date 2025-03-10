from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
import uvicorn
from app.chroma_vector_store import chroma_vector_store
from app.startup import start_service
from pydantic import BaseModel

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
    """
    List all collections in the vector store.

    Returns:
        List of collection names
    """
    collections = chroma_vector_store.list_collections()
    return {"collections": collections}

def start_api():
    """Start the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Initialize the vector store
    start_service()
    # Start the API server
    start_api()