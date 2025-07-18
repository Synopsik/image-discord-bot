from fastapi import FastAPI
from mangum import Mangum

from api_router import api_router

app = FastAPI(
    title="AWS Discord Bot",
    version="1.0.0"
    # So much more to add
)

app.include_router(api_router)

handler = Mangum(app)

@app.get("/")
async def root():
    return {"response": "Go away"}


if __name__ == "__main__":
    import uvicorn 
    # Will this work on AWS EC2? Possibly not since the warning appeared,
    # INFO: ASGI 'lifespan' protocol appears unsupported.
    # will probably need to just comment out this whole area if errors occur
    uvicorn.run("start:handler", host="0.0.0.0", port=8000, reload=True)