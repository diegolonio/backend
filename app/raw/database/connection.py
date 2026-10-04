from collections.abc import AsyncIterator
from typing import Annotated, Any, AsyncGenerator
from fastapi import Depends
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow
from psycopg_pool import AsyncConnectionPool

from app.database.config import settings

# Opened and closed by the app lifespan (an async pool can't be opened at import time)
pool = AsyncConnectionPool(
    conninfo=settings.database_url,
    connection_class=AsyncConnection[DictRow],
    kwargs={"row_factory": dict_row},
    open=False,
)

async def get_connection() -> AsyncIterator[AsyncConnection[DictRow]]:
    # Commits on exit, rolls back on exception, then returns the connection to the pool
    async with pool.connection() as conn:
        yield conn

ConnDep = Annotated[AsyncConnection[DictRow], Depends(get_connection, scope="function")]
