from typing import Annotated, Literal
from fastapi import APIRouter, HTTPException, status, Query, Response
from app.schemas import Destination, ShipmentRead, ShipmentStatus, ShipmentCreate, ShipmentReplace, ShipmentUpdate
from app.raw.api.dependencies import ShipmentServiceDep

router = APIRouter(prefix="/raw", tags=["Raw"])

@router.get("/shipments")
async def get_shipments(
        service: ShipmentServiceDep,
        destination: Destination|None = None,
        shipment_status: Annotated[ShipmentStatus|None, Query(alias="status")] = None,
    ) -> list[ShipmentRead]:
    return await service.get_all(destination=destination, status=shipment_status)

@router.get("/shipments/{shipment_id}")
async def get_shipment(
        shipment_id: int,
        service: ShipmentServiceDep
    ) -> ShipmentRead:
    return await service.get(shipment_id=shipment_id)

@router.get("/shipments/{shipment_id}/{field}")
async def get_shipment_field(
        shipment_id: int,
        field: Literal["content", "weight", "status", "destination"],
        service: ShipmentServiceDep
    ) -> str|float|int:
    return (await service.get(shipment_id=shipment_id)).model_dump(mode="json")[field]

@router.post("/shipments", status_code=status.HTTP_201_CREATED)
async def submit_shipment(
        shipment: ShipmentCreate,
        service: ShipmentServiceDep,
        response: Response
    ) -> ShipmentRead:
    new_shipment = await service.create(shipment=shipment)
    response.headers["Location"] = f"{router.prefix}/shipments/{new_shipment.id}"
    return new_shipment

@router.put("/shipments/{shipment_id}")
async def update_shipment(
        shipment_id: int,
        shipment: ShipmentReplace,
        service: ShipmentServiceDep
    ) -> ShipmentRead:
    return await service.replace(shipment_id=shipment_id, shipment=shipment)

@router.patch("/shipments/{shipment_id}")
async def patch_shipment(
        shipment_id: int,
        shipment_patch: ShipmentUpdate,
        service: ShipmentServiceDep
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
        service: ShipmentServiceDep
    ) -> dict[str, str]:
    await service.delete(shipment_id=shipment_id)
    return {"detail": f"Shipment #{shipment_id} deleted"}
