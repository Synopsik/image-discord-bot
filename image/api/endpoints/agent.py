from fastapi import APIRouter
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
# from util.ai_utils import 

router = APIRouter(prefix="/agent", tags=["ai"])

@router.get("/")
async def agent_get():
    """
    Handles the GET request at the query root endpoint.
    """
    return {"response": "These are not the droids you are looking for"}

@router.get("/models")
async def models_get():
    response = requests.get(f"{os.getenv("OLLAMA_BASE_URL")}/api/tags", timeout=10)
    response.raise_for_status()
    return response.json()


