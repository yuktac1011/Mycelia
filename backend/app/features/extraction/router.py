# backend/app/features/extraction/router.py
from fastapi import APIRouter, HTTPException
from app.features.extraction.platforms.github import GitHubExtractor
from app.core.ethics import ethics_gatekeeper

router = APIRouter()

# Instantiate our plugins
plugins = {
    "github": GitHubExtractor()
}

@router.get("/extract/{platform}/{username}")
async def extract_network(platform: str, username: str):
    """
    Extracts a network from a platform, passing it through the Ethics Engine.
    """
    platform = platform.lower()
    
    if platform not in plugins:
        raise HTTPException(status_code=400, detail=f"Platform '{platform}' not supported.")
        
    extractor = plugins[platform]
    
    # 1. Fetch raw data from the internet
    raw_data_list = await extractor.get_connections(username)
    
    clean_nodes = []
    
    # 2. Pass everything through the Ethics Engine
    for raw_data in raw_data_list:
        clean_node = ethics_gatekeeper.sanitize_node(raw_data)
        if clean_node: # If it wasn't opted out or invalid
            clean_nodes.append(clean_node)
            
    return {
        "target": username,
        "platform": platform,
        "nodes_found": len(clean_nodes),
        "data": clean_nodes
    }