from fastapi import APIRouter
from endpoints import health, query, reset, agent

api_router = APIRouter()
api_router.include_router(reset.router)
api_router.include_router(health.router)
api_router.include_router(query.router)
api_router.include_router(agent.router)