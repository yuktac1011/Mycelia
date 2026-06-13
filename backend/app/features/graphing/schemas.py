# backend/app/features/graphing/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class UserNode(BaseModel):
    """
    Represents a single user in the graph.
    Strictly adheres to data minimization: No PII (emails, phone numbers) allowed.
    """
    username: str = Field(..., description="The public handle of the user")
    platform: str = Field(..., description="e.g., twitter, github, reddit")
    display_name: Optional[str] = Field(None, description="Public display name")
    profile_url: Optional[str] = Field(None, description="URL to public profile")
    
    # Notice what is missing: email, phone, exact_location, age, etc.

class ConnectionEdge(BaseModel):
    """
    Represents a connection (follow/friend) between two nodes.
    """
    source_username: str
    target_username: str
    platform: str
    connection_type: str = Field(default="follows", description="e.g., follows, mentions, forks")