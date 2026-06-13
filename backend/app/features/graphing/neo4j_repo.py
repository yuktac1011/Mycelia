# backend/app/features/graphing/neo4j_repo.py
from neo4j import GraphDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jRepository:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def save_network(self, source_username: str, platform: str, clean_nodes: list):
        """
        Saves the target user and their connections into the Graph Database.
        """
        if not clean_nodes:
            return

        # Cypher query to bulk-insert nodes and relationships
        # UNWIND acts like a for-loop in Cypher, making bulk inserts blazingly fast.
        query = """
        // 1. Ensure the Source Node (Target) exists
        MERGE (source:User {username: $source_username, platform: $platform})
        
        // 2. Loop through all scraped nodes
        WITH source
        UNWIND $nodes AS node_data
        
        // 3. Create/Match the Target Node
        MERGE (target:User {username: node_data.username, platform: node_data.platform})
        ON CREATE SET target.display_name = node_data.display_name,
                      target.profile_url = node_data.profile_url
                      
        // 4. Create the Edge (Relationship) between them
        MERGE (source)-[:FOLLOWS]->(target)
        """

        try:
            with self.driver.session() as session:
                session.run(
                    query, 
                    source_username=source_username, 
                    platform=platform, 
                    nodes=clean_nodes
                )
            logger.info(f"Successfully saved {len(clean_nodes)} nodes to Neo4j for {source_username}")
        except Exception as e:
            logger.error(f"Failed to save to Neo4j: {e}")

# Instantiate singleton
graph_db = Neo4jRepository()