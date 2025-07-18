from fastapi import APIRouter

router = APIRouter(prefix="/reset", tags=["util"])

@router.get("/")
async def reset_get() -> dict:
    return {"message": "Entry for reset check endpoint"}

@router.post("/{data}")
async def reset_post(data: str):
    return {"message": data}