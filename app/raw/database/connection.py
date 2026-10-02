from collections.abc import Iterator
from typing import Annotated
import psycopg
from fastapi import Depends
from psycopg.rows import dict_row, DictRow
from psycopg import Connection

from app.database.config import settings

def get_connection() -> Iterator[Connection[DictRow]]:
    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        yield conn

ConnDep = Annotated[Connection[DictRow], Depends(get_connection, scope="function")]
