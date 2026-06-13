# backend/app/features/extraction/platforms/github.py
import httpx
import logging
from typing import List, Dict, Any
from .base import BaseExtractor

logger = logging.getLogger(__name__)

class GitHubExtractor(BaseExtractor):
    @property
    def platform_name(self) -> str:
        return "github"

    async def get_connections(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetches the users that the target follows on GitHub.
        """
        url = f"https://api.github.com/users/{username}/following"
        
        # We use a custom User-Agent to be polite and identify our bot
        headers = {"User-Agent": "Mycelia-Ethical-OSINT-Bot/1.0"}
        
        raw_connections = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                # If the user doesn't exist or we hit rate limits
                if response.status_code != 200:
                    logger.error(f"GitHub API error for {username}: {response.status_code}")
                    return raw_connections

                data = response.json()
                
                # Format the data
                for item in data:
                    raw_node = {
                        "username": item.get("login"),
                        "platform": self.platform_name,
                        "display_name": item.get("login"), # GitHub public API doesn't return name in this endpoint
                        "profile_url": item.get("html_url"),
                        # We capture the relationship for our edges
                        "_relationship": "follows",
                        "_source": username
                    }
                    raw_connections.append(raw_node)
                    
        except Exception as e:
            logger.error(f"Failed to extract from GitHub for {username}: {e}")
            
        return raw_connections