# backend/app/features/jobs/worker.py
import asyncio
from app.core.celery_app import celery_app
from app.features.extraction.platforms.github import GitHubExtractor
from app.core.ethics import ethics_gatekeeper
from app.features.graphing.neo4j_repo import graph_db  # <-- NEW IMPORT

plugins = {
    "github": GitHubExtractor()
}

@celery_app.task(bind=True, name="extract_network_task")
def extract_network_task(self, platform: str, username: str):
    platform = platform.lower()
    
    if platform not in plugins:
        return {"error": f"Platform '{platform}' not supported"}

    extractor = plugins[platform]
    raw_data_list = asyncio.run(extractor.get_connections(username))
    
    clean_nodes = []
    
    for raw_data in raw_data_list:
        clean_node = ethics_gatekeeper.sanitize_node(raw_data)
        if clean_node:
            clean_nodes.append(clean_node.model_dump())
            
    # --- NEW: SAVE TO DATABASE ---
    if clean_nodes:
        graph_db.save_network(
            source_username=username, 
            platform=platform, 
            clean_nodes=clean_nodes
        )
    # -----------------------------

    return {
        "target": username,
        "platform": platform,
        "nodes_saved": len(clean_nodes)
    }