from pydantic import BaseModel
from enum import Enum

class AttachmentEnum(str, Enum):
    image = "image"
    pdf = "pdf"
    video = "video"
    audio = "audio"
    document = "document"
    code = "code"
    
class Query(BaseModel):
    content: str = "Waduhek?"
    llm: str = "ollama"
    model: str = "deepseek-r1:8b"
    show_thoughts: bool = False # Provide thoughts in response, formatted cleanly
    