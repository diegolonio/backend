from datetime import datetime
from enum import StrEnum
from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints


class ShipmentStatus(StrEnum):
    PLACED = "placed"
    PENDING = "pending"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


# Mirrors the DB check: length(trim(content)) > 0
Content = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
# DECIMAL(4, 2): values below 0.01 round to 0.00 and fail the DB check
Weight = Annotated[float, Field(ge=0.01, le=25)]
Destination = Annotated[int, Field(ge=1, le=99999, description="Destination ZIP code.")]


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
    created_at: datetime
