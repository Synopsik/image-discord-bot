import os

import uvicorn
from fastapi import FastAPI
from mangum import Mangum
from util.api_router import api_router

app = FastAPI(
    title="AWS Discord Bot",
    version="1.0.0",
    # So much more to add
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"response": "Go away"}

handler = Mangum(app)

if __name__ == "__main__": # Comment out in prod
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    # uvicorn.run("main:handler", host="0.0.0.0", port=8000)