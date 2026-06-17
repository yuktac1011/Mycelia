from fastapi import FastAPI
from app.core.config import settings

from app.features.extraction.router import router as extraction_router
from app.features.jobs.router import router as jobs_router

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.features.graphing.router import router as graphing_router

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
        
    app.include_router(extraction_router, prefix=settings.API_V1_STR, tags=["Extraction"])
    app.include_router(jobs_router, prefix=f"{settings.API_V1_STR}/jobs", tags=["Jobs"])
    app.include_router(graphing_router, prefix=f"{settings.API_V1_STR}/graph", tags=["Graphing"])

    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Serve the index.html on the root URL
    @app.get("/", include_in_schema=False)
    async def serve_ui():
        return FileResponse("app/static/index.html")

    return app


app = get_application()