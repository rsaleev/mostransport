import os
from typing import Generator

from clickhouse_connect import get_client
from clickhouse_connect.driver.client import Client

"""
Используеся нативный клиент от Yandex для совместимости с последними версиями clickhouse-server
"""


def get_session() -> Generator[Client, None, None]:
    client = get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        port=int(os.environ.get("CLICKHOUSE_PORT", 8123)),
        username=os.environ.get("CLICKHOUSE_USER", "default"),
        password=os.environ.get("CLICKHOUSE_PASSWORD", None),
        database=os.environ.get("CLICKHOUSE_DATABASE", "default"),
    )
    yield client
    client.close()
