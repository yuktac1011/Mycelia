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
            
    def get_visjs_network(self, username: str):
        """Fetches the ego-network and all interconnections for Vis.js"""
        query = """
        // 1. Find the target and everyone within 2 hops
        MATCH (start:User)-[:FOLLOWS*0..2]-(neighbor:User)
        WHERE toLower(start.username) = toLower($username)
        WITH collect(DISTINCT neighbor) AS network_nodes
        
        // 2. Find ALL edges where both users are inside this bubble
        MATCH (n1:User)-[r:FOLLOWS]-(n2:User)
        WHERE n1 IN network_nodes AND n2 IN network_nodes
        
        RETURN n1.username AS source_id, n2.username AS target_id
        """
        
        nodes_dict = {}
        edges = []

        try:
            with self.driver.session() as session:
                result = session.run(query, username=username)
                
                for record in result:
                    src_id = record["source_id"]
                    tgt_id = record["target_id"]
                    
                    # Highlight the searched user in Red, everyone else in Green
                    if src_id not in nodes_dict:
                        color = "#e05263" if src_id.lower() == username.lower() else "#69b3a2"
                        size = 35 if src_id.lower() == username.lower() else 20
                        nodes_dict[src_id] = {"id": src_id, "label": src_id, "color": color, "size": size} 
                    
                    if tgt_id not in nodes_dict:
                        color = "#e05263" if tgt_id.lower() == username.lower() else "#69b3a2"
                        size = 35 if tgt_id.lower() == username.lower() else 20
                        nodes_dict[tgt_id] = {"id": tgt_id, "label": tgt_id, "color": color, "size": size}
                        
                    edges.append({"from": src_id, "to": tgt_id})
                    
        except Exception as e:
            logger.error(f"Failed to fetch network for {username}: {e}")

        return {
            "nodes": list(nodes_dict.values()),
            "edges": edges
        }

# Instantiate singleton
graph_db = Neo4jRepository()