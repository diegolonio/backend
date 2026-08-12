from typing import Any
from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

app = FastAPI()
feature_store = {}

@app.post("/users/{user_id}/features")
def new_user(user_id: int, user_data: dict[str, Any], api_key: str|None = None) -> dict[str, str]:
    if user_id < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid user ID."
        )

    if user_id in feature_store.keys():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists."
        )

    if not all(key in user_data for key in ["age", "monthly_income", "is_active"]):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="All features are required."
        )

    if not isinstance(user_data["age"], int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="age must be an integer."
        )

    if user_data["age"] < 18:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="User age must be at least 18 years old."
        )

    if not isinstance(user_data["monthly_income"], float):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="monthly_income must be a float."
        )

    if not isinstance(user_data["is_active"], bool):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="is_active must be a boolean."
        )

    if api_key is not None and api_key != "mle_admin_123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key."
        )

    feature_store[user_id] = user_data

    return {"success": "User created successfully."}

@app.get("/users/{user_id}/features")
def get_user_features(user_id: int, strict_mode: bool = False) -> dict[str, Any]:
    if user_id not in feature_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist."
        )

    if strict_mode and not feature_store[user_id]["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model can not predict on inactive users."
        )

    return feature_store[user_id]

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
