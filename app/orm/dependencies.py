from typing import Annotated
from fastapi import Depends
from app.orm.database.session import SessionDep
from app.services.shipment import ShipmentService
from app.orm.services.shipment import OrmShipmentService


async def get_service(session: SessionDep) -> OrmShipmentService:
    return OrmShipmentService(session)

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_service)]
