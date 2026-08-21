from pydantic import BaseModel, Field

class Shipment(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(gt=0, le=25)
    status: str = Field(max_length=20, default="placed")
    destination: int|None = Field(default=None)
