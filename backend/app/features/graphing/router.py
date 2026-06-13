from fastapi import APIRouter, HTTPException
from app.features.graphing.neo4j_repo import graph_db

router = APIRouter()

@router.get("/network/{username}")
async def get_network_visual(username: str):
    """Returns nodes and edges for the frontend visualization."""
    data = graph_db.get_visjs_network(username)
    
    if not data["nodes"]:
        raise HTTPException(status_code=404, detail="No network found for this user. Try extracting first.")
        
    return data