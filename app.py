from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import joblib
from preprocessing.cleaning_data import preprocess
from predict.prediction import predict_price as predict  # 
from typing import Literal, Optional
import uvicorn
from enum import Enum
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import HTTPException, Request

# Create the app instance
app = FastAPI()

# ------------------
# 🔹 Define input schema
# ------------------

class EPCScore(str, Enum):
    A_pluplus = 'A++', 
    A_plus = 'A+', 
    A='A' 
    B='B' 
    C='C'
    D='D' 
    E='E'
    F='F'
    G='G'

class BuildingState(str, Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    JUST_RENOVATED = "JUST RENOVATED"
    TO_BE_DONE_UP = "TO BE DONE UP"
    TO_RENOVATE = "TO RENOVATE"
    TO_RESTORE = "TO RESTORE"
    
class PropertyType(str, Enum):
    APARTMENT="APARTMENT"
    HOUSE="HOUSE"

class InputData(BaseModel):
    rooms_number: int
    area: float
    lift: Optional[bool] = False
    garden: Optional[bool] = False
    swimming_pool: Optional[bool] = False
    terrace: Optional[bool] = False
    parking: Optional[bool] = False
    epc_score: Optional[EPCScore]=Field(
        'E', description='EPC Score of the property. Options: A++, A+, A, B, C, D, E, F, G' 
    )
    building_state: Optional[BuildingState] = Field(
        'GOOD', description="Condition of the property. Options: NEW, GOOD, JUST RENOVATED, TO BE DONE UP, TO RENOVATE, TO RESTORE."
    )
    property_type: PropertyType = Field(description='Type of the property required. APARTMENT, HOUSE')
    #Literal["APARTMENT", "HOUSE"]
    """building_state: Optional[
        Literal["NEW", "GOOD", "JUST RENOVATED", "TO BE DONE UP", "TO RENOVATE", 
                "TO RESTORE"]
    ] = None"""
    zip_code: int

"""class RequestBody(BaseModel):
    data: InputData"""

# ----------- Routes -----------
@app.get("/")
def root():
    return {"message": "alive"}

@app.get("/predict")
def predict_info():
    return {
        "epc_score_options": [score.value for score in EPCScore],
        "building_state_options": [state.value for state in BuildingState],
        "property_type_options": [ptype.value for ptype in PropertyType]
    }

# Custom handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Custom handler for generic Exception
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

@app.post("/predict")
async def predict_endpoint(input_data: InputData):
    try:
        processed_data = preprocess(input_data.model_dump())
        price = predict(processed_data)
        return {"prediction": price, "status_code": 200}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"❌ Internal error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    

if __name__ == '__main__':
    uvicorn.run(app=app)
