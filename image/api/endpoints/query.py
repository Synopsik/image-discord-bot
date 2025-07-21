from http.client import responses

from fastapi import APIRouter
from models.Query import Query, AttachmentEnum
from util.ai_utils import query_llm

router = APIRouter(prefix="/query", tags=["ai"])

@router.get("/")
async def query_get():
    """
    Handles the GET request at the query root endpoint.
    """
    return {"response": "These are not the droids you are looking for"}

@router.post("/")
async def query_post(query: Query):
    """
    Handles POST requests to execute a query against a language model (LLM).
    """
    return await query_llm(
        query=query.content,
        llm=query.llm,
        model=query.model,
        show_thoughts=query.show_thoughts
    )