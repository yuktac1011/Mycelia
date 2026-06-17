from fastapi import APIRouter, HTTPException
from app.features.graphing.neo4j_repo import graph_db
from app.features.graphing.analytics import graph_analyzer

router = APIRouter()

@router.get("/network/{username}")
async def get_network_visual(username: str):
    """Returns nodes and edges for the frontend visualization."""
    data = graph_db.get_visjs_network(username)
    
    if not data["nodes"]:
        raise HTTPException(status_code=404, detail="No network found for this user. Try extracting first.")
        
    return data

@router.get("/analyze/{username}")
async def analyze_network(username: str):
    """
    Runs advanced community detection to find Sybil rings.
    """
    analysis_result = graph_analyzer.detect_sybil_rings(username)
    
    if "error" in analysis_result:
        raise HTTPException(status_code=400, detail=analysis_result["error"])
        
    return analysis_result