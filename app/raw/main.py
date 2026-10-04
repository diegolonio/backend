from typing import Annotated, Literal
from fastapi import APIRouter, status, HTTPException, Query, Depends, Response
from app.schemas import ShipmentCreate, ShipmentReplace, ShipmentUpdate, ShipmentRead, ShipmentStatus
from app.raw.database.connection import ConnDep
from app.services.shipment import RawShipmentService

router = APIRouter(prefix="/raw", tags=["Raw"])

async def get_raw_service(conn: ConnDep) -> RawShipmentService:
    return RawShipmentService(conn)

DBServiceDep = Annotated[RawShipmentService, Depends(get_raw_service)]

@router.get("/shipments")
async def get_shipments(
        service: DBServiceDep,
        destination: int|None = None,
        shipment_status: Annotated[ShipmentStatus|None, Query(alias="status")] = None,
) -> list[ShipmentRead]:
    return await service.get_all(destination=destination, status=shipment_status)

@router.get("/shipments/{shipment_id}")
async def get_shipment(
        shipment_id: int,
        service: DBServiceDep
) -> ShipmentRead:
    return await service.get(shipment_id=shipment_id)

@router.get("/shipments/{shipment_id}/{field}")
async def get_shipment_field(
        shipment_id: int,
        field: Literal["content", "weight", "status", "destination"],
        service: DBServiceDep
) -> str|float|int:
    return (await service.get(shipment_id=shipment_id)).model_dump(mode="json")[field]

@router.post("/shipments", status_code=status.HTTP_201_CREATED)
async def submit_shipment(
        shipment: ShipmentCreate,
        service: DBServiceDep,
        response: Response) -> ShipmentRead:
    created = await service.create(shipment)
    response.headers["Location"] = f"{router.prefix}/shipments/{created.id}"
    return created

@router.put("/shipments/{shipment_id}")
async def update_shipment(
        shipment_id: int,
        shipment: ShipmentReplace,
        service: DBServiceDep
) -> ShipmentRead:
    return await service.replace(shipment_id=shipment_id, shipment=shipment)

@router.patch("/shipments/{shipment_id}")
async def patch_shipment(
        shipment_id: int,
        shipment_patch: ShipmentUpdate,
        service: DBServiceDep
) -> ShipmentRead:
    if not shipment_patch.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No fields to update."
        )
    return await service.update(shipment_id=shipment_id, changes=shipment_patch)

@router.delete("/shipments/{shipment_id}", status_code=status.HTTP_200_OK)
async def delete_shipment(
        shipment_id: int,
        service: DBServiceDep
) -> dict[str, str]:
    await service.delete(shipment_id=shipment_id)
    return {"detail": f"Shipment #{shipment_id} deleted"}
