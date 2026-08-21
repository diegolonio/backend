from typing import Any, Annotated, Literal
from fastapi import FastAPI, status, HTTPException, Query
from scalar_fastapi import get_scalar_api_reference
from app.schemas import Shipment

app = FastAPI()

shipments = {
    12798: {
        "weight": 0.6,
        "content": "glassware",
        "status": "placed"
    },
    12799: {
        "weight": 1.2,
        "content": "electronics",
        "status": "shipped"
    },
    12800: {
        "weight": 0.3,
        "content": "documents",
        "status": "delivered"
    },
    12801: {
        "weight": 5.4,
        "content": "machinery parts",
        "status": "in_transit"
    },
    12802: {
        "weight": 2.1,
        "content": "textiles",
        "status": "placed"
    },
    12803: {
        "weight": 0.8,
        "content": "ceramics",
        "status": "pending"
    },
    12804: {
        "weight": 12.0,
        "content": "furniture",
        "status": "delivered"
    },
    12805: {
        "weight": 0.1,
        "content": "office supplies",
        "status": "shipped"
    }
}

@app.get("/shipments/{shipment_id}")
def get_shipment(
        shipment_id: int,
        field: Annotated[Literal["content", "weight", "status", "destination"]|None, Query()] = None
) -> Shipment|str|float|int:
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given ID shipment does not exist."
        )

    if field is not None:
        return shipments[shipment_id][field]

    return Shipment(**shipments[shipment_id])

@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def submit_shipment(shipment: Shipment) -> dict[str, int]:
    new_id = max(shipments.keys()) + 1
    shipments[new_id] = shipment.model_dump()

    return {"id": new_id}

@app.put("/shipments/{shipment_id}")
def update_shipment(shipment_id: int, shipment_data: dict[str, Any]) -> dict[str, Any]:
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given ID shipment does not exist."
        )

    if not all(key in shipment_data for key in ["weight", "content", "status"]):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="All fields are required"
        )

    shipments[shipment_id] = {
        "weight": shipment_data["weight"],
        "content": shipment_data["content"],
        "status": shipment_data["status"]
    }

    return shipments[shipment_id]

@app.patch("/shipments/{shipment_id}")
def patch_shipment(shipment_id: int, shipment_data: dict[str, Any]) -> dict[str, Any]:
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given ID shipment does not exist."
        )

    shipments[shipment_id].update(shipment_data)

    return shipments[shipment_id]

@app.delete("/shipments/{shipment_id}", status_code=status.HTTP_200_OK)
def delete_shipment(shipment_id: int) -> dict[str, str]:
    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given ID shipment does not exist."
        )

    shipments.pop(shipment_id)

    return {"detail": f"Shipment #{shipment_id} deleted"}


# Scalar documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
