from enum import StrEnum
from pydantic import BaseModel, Field

class ShipmentStatus(StrEnum):
    PLACED = "placed"
    PENDING = "pending"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"

class Shipment(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(gt=0, le=25)
    status: ShipmentStatus = Field(default=ShipmentStatus.PLACED)
    destination: int

class ShipmentGet(Shipment):
    id: int

class ShipmentPatch(BaseModel):
    content: str|None = Field(max_length=30, default=None)
    weight: float|None = Field(gt=0, le=25, default=None)
    status: ShipmentStatus|None = Field(default=None)
    destination: int|None = Field(default=None)
