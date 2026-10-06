from typing import Protocol
from app.schemas import ShipmentCreate, ShipmentUpdate, ShipmentRead, ShipmentStatus, ShipmentReplace


class ShipmentNotFound(Exception):
    def __init__(self, shipment_id: int):
        self.shipment_id = shipment_id
        super().__init__(f"Shipment #{shipment_id} not found.")


# Methods that receive a shipment_id raise ShipmentNotFound when it doesn't exist
class ShipmentService(Protocol):
    async def get(self, shipment_id: int) -> ShipmentRead:
        ...

    async def get_all(self, destination: str|None = None, status: ShipmentStatus|None = None) -> list[ShipmentRead]:
        ...

    async def create(self, shipment: ShipmentCreate) -> ShipmentRead:
        ...

    async def replace(self, shipment_id: int, shipment: ShipmentReplace) -> ShipmentRead:
        ...

    async def update(self, shipment_id: int, changes: ShipmentUpdate) -> ShipmentRead:
        ...

    async def delete(self, shipment_id: int) -> None:
        ...
