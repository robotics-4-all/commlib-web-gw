import time
import asyncio
import json
from datetime import datetime
from typing import Optional, Any, Dict, List
from collections import deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
# from fastapi.encoders import jsonable_encoder
# from fastapi.testclient import TestClient
# from fastapi.websockets import WebSocket
from pydantic import BaseModel

from commlib.node import Node, TransportType


class PublishInModel(BaseModel):
    topic: str
    msg: Dict[str, Any]


class SubscribeInModel(BaseModel):
    topic: str


class PublishOutModel(BaseModel):
    status: int
    error: str


def init_commlib_node(broker: str, debug: bool = True):
    if broker == 'redis':
        from commlib.transports.redis import ConnectionParameters
        transport = TransportType.REDIS
    elif broker == 'amqp':
        from commlib.transports.amqp import ConnectionParameters
        transport = TransportType.AMQP
    elif broker == 'mqtt':
        from commlib.transports.mqtt import ConnectionParameters
        transport = TransportType.MQTT
    else:
        raise ValueError('Not a valid broker-type was given!')
    conn_params = ConnectionParameters()

    node = Node(node_name=f'http_to_{broker}_gw',
                transport_type=transport,
                connection_params=conn_params,
                debug=debug)
    return node


cnode = init_commlib_node('redis')
mpub = cnode.create_mpublisher()
cnode.run()

# FastAPI endpoints ----------------------------------------------->
# ------------------------------------------------------------------
app = FastAPI()


@app.post("/publish", status_code=201, response_model=PublishOutModel)
async def publish_post(data: PublishInModel):
    resp = PublishOutModel(status=200, error='')
    try:
        # json_data = jsonable_encoder(data)
        print(data.topic)
        print(data.msg)
        mpub.publish(data.msg, data.topic)
    except Exception as e:
        resp.status = 500
        resp.error = f'{e}'
    return resp


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


manager = ConnectionManager()


@app.websocket("/ws/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        data = await websocket.receive_text()
        data = json.loads(data)
        await _ws_subscribe_handle(data['topic'], websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def _ws_subscribe_handle(topic: str, websocket: WebSocket):
    q = deque()
    def _on_msg(msg: Dict[str, Any]):
        print('MSG')
        q.appendleft(msg)

    sub = cnode.create_subscriber(topic=topic, on_message=_on_msg)
    sub.run()
    while True:
        if len(q) > 0:
            msg = q.pop()
            print(msg)
        await asyncio.sleep(0.1)
    # sub.stop()
    # del sub
