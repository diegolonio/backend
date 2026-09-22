from typing import Annotated
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import SQLModel, Field, Column
from app.schemas import ShipmentStatus

# Reuse the existing Postgres enum type instead of letting SQLAlchemy create its own
shipment_status_type = ENUM(
    ShipmentStatus,
    name="shipment_status",
    values_callable=lambda enum: [member.value for member in enum],
    create_type=False,
)

class Shipment(SQLModel, table=True):
    __tablename__ = "shipments"

    id: Annotated[int|None, Field(default=None, primary_key=True)]
    content: Annotated[str, Field(max_length=30)]
    weight: Annotated[float, Field(gt=0, le=25)]
    destination: int
    status: ShipmentStatus = Field(
        default=ShipmentStatus.PLACED,
        sa_column=Column(shipment_status_type, nullable=False)
    )
