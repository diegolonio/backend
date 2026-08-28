from enum import StrEnum
from typing import Annotated
from pydantic import BaseModel, Field


class ShipmentStatus(StrEnum):
    PLACED = "placed"
    PENDING = "pending"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


Content = Annotated[str, Field(max_length=30)]
Weight = Annotated[float, Field(gt=0, le=25)]
Destination = Annotated[int, Field(description="Destination ZIP code.")]


class ShipmentBase(BaseModel):
    content: Content
    weight: Weight
    destination: Destination


class ShipmentCreate(ShipmentBase):
    """Create a new Shipment. 'status' initial value is 'placed' always;
    if a different value is sent in the request it's ignored."""


class ShipmentReplace(ShipmentBase):
    status: ShipmentStatus


class ShipmentUpdate(BaseModel):
    content: Content | None = None
    weight: Weight | None = None
    status: ShipmentStatus | None = None
    destination: Destination | None = None


class ShipmentRead(ShipmentBase):
    id: int
    status: ShipmentStatus
