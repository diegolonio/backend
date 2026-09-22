from typing import Annotated, Literal
from fastapi import FastAPI, status, HTTPException, Query, Depends, Response
from scalar_fastapi import get_scalar_api_reference
from app.schemas import ShipmentCreate, ShipmentReplace, ShipmentUpdate, ShipmentRead, ShipmentStatus
from psycopg import Connection, sql
from psycopg.rows import class_row
from app.raw.database.connection import get_connection

app = FastAPI()

def existing_shipment_id(shipment_id: int, conn: Annotated[Connection, Depends(get_connection)]) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM shipments WHERE id = %s", (shipment_id,))
        if cur.fetchone() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Given ID shipment does not exist."
            )
    return shipment_id

@app.get("/shipments")
def get_shipments(
        conn: Annotated[Connection, Depends(get_connection)],
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

    parts: list[sql.Composable] = [sql.SQL("SELECT id, content, weight, status, destination FROM shipments")]

    if conditions:
        parts.append(sql.SQL("WHERE"))
        parts.append(sql.SQL(" AND ").join(conditions))

    parts.append(sql.SQL("ORDER BY id"))

    with conn.cursor() as cur:
        cur.execute(sql.SQL(" ").join(parts), params)
        return cur.fetchall()

@app.get("/shipments/{shipment_id}")
def get_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        conn: Annotated[Connection, Depends(get_connection)]
) -> ShipmentRead:
    with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        cur.execute("SELECT id, content, weight, status, destination FROM shipments WHERE id = %s", (shipment_id,))
        return cur.fetchone()

@app.get("/shipments/{shipment_id}/{field}")
def get_shipment_field(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        field: Literal["content", "weight", "status", "destination"],
        conn: Annotated[Connection, Depends(get_connection)]
) -> str|float|int:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("SELECT {} FROM shipments WHERE id = %s").format(sql.Identifier(field)),
            (shipment_id,)
        )
        return cur.fetchone()[field]

@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def submit_shipment(
        shipment: ShipmentCreate,
        conn: Annotated[Connection, Depends(get_connection)],
        response: Response) -> ShipmentRead:
    with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        cur.execute(
            """
            INSERT INTO shipments (content, weight, destination)
            VALUES (%(content)s, %(weight)s, %(destination)s)
            RETURNING id, content, weight, status, destination
            """,
            shipment.model_dump(mode="json"),
        )
        created: ShipmentRead = cur.fetchone()
    response.headers["Location"] = f"/shipments/{created.id}"
    return created

@app.put("/shipments/{shipment_id}")
def update_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        shipment: ShipmentReplace,
        conn: Annotated[Connection, Depends(get_connection)]
) -> ShipmentRead:
    with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        cur.execute(
            """
            UPDATE shipments
            SET content = %(content)s, weight = %(weight)s,
                status = %(status)s, destination = %(destination)s
            WHERE id = %(shipment_id)s
            RETURNING id, content, weight, status, destination
            """,
            {**shipment.model_dump(mode="json"), "shipment_id": shipment_id},
        )
        return cur.fetchone()

@app.patch("/shipments/{shipment_id}")
def patch_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        shipment_patch: ShipmentUpdate,
        conn: Annotated[Connection, Depends(get_connection)]
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
           RETURNING id, content, weight, status, destination"""
    ).format(assignments=assignments)

    with conn.cursor(row_factory=class_row(ShipmentRead)) as cur:
        cur.execute(query, {**changes, "shipment_id": shipment_id})
        return cur.fetchone()

@app.delete("/shipments/{shipment_id}", status_code=status.HTTP_200_OK)
def delete_shipment(
        shipment_id: Annotated[int, Depends(existing_shipment_id)],
        conn: Annotated[Connection, Depends(get_connection)]
) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM shipments WHERE id = %s", (shipment_id,))
    return {"detail": f"Shipment #{shipment_id} deleted"}


# Scalar documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
