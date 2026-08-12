from typing import Any
from fastapi import FastAPI, status, HTTPException
from scalar_fastapi import get_scalar_api_reference

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

@app.get("/shipment/{field}")
def get_shipment_field(field: str, shipment_id: int) -> Any:
    return shipments[shipment_id][field]

# Query parameters
# Example /shipment?shipment_id=12800
@app.get("/shipment")
def get_shipment_query(shipment_id: int|None = None) -> dict[str, Any]:
    if not shipment_id:
        shipment_id = max(shipments.keys())
        return shipments[shipment_id]

    if shipment_id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The given shipment id does not exist"
        )

    return shipments[shipment_id]

@app.post("/shipment")
def submit_shipment(data: dict[str, Any]) -> dict[str, int]:

    if not all(key in data for key in ["weight", "content", "status"]):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="All fields are required"
        )

    weight = data["weight"]
    content = data["content"]
    shipment_status = data["status"]

    if weight > 25.0 or weight < 0.0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Maximum weight limit is 25kg"
        )

    new_id = max(shipments.keys()) + 1

    shipments[new_id] = {
        "content": content,
        "weight": weight,
        "status": shipment_status
    }

    return {"id": new_id}

# Path paramete
# Example /shipment/12800
@app.get("/shipment/{shipment_id}")
def get_shipment_path(shipment_id: int) -> dict[str, Any]:
    if shipment_id not in shipments:
        return {
            "detail": "The given shipment id does not exist"
        }

    return shipments[shipment_id]



# Scalar documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
