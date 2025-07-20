from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["stats"])


@router.get("/{index}")
async def health_get(index) -> dict:
    match int(index):
        case 1:
            return {"health": "Healthy"}
        case _:
            return {"health": "Unhealthy"}