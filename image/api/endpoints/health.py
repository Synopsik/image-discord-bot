from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["stats"])


@router.get("/")
async def health_get() -> dict:
    return {"message": "Entry for health check endpoint"}

@router.post("/")
async def health_post(status: int) -> int:
    if status == 1:
        return 1
    else:
        return 0
