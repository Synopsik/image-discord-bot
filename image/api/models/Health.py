from pydantic import BaseModel

class Health(BaseModel):
    verbosity: int = 1