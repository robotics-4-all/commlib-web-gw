import time
import asyncio
import json
from datetime import datetime
from typing import Optional, Any, Dict, List
from collections import deque

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .commlib_provider import CommlibProvider


INTERVAL = 0.01


class SubscribeInModel(BaseModel):
    topic: str


class PublishInModel(BaseModel):
    topic: str
    msg: Dict[str, Any]


class PublishOutModel(BaseModel):
    status: int
    error: str


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


router = APIRouter(
    responses={404: {"description": "Not found"}},
)
manager = ConnectionManager()

# FastAPI endpoints ----------------------------------------------->
# ------------------------------------------------------------------

@router.websocket("/ws/subscribe")
async def websocket_subscribe(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        data = await websocket.receive_text()
        data = json.loads(data)
        await _ws_subscribe_handle(data['topic'], websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws/publish")
async def websocket_publish(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        data = await websocket.receive_text()
        data = json.loads(data)
        await _ws_publish_handle(data['topic'], data['msg'], websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def _ws_publish_handle(topic: str, msg: Dict[str, Any],
                             websocket: WebSocket):
    print(f'Publishing on topic: {data.topic}')
    gpub = CommlibProvider.gpub
    gpub.publish(msg, topic)


async def _ws_subscribe_handle(topic: str, websocket: WebSocket):
    q = deque()

    def _on_msg(msg: Dict[str, Any]):
        print('MSG')
        q.appendleft(msg)

    gnode = CommlibProvider.gnode
    sub = gnode.create_subscriber(topic=topic, on_message=_on_msg)
    sub.run()
    while True:
        if len(q) > 0:
            msg = q.pop()
            print(msg)
        await asyncio.sleep(INTERVAL)
    sub.stop()
