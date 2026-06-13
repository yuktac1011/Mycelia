from fastapi import FastAPI
from app.core.config import settings

def get_application() -> FastAPI:
    # Initialize the app with our configurations
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Basic health-check route
    @app.get("/health", tags=["System"])
    async def health_check():
        return {
            "status": "online", 
            "environment": settings.ENVIRONMENT,
            "project": settings.PROJECT_NAME
        }

    return app

app = get_application()