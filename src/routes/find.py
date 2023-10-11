import json
from datetime import datetime
from hashlib import sha256
from typing import Annotated, Any, Dict, List, Sequence

from fastapi import Body, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.database.connection import Client, get_session

router = APIRouter(prefix="")


def format_ch_json_string(data: Sequence[str]) -> Dict[str, Any]:
    """
    format_ch_json_string форматирование Sequence в dict для выдачи в виде вложенного JSON без использования функционала клиента для обеспечения контролируемого transform алгоритма

    :param data: массив строк из ResultSet
    :type data: List[str]
    :return: dict с отформатированным элементами
    :rtype: Dict[str, Any]
    """
    embedded = {}
    for idx, item in enumerate(data):
        if idx == 0:
            item = json.loads(item)
            embedded.update({"headers": item})
        if idx == 1:
            item = json.loads(item)
            embedded.update({"body": item})
    return embedded


def fetch_result_set_by_key_value(
    session: Client, key: Any, value: Any
) -> List[Dict[str, Dict[str, Any]]]:
    """
    fetch_result_set ET процесс: получение данных из Clickhouse DB с трансформированием структуры 

    :param session: инстанс подключения/курсора к Clickhouse
    :type session: Client
    :param key: ключ JSON для поиска в значениях в таблицах
    :type key: Any
    :param key: значение JSON для поиска в значениях в таблицах
    :type key: Any
    :return: массив с отформатированным элементами с возможностью дампа в JSON массив
    :rtype: List[Dict[str, Dict[str, Any]]]
    """
    result = session.query(
        query="""SELECT
    toJSONString(headers),
    toJSONString(body),
    FROM requests
    WHERE (visitParamHas(toJSONString(body), %(key)s) = 1) AND (visitParamExtractString(toJSONString(body), %(key)s) = %(value)s)
    """,
        parameters={"key": key, "value": value},
    ).result_set
    result = [format_ch_json_string(item) for item in result]
    return result


# средняя скорость ответа 38 мс
@router.post("/find", description="Поиск записей по key:value")
async def find_record_by_payload(
    session: Annotated[Client, Depends(get_session)],
    payload: Annotated[
        dict,
        Body(
            description="Тело запроса",
            examples=[
                {"hello": "world"},
                {"z": "6.456"},
                {"q": 1},
                {"t": 15},
            ],
        ),
    ],
):
    results = [fetch_result_set_by_key_value(session, k, v) for k, v in payload.items()]
    return results


# средняя скорость ответа 45 мс
@router.get("/find2", description="Поиск записей по hash")
async def find_record_by_hash(
    session: Annotated[Client, Depends(get_session)],
    h: str = Query(
        description="Поиск по hash",
        examples=["061F054D9593257A2BE37140C3FB346C9FBF380E50EAF50C35BF18158E899A54"],
    ),
):
    result = session.query(
        "SELECT * FROM requests WHERE hex(SHA256(concat(toJSONString(headers), toJSONString(body)))) = %(hash)s",
        parameters={"hash": h},
    )
    results = [format_ch_json_string(item) for item in result.result_set]
    return {"result": results}
