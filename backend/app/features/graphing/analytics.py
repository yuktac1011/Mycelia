# backend/app/features/graphing/analytics.py
import networkx as nx
import community.community_louvain as community_louvain
from app.features.graphing.neo4j_repo import graph_db
import logging

logger = logging.getLogger(__name__)

class GraphAnalyzer:
    def detect_sybil_rings(self, username: str):
        """
        Runs Louvain Modularity to detect suspicious, isolated clusters.
        """
        # 1. Fetch raw graph edges from Neo4j
        # We reuse the Vis.js data structure for simplicity
        raw_data = graph_db.get_visjs_network(username)
        edges = raw_data.get("edges", [])
        
        if not edges:
            return {"error": "Graph too small or not found."}

        # 2. Build the NetworkX Graph (Undirected for Louvain)
        G = nx.Graph()
        for edge in edges:
            G.add_edge(edge["from"], edge["to"])

        # 3. Run Community Detection (Louvain Modularity)
        # This assigns every node to a 'community_id'
        partition = community_louvain.best_partition(G)

        # Group nodes by their community
        communities = {}
        for node, comm_id in partition.items():
            if comm_id not in communities:
                communities[comm_id] = []
            communities[comm_id].append(node)

        # 4. Identify "Suspicious" Rings
        # Heuristic: A bot-ring usually has 3 to 15 accounts that all follow each other
        # but have very few connections outside their circle.
        suspicious_nodes = []
        ring_details = []

        for comm_id, members in communities.items():
            if 3 <= len(members) <= 15:
                # Calculate internal density (how tightly knit they are)
                subgraph = G.subgraph(members)
                density = nx.density(subgraph)
                
                # If density is unusually high (>0.8 means almost everyone follows everyone)
                if density > 0.8:
                    suspicious_nodes.extend(members)
                    ring_details.append({
                        "ring_id": comm_id,
                        "size": len(members),
                        "density": round(density, 2),
                        "members": members
                    })

        logger.info(f"Analysis complete for {username}. Found {len(ring_details)} Sybil rings.")
        
        return {
            "total_nodes_analyzed": len(G.nodes),
            "total_communities_found": len(communities),
            "suspicious_rings": ring_details,
            "flagged_nodes": suspicious_nodes
        }

graph_analyzer = GraphAnalyzer()