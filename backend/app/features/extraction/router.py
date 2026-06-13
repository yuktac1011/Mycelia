# backend/app/features/extraction/router.py
from fastapi import APIRouter, HTTPException
from app.features.jobs.worker import extract_network_task

router = APIRouter()

@router.post("/extract/{platform}/{username}")
async def trigger_extraction(platform: str, username: str):
    """
    Submits an extraction job to the Celery queue.
    Returns a job_id immediately.
    """
    # .delay() pushes the task to Redis
    task = extract_network_task.delay(platform, username)
    
    return {
        "message": "Extraction job submitted successfully",
        "job_id": task.id,
        "status_url": f"/api/v1/jobs/status/{task.id}"
    }