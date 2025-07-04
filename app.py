# A health check route at /
# A /predict endpoint with GET and POST methods
# Placeholder logic for loading the model, preprocessing, and prediction

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import joblib
from preprocessing.cleaning_data import preprocess
from predict.prediction import predict_price as predict  # 
from typing import List


# Create the app instance
app = FastAPI()

# ----------- Input Data Schema -----------
class InputData(BaseModel):
    area: int
    property_type: List[str] = ['APARTMENT', 'HOUSE']
    rooms_number = int
    zip_code: int
    garden: bool | None = None
    swimming_pool: bool | None = None
    terrace: bool | None = None
    building_state: List[str] = ["NEW", "GOOD", "JUST RENOVATED", 'TO BE DONE UP', "TO RENOVATE", "TO RESTORE"] | None

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
        processed_data = preprocess(input_dict)  # Preprocessing (your colleague Manu)
        price = predict(processed_data)          # Prediction function
        return {"prediction": price, "status_code": 200}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
