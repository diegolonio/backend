from typing import Annotated
from fastapi import Depends
from app.raw.database.connection import ConnDep
from app.services.shipment import ShipmentService
from app.raw.services.shipment import RawShipmentService


async def get_service(conn: ConnDep) -> RawShipmentService:
    return RawShipmentService(conn)

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_service)]
