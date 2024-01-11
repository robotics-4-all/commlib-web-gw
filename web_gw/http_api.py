import asyncio
import json
from typing import Optional, Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from .commlib_provider import CommlibProvider

INTERVAL = 0.01


class PublishInModel(BaseModel):
    topic: str
    msg: Dict[str, Any]


class PublishOutModel(BaseModel):
    status: int
    error: str


class RPCInModel(BaseModel):
    topic: str
    msg: Dict[str, Any]


class RPCOutModel(BaseModel):
    response: Dict[str, Any]


router = APIRouter(
    responses={404: {"description": "Not found"}},
)

# FastAPI endpoints ----------------------------------------------->
# ------------------------------------------------------------------

@router.put("/publish", status_code=201, response_model=PublishOutModel)
async def publish_put(data: PublishInModel):
    print(f'Publishing on topic: {data.topic}')
    resp = PublishOutModel(status=200, error='')
    try:
        # json_data = jsonable_encoder(data)
        gpub = CommlibProvider.gpub
        gpub.publish(data.msg, data.topic)
    except Exception as e:
        resp.status = 500
        resp.error = f'{e}'
    return resp


@router.put("/rpc", status_code=201, response_model=RPCOutModel)
async def rpc_call_http(data: RPCInModel):
    print(f'RPC call: {data.topic}')
    resp = RPCOutModel(response={})
    try:
        # json_data = jsonable_encoder(data)
        gpub.publish(data.msg, data.topic)
    except Exception as e:
        resp.status = 500
        resp.error = f'{e}'
    return resp
