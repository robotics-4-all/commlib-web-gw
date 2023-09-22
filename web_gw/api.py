import os
from fastapi import Depends, FastAPI

from .http_api import router as http_router
from .ws_api import router as ws_router
from .commlib_provider import CommlibProvider


BROKER = os.getenv('BROKER_TYPE', 'mqtt')

CommlibProvider.init_commlib_node(BROKER)

app = FastAPI()
app.include_router(http_router)
app.include_router(ws_router)

@app.get("/")
async def root():
    return {"message": "Commlib Web Integration over HTTP and Websockets"}
