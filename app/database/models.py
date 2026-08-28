from typing import Annotated
from sqlmodel import SQLModel, Field
from ..schemas import ShipmentStatus

class ShipmentTable(SQLModel):
    __tablename__ = "shipments"

    id: Annotated[int, Field(primary_key=True)]
    content: Annotated[str, Field(max_length=30)]
    weight: Annotated[float, Field(gt=0, le=25)]
    destination: int
    status: ShipmentStatus = ShipmentStatus.PLACED
