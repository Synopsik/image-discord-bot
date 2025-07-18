from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["stats"])

@router.get("/")
async def query():
    return {"message": "Entry for health check endpoint"}

