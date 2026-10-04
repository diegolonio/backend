from typing import Annotated, Literal
from fastapi import APIRouter, status, HTTPException, Query, Depends, Response
from app.schemas import ShipmentCreate, ShipmentReplace, ShipmentUpdate, ShipmentRead, ShipmentStatus
from psycopg import sql
from psycopg.rows import class_row
from app.raw.database.connection import ConnDep

router = APIRouter(prefix="/raw", tags=["Raw"])

async def existing_shipment_id(shipment_id: int, conn: ConnDep) -> int:
    async with conn.cursor() as cur:
        await cur.execute("SELECT 1 FROM shipments WHERE id = %s", (shipment_id,))
        if await cur.fetchone() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Given ID shipment does not exist."
            )
    return shipment_id

@router.get("/shipments")
async def get_shipments(
        conn: ConnDep,
        destination: int|None = None,
        shipment_status: Annotated[ShipmentStatus|None, Query(alias="status")] = None,
) -> list[ShipmentRead]:
    conditions: list[sql.Composable] = []
    params: list[object] = []

    if destination is not None:
        conditions.append(sql.SQL("destination = %s"))
        params.append(destination)

    if shipment_status is not None:
        conditions.append(sql.SQL("status = %s"))
        params.append(shipment_status.value)

    parts: list[sql.Composable] = [sql.SQL("SELECT id, content, weight, status, destination, created_at FROM shipments")]

    if conditions:
        parts.append(sql.SQL("WHERE"))
        parts.append(sql.SQL(" AND ").join(conditions))

    parts.append(sql.SQL("ORDER BY id"))

    async with conn.cursor() as cur:
        await cur.execute(sql.SQL(" ").join(parts), params)
        return await cur.fetchall()

@router.get("/shipments/{shipment_id}")
async def get_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        conn: ConnDep
) -> ShipmentRead:
    async with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        await cur.execute("SELECT id, content, weight, status, destination, created_at FROM shipments WHERE id = %s", (shipment_id,))
        return await cur.fetchone()

@router.get("/shipments/{shipment_id}/{field}")
async def get_shipment_field(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        field: Literal["content", "weight", "status", "destination"],
        conn: ConnDep
) -> str|float|int:
    async with conn.cursor() as cur:
        await cur.execute(
            sql.SQL("SELECT {} FROM shipments WHERE id = %s").format(sql.Identifier(field)),
            (shipment_id,)
        )
        return (await cur.fetchone())[field]

@router.post("/shipments", status_code=status.HTTP_201_CREATED)
async def submit_shipment(
        shipment: ShipmentCreate,
        conn: ConnDep,
        response: Response) -> ShipmentRead:
    async with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        await cur.execute(
            """
            INSERT INTO shipments (content, weight, destination)
            VALUES (%(content)s, %(weight)s, %(destination)s)
            RETURNING id, content, weight, status, destination, created_at
            """,
            shipment.model_dump(mode="json"),
        )
        created: ShipmentRead = await cur.fetchone()
    response.headers["Location"] = f"{router.prefix}/shipments/{created.id}"
    return created

@router.put("/shipments/{shipment_id}")
async def update_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        shipment: ShipmentReplace,
        conn: ConnDep
) -> ShipmentRead:
    async with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        await cur.execute(
            """
            UPDATE shipments
            SET content = %(content)s, weight = %(weight)s,
                status = %(status)s, destination = %(destination)s
            WHERE id = %(shipment_id)s
            RETURNING id, content, weight, status, destination, created_at
            """,
            {**shipment.model_dump(mode="json"), "shipment_id": shipment_id},
        )
        return await cur.fetchone()

@router.patch("/shipments/{shipment_id}")
async def patch_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        shipment_patch: ShipmentUpdate,
        conn: ConnDep
) -> ShipmentRead:
    changes = shipment_patch.model_dump(mode="json", exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No fields to update."
        )

    assignments = sql.SQL(", ").join(
        sql.SQL("{} = {}").format(sql.Identifier(field), sql.Placeholder(field)) for field in changes
    )

    query = sql.SQL(
        """UPDATE shipments SET {assignments} WHERE id = %(shipment_id)s
           RETURNING id, content, weight, status, destination, created_at"""
    ).format(assignments=assignments)

    async with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        await cur.execute(query, {**changes, "shipment_id": shipment_id})
        return await cur.fetchone()

@router.delete("/shipments/{shipment_id}", status_code=status.HTTP_200_OK)
async def delete_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        conn: ConnDep
) -> dict[str, str]:
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM shipments WHERE id = %s", (shipment_id,))
    return {"detail": f"Shipment #{shipment_id} deleted"}
