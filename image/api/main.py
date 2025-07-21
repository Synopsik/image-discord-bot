import os

import uvicorn
from fastapi import FastAPI
from mangum import Mangum

from util.api_router import api_router

app = FastAPI(
    title="AWS Discord Bot",
    version="1.0.1",
    # So much more to add
)

app.include_router(api_router)

@app.get("/")
async def root(): # Root GET endpoint
    return {"response": "Go away"}

handler = Mangum(app) # Handler for AWS API

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    # We'll use handler once AWS is setup. 
    # Need to implement way to differentiate environments (local / AWS) 
    # uvicorn.run("main:handler", host="0.0.0.0", port=8000)