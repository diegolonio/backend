from scalar_fastapi import get_scalar_api_reference
from fastapi import FastAPI
from contextlib import asynccontextmanager
from rich import print, panel
from app.orm.main import router as orm_router
from app.raw.main import router as raw_router
from app.orm.database.session import engine
from app.raw.database.connection import pool


@asynccontextmanager
async def lifespan_handler(_app):
    print(panel.Panel("Server started.", border_style="green"))
    await pool.open()
    yield
    await pool.close()
    await engine.dispose()
    print(panel.Panel("Server stopped.", border_style="green"))


app = FastAPI(lifespan=lifespan_handler)


app.include_router(orm_router)
app.include_router(raw_router)


# Scalar documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
