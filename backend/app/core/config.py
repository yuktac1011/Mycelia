from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mycelia : Ethical OSINT Graph System"
    API_V1_STR: str = "/api/v1"
    # Add these inside the Settings class in config.py
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "mycelia_secret_123"
    
    # We will add Database and Redis URLs here later
    ENVIRONMENT: str = Field(default="development")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instantiate the settings so they can be imported across the app
settings = Settings()