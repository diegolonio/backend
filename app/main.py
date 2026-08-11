from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()

@app.get("/shipment/{id}")
def get_shipment(id: int):
    return {
        "id": id,
        "content": "wooden table",
        "status": "in transit"
    }



# Scalar documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
