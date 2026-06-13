# backend/app/core/ethics.py
from app.features.graphing.schemas import UserNode
import logging

logger = logging.getLogger(__name__)

class EthicsEngine:
    def __init__(self):
        # Simulated database of people who requested "Do Not Track/Map"
        # In production, this will be connected to a Redis cache
        self._opt_out_registry = {
            "private_jane123",
            "do_not_scrape_me_bro",
            "ceo_private_acct"
        }

    def is_opted_out(self, username: str) -> bool:
        """Check if a user has requested to be excluded from mapping."""
        return username.lower() in self._opt_out_registry

    def sanitize_node(self, raw_data: dict) -> UserNode | None:
        """
        Takes raw scraped dictionary data.
        1. Checks opt-out registry.
        2. Drops PII by forcing data through the UserNode Pydantic schema.
        Returns None if the user is opted out.
        """
        username = raw_data.get("username")
        
        if not username:
            logger.warning("Scraped data missing username. Dropping.")
            return None

        # Ethical Gate 1: Respect Opt-Outs
        if self.is_opted_out(username):
            logger.info(f"ETHICS ENGINE: Dropped node for '{username}' (Opt-Out Registry)")
            return None

        # Ethical Gate 2: Data Minimization
        # Pydantic will automatically ignore any keys in raw_data that aren't in UserNode
        try:
            clean_node = UserNode(**raw_data)
            return clean_node
        except Exception as e:
            logger.error(f"Failed to sanitize node {username}: {e}")
            return None

# Instantiate a singleton to be used across the app
ethics_gatekeeper = EthicsEngine()