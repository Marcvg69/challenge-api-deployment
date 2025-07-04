# A health check route at /
# A /predict endpoint with GET and POST methods
# Placeholder logic for loading the model, preprocessing, and prediction

from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from preprocessing.cleaning_data import preprocess
from predict.prediction import predict_price as predict  
import numpy as np

# Create the app instance
app = FastAPI()

# ----------- Input Data Schema -----------
class InputData(BaseModel):
    area: int
    property_type: Literal["APARTMENT", "HOUSE", "OTHERS"]
    rooms_number: int
    zip_code: int
    land_area: Optional[int] = None
    garden: Optional[bool] = None
    garden_area: Optional[int] = None
    equipped_kitchen: Optional[bool] = None
    full_address: Optional[str] = None
    swimming_pool: Optional[bool] = None
    furnished: Optional[bool] = None
    open_fire: Optional[bool] = None
    terrace: Optional[bool] = None
    terrace_area: Optional[int] = None
    facades_number: Optional[int] = None
    building_state: Optional[
        Literal["NEW", "GOOD", "TO RENOVATE", "JUST RENOVATED", "TO REBUILD"]
    ] = None

class RequestBody(BaseModel):
    data: InputData

# ----------- Routes -----------
@app.get("/")
def root():
    return {"message": "alive"}

@app.get("/predict")
def predict_info():
    return {
        "message": "Send a POST request to /predict with JSON body in the specified input format to get a price prediction."
    }

@app.post("/predict")
def predict_price(request_body: RequestBody):
    try:
        input_dict = request_body.data.model_dump()
        print(f"input_dict: {input_dict}")
        processed_data = preprocess(input_dict)  # Preprocessing (your colleague Manu)
        price = predict(processed_data)          # Prediction function
        price = round(np.expm1(price))  # arrondi to euro

        return {"prediction": f"{price} €", "status_code": 200}
    except ValueError as ve:
        print(f"ValueError: {ve}")  # Add for debug
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Internal Error: {e}")  # Add for debug
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    
