from app.schemas import ShipmentCreate, ShipmentUpdate, ShipmentRead, ShipmentStatus, ShipmentReplace
from app.services.shipment import ShipmentNotFound
from app.orm.database.models import Shipment
from sqlmodel import select, col, delete
from sqlmodel.ext.asyncio.session import AsyncSession


class OrmShipmentService:
    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, shipment_id: int) -> ShipmentRead:
        shipment = await self._session.get(Shipment, shipment_id)

        if shipment is None:
            raise ShipmentNotFound(shipment_id)

        return ShipmentRead.model_validate(shipment, from_attributes=True)

    async def get_all(self, destination: int|None = None, status: ShipmentStatus|None = None) -> list[ShipmentRead]:
        statement = select(Shipment)

        if destination is not None:
            statement = statement.where(Shipment.destination == destination)

        if status is not None:
            statement = statement.where(Shipment.status == status)

        statement = statement.order_by(col(Shipment.id))

        shipments = (await self._session.exec(statement)).all()
        return [ShipmentRead.model_validate(shipment, from_attributes=True) for shipment in shipments]

    async def create(self, shipment: ShipmentCreate) -> ShipmentRead:
        new_shipment = Shipment(**shipment.model_dump())
        self._session.add(new_shipment)
        await self._session.commit()
        await self._session.refresh(new_shipment)
        return ShipmentRead.model_validate(new_shipment, from_attributes=True)

    async def replace(self, shipment_id: int, shipment: ShipmentReplace) -> ShipmentRead:
        stored_shipment = await self._session.get(Shipment, shipment_id)

        if stored_shipment is None:
            raise ShipmentNotFound(shipment_id)

        stored_shipment.sqlmodel_update(shipment.model_dump())
        await self._session.commit()
        await self._session.refresh(stored_shipment)
        return ShipmentRead.model_validate(stored_shipment, from_attributes=True)

    async def update(self, shipment_id: int, changes: ShipmentUpdate) -> ShipmentRead:
        stored_shipment = await self._session.get(Shipment, shipment_id)

        if stored_shipment is None:
            raise ShipmentNotFound(shipment_id)

        stored_shipment.sqlmodel_update(changes.model_dump(exclude_unset=True))
        await self._session.commit()
        await self._session.refresh(stored_shipment)
        return ShipmentRead.model_validate(stored_shipment, from_attributes=True)

    async def delete(self, shipment_id: int) -> None:
        result = await self._session.exec(delete(Shipment).where(col(Shipment.id) == shipment_id))
        await self._session.commit()

        if result.rowcount == 0:
            raise ShipmentNotFound(shipment_id)
