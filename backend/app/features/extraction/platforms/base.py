# backend/app/features/extraction/platforms/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseExtractor(ABC):
    """
    The blueprint for all Mycelia platform plugins.
    Every platform (Reddit, Twitter, GitHub) MUST implement these methods.
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Returns the name of the platform (e.g., 'github')"""
        pass

    @abstractmethod
    async def get_connections(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetches the network for a given user.
        Must return a list of dictionaries representing raw node/edge data.
        """
        pass