import json
from datetime import datetime
from typing import Annotated

from fastapi import Body, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.database.connection import Client, get_session

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post(
    "", status_code=status.HTTP_200_OK, description="Эндпоинт для загрузки данных в БД"
)
async def insert_problem(
    session: Annotated[Client, Depends(get_session)],
    request: Request,
    payload: Annotated[dict, Body(examples=[{"hello": "world", "z": "6.456"}])],
)->JSONResponse:
    header = dict(request.headers)
    body = payload
    session.insert(
        "default.requests",
        data=[[json.dumps(header), json.dumps(body)]],
        column_names=["headers", "body"],
    )
    result = session.query(
        "SELECT hex(SHA256(concat(toJSONString(%(headers)s), toJSONString(%(body)s))))",
        parameters={"headers": json.dumps(header), "body": json.dumps(body)},
    ).first_row
    return JSONResponse({"hash": result[0]})
