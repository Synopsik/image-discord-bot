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
    query: str = "Waduhek?"
    attachments: list[AttachmentEnum] | None = None # Needs to be refactored for attachments w/ other
    show_thoughts: bool = False # Provide thoughts in response, formatted cleanly
    