from app.schemas import ShipmentCreate, ShipmentUpdate, ShipmentRead, ShipmentStatus, ShipmentReplace
from app.services.shipment import ShipmentNotFound
from psycopg import AsyncConnection, sql
from psycopg.rows import DictRow, class_row


class RawShipmentService:
    _connection: AsyncConnection[DictRow]

    def __init__(self, connection: AsyncConnection[DictRow]):
        self._connection = connection

    async def get(self, shipment_id: int) -> ShipmentRead:
        async with self._connection.cursor(row_factory=class_row(ShipmentRead)) as cur:
            await cur.execute(
                "SELECT id, content, weight, status, destination, created_at FROM shipments WHERE id = %s",
                (shipment_id,))
            shipment = await cur.fetchone()

        if shipment is None:
            raise ShipmentNotFound(shipment_id)

        return shipment

    async def get_all(self, destination: str|None = None, status: ShipmentStatus|None = None) -> list[ShipmentRead]:
        conditions: list[sql.Composable] = []
        params: list[object] = []

        if destination is not None:
            conditions.append(sql.SQL("destination = %s"))
            params.append(destination)

        if status is not None:
            conditions.append(sql.SQL("status = %s"))
            params.append(status.value)

        parts: list[sql.Composable] = [
            sql.SQL("SELECT id, content, weight, status, destination, created_at FROM shipments")]

        if conditions:
            parts.append(sql.SQL("WHERE"))
            parts.append(sql.SQL(" AND ").join(conditions))

        parts.append(sql.SQL("ORDER BY id"))

        async with self._connection.cursor(row_factory=class_row(ShipmentRead)) as cur:
            await cur.execute(sql.SQL(" ").join(parts), params)
            return await cur.fetchall()

    async def create(self, shipment: ShipmentCreate) -> ShipmentRead:
        async with self._connection.cursor(row_factory=class_row(ShipmentRead)) as cur:
            await cur.execute(
                """
                INSERT INTO shipments (content, weight, destination)
                VALUES (%(content)s, %(weight)s, %(destination)s)
                RETURNING id, content, weight, status, destination, created_at
                """,
                shipment.model_dump(mode="json"),
            )
            created = await cur.fetchone()

        if created is None:
            raise RuntimeError("INSERT ... RETURNING returned no row")

        return created

    async def replace(self, shipment_id: int, shipment: ShipmentReplace) -> ShipmentRead:
        async with self._connection.cursor(row_factory=class_row(ShipmentRead)) as cur:
            await cur.execute(
                """
                UPDATE shipments
                SET content     = %(content)s,
                    weight      = %(weight)s,
                    status      = %(status)s,
                    destination = %(destination)s
                WHERE id = %(shipment_id)s
                RETURNING id, content, weight, status, destination, created_at
                """,
                {**shipment.model_dump(mode="json"), "shipment_id": shipment_id},
            )
            replaced = await cur.fetchone()

        if replaced is None:
            raise ShipmentNotFound(shipment_id)

        return replaced

    async def update(self, shipment_id: int, changes: ShipmentUpdate) -> ShipmentRead:
        fields = changes.model_dump(mode="json", exclude_unset=True)

        if not fields:
            return await self.get(shipment_id)

        assignments = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(field), sql.Placeholder(field)) for field in fields
        )

        query = sql.SQL(
            """UPDATE shipments SET {assignments} WHERE id = %(shipment_id)s
            RETURNING id, content, weight, status, destination, created_at"""
        ).format(assignments=assignments)

        async with self._connection.cursor(row_factory=class_row(ShipmentRead)) as cur:
            await cur.execute(query, {**fields, "shipment_id": shipment_id})
            updated = await cur.fetchone()

        if updated is None:
            raise ShipmentNotFound(shipment_id)

        return updated

    async def delete(self, shipment_id: int) -> None:
        async with self._connection.cursor() as cur:
            await cur.execute("DELETE FROM shipments WHERE id = %s", (shipment_id,))
            deleted = cur.rowcount

        if deleted == 0:
            raise ShipmentNotFound(shipment_id)
