from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mycelia : Ethical OSINT Graph System"
    API_V1_STR: str = "/api/v1"
    
    # We will add Database and Redis URLs here later
    ENVIRONMENT: str = Field(default="development")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instantiate the settings so they can be imported across the app
settings = Settings()