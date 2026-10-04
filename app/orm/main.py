from collections.abc import Sequence
from typing import Annotated, Literal
from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager
from app.orm.database.models import Shipment
from app.orm.database.session import engine, SessionDep
from app.schemas import ShipmentRead, ShipmentStatus, ShipmentCreate, ShipmentReplace, ShipmentUpdate
from sqlmodel import select, col
from rich import print, panel

@asynccontextmanager
async def lifespan_handler(_app: FastAPI):
    print(panel.Panel("Server started.", border_style="green"))
    yield
    await engine.dispose()
    print(panel.Panel("Server stopped.", border_style="green"))

app = FastAPI(lifespan=lifespan_handler)

async def existing_shipment_id(shipment_id: int, session: SessionDep) -> int:
    if not await session.get(Shipment, shipment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given ID shipment does not exist."
        )
    return shipment_id

IDDep = Annotated[int, Depends(existing_shipment_id)]

@app.get("/shipments", response_model=list[ShipmentRead])
async def get_shipments(
    session: SessionDep,
    destination: int|None = None,
    shipment_status: Annotated[ShipmentStatus|None, Query(alias="status")] = None,
) -> Sequence[Shipment]:
    statement = select(Shipment)

    if destination is not None:
        statement = statement.where(Shipment.destination == destination)

    if shipment_status is not None:
        statement = statement.where(Shipment.status == shipment_status)

    statement = statement.order_by(col(Shipment.id))

    return (await session.exec(statement)).all()

@app.get("/shipments/{shipment_id}", response_model=ShipmentRead)
async def get_shipment(shipment_id: IDDep, session: SessionDep) -> Shipment:
    # noinspection PyTypeChecker
    return await session.get_one(Shipment, shipment_id)

@app.get("/shipments/{shipment_id}/{field}")
async def get_shipment_field(
        shipment_id: IDDep,
        field: Literal["content", "weight", "status", "destination"],
        session: SessionDep
) -> str|float|int:
    shipment = await session.get_one(Shipment, shipment_id)
    return getattr(shipment, field)

@app.post("/shipments", status_code=status.HTTP_201_CREATED, response_model=ShipmentRead)
async def submit_shipment(shipment: ShipmentCreate, session: SessionDep, response: Response) -> Shipment:
    new_shipment = Shipment(**shipment.model_dump())
    session.add(new_shipment)
    await session.commit()
    await session.refresh(new_shipment)
    response.headers["Location"] = f"/shipments/{new_shipment.id}"
    return new_shipment

@app.put("/shipments/{shipment_id}", response_model=ShipmentRead)
async def update_shipment(shipment_id: IDDep, shipment: ShipmentReplace, session: SessionDep) -> Shipment:
    # noinspection PyTypeChecker
    stored_shipment: Shipment = await session.get_one(Shipment, shipment_id)
    stored_shipment.sqlmodel_update(shipment.model_dump())
    await session.commit()
    await session.refresh(stored_shipment)
    return stored_shipment

@app.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
async def patch_shipment(shipment_id: IDDep, shipment_patch: ShipmentUpdate, session: SessionDep) -> Shipment:
    changes = shipment_patch.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No fields to update."
        )

    # noinspection PyTypeChecker
    stored_shipment: Shipment = await session.get_one(Shipment, shipment_id)
    stored_shipment.sqlmodel_update(changes)
    await session.commit()
    await session.refresh(stored_shipment)
    return stored_shipment

@app.delete("/shipments/{shipment_id}", status_code=status.HTTP_200_OK)
async def delete_shipment(shipment_id: IDDep, session: SessionDep) -> dict[str, str]:
    await session.delete(await session.get_one(Shipment, shipment_id))
    await session.commit()
    return {"detail": f"Shipment #{shipment_id} deleted"}


# Scalar documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
