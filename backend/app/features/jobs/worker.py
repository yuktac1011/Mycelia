# backend/app/features/jobs/worker.py
import asyncio
from app.core.celery_app import celery_app
from app.features.extraction.platforms.github import GitHubExtractor
from app.core.ethics import ethics_gatekeeper

# Instantiate plugins for the worker
plugins = {
    "github": GitHubExtractor()
}

@celery_app.task(bind=True, name="extract_network_task")
def extract_network_task(self, platform: str, username: str):
    """
    Background job that runs outside the main web thread.
    """
    platform = platform.lower()
    
    if platform not in plugins:
        return {"error": f"Platform '{platform}' not supported"}

    extractor = plugins[platform]
    
    # Run the async extraction inside the sync Celery task
    # In production, we'd add depth-crawling logic here
    raw_data_list = asyncio.run(extractor.get_connections(username))
    
    clean_nodes = []
    
    # Ethics Engine Gate
    for raw_data in raw_data_list:
        clean_node = ethics_gatekeeper.sanitize_node(raw_data)
        if clean_node:
            # Convert Pydantic model to dict so Celery can serialize it to Redis
            clean_nodes.append(clean_node.model_dump())
            
    return {
        "target": username,
        "platform": platform,
        "nodes_found": len(clean_nodes),
        "data": clean_nodes
    }