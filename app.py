# ---------- Imports ----------
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from fastapi.responses import JSONResponse
from preprocessing.cleaning_data import preprocess
from predict.prediction import predict_price as predict
import uvicorn
import os

# ---------- Configuration ----------
# Get port from environment variable (used when deploying on platforms like Render)
PORT = os.environ.get("PORT", 8000)

# Create the FastAPI app instance
app = FastAPI()

# ---------- Enums ----------
# These enums define valid options for dropdowns in frontend or validations

class BuildingState(str, Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    JUST_RENOVATED = "JUST RENOVATED"
    TO_BE_DONE_UP = "TO BE DONE UP"
    TO_RENOVATE = "TO RENOVATE"
    TO_RESTORE = "TO RESTORE"

class PropertyType(str, Enum):
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"

# ---------- Input Schema ----------
# Defines what data the API expects from a POST /predict request
class InputData(BaseModel):
    rooms_number: int = Field(..., gt=0, description="Number of rooms. Must be greater than 0.")
    area: float = Field(..., gt=10, description="Area in m². Must be greater than 10.")
    lift: Optional[bool] = False
    garden: Optional[bool] = False
    swimming_pool: Optional[bool] = False 
    terrace: Optional[bool] = False
    building_state: Optional[BuildingState] = Field(
        'TO BE DONE UP',
        description="Options: NEW, GOOD, JUST RENOVATED, TO BE DONE UP, TO RENOVATE, TO RESTORE."
    )
    property_type: PropertyType = Field(description="Options: APARTMENT, HOUSE")
    zip_code: int  # Required: 4-digit Belgian postal code

# ---------- Output Schema ----------
class PredictionResponse(BaseModel):
    prediction: Optional[float]  # Predicted price
    status_code: Optional[int]   # HTTP status (usually 200)

# ---------- Utility (unused) ----------
# Helper function to get data from frontend (commented out for now)
"""
def get_frontend_data():
    url = "http://host.docker.internal:3000/"
    try:
        response = Request.get(url)
        response.raise_for_status()
        return response.json()
    except Request.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

# ---------- Routes ----------
@app.get("/")
def root():
    return {"message": "alive"}  # Health check endpoint

@app.get("/predict")
def predict_info():
    # Returns dropdown values for use in frontend (e.g., select menus)
    return {
        "building_state_options": [state.value for state in BuildingState],
        "property_type_options": [ptype.value for ptype in PropertyType]
    }

# ---------- Custom Exception Handlers ----------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# ---------- Main Prediction Endpoint ----------
@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(input_data: InputData):
    try:
        # Convert to dictionary and preprocess
        processed_data = preprocess(input_data.model_dump())

        # Get prediction
        price = predict(processed_data)

        return {"prediction": price, "status_code": 200}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"❌ Internal error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# ---------- Run App Locally ----------
if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=int(PORT))
