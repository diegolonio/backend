from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session
from app.database.config import settings

engine = create_engine(
    url=settings.database_url.replace("postgresql://", "postgresql+psycopg://"),
    echo=False
)

def get_session():
    with Session(bind=engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
