from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.vector_store.chroma_vector_store import chroma_vector_store
from app.startup import start_service
from pydantic import BaseModel
from app.logging.logging_config import get_logger
import traceback
import uvicorn
logger = get_logger()

app = FastAPI(title="Vector Store API", description="API for interacting with ChromaDB vector store")

class SearchRequest(BaseModel):
    query: str
    n_results: int = 25

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]

class AddRequest(BaseModel):
    item_dict: Dict[str, str]

@app.get("/collections/{collection_name}/exists")
async def check_collection(collection_name: str):
    """
    Check if a collection exists in the vector store.

    Args:
        collection_name: Name of the collection to check

    Returns:
        JSON response indicating if the collection exists
    """
    if not collection_name:
        raise HTTPException(status_code=400, detail="Collection name cannot be empty")
        
    collection = chroma_vector_store.get_collection(collection_name)
    return {"exists": collection is not None}

@app.post("/collections")
async def create_collection(collection_name: str = Query(..., description="Name of the collection to create")):
    """
    Create a new collection in the vector store.

    Args:
        collection_name: Name of the collection to check

    Returns:
        JSON response indicating if the collection exists
    """
    collection = chroma_vector_store.get_collection(collection_name=collection_name)
    if collection is not None:
        return {"message": f"{collection} already exists"}
    collection = chroma_vector_store.create_collection(collection_name)
    return {"message": f"{collection} created successfully!"}

@app.post("/collections/{collection_name}/items")
async def add_items_to_collection(collection_name: str, request: AddRequest):
    """
    Add items to a collection in the vector store.

    Args:
        collection_name: Name of the collection to add items to
        request: Request containing dictionary of items to add

    Returns:
        JSON response indicating the status of the operation
    """
    data = request.item_dict
    if not collection_name:
        raise HTTPException(status_code=400, detail="No collection name provided")
    if not data:
        raise HTTPException(status_code=400, detail="No data provided to add")
    
    collection = chroma_vector_store.get_collection(collection_name=collection_name)
    if collection is None:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    
    try:
        chroma_vector_store.add_dictionary(collection_name, data)
        return {"message": "Data successfully added to collection"}
    except Exception as e:
        logger.error(f"Unable to add data to collection: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Unable to add data to the collection: {str(e)}")

@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """
    Delete a collection from the vector store.

    Args:
        collection_name: Name of the collection to delete

    Returns:
        JSON response indicating the deletion status
    """
    collection = chroma_vector_store.get_collection(collection_name=collection_name)
    if collection is None:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
    
    chroma_vector_store.delete_collection(collection_name)
    return {"message": f"Collection '{collection_name}' deleted successfully"}

@app.post("/collections/{collection_name}/search", 
    response_model=SearchResponse,
    responses={
        200: {"description": "Successful search results"},
        404: {"description": "Collection not found"},
        500: {"description": "Internal server error"}
    }
)
async def search(collection_name: str, request: SearchRequest):
    """
    Search for documents in a collection.

    Args:
        collection_name: Name of the collection to search in
        request: Search request containing query and number of results

    Returns:
        Search results from the vector store
    """
    try:
        results = chroma_vector_store.search(
            query=request.query,
            n_results=request.n_results,
            collection_name=collection_name
        )
        return {"results": results}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found")
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
    #start_service()
    # Start the API server
    start_api_service()
