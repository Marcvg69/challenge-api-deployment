from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import joblib
import pandas as pd

app = FastAPI()

# ------------------
# 🔹 Define input schema
# ------------------

class PropertyData(BaseModel):
    area: float
    property_type: str = Field(..., alias="property-type")
    rooms_number: int = Field(..., alias="rooms-number")
    zip_code: int = Field(..., alias="zip-code")
    land_area: Optional[float] = Field(None, alias="land-area")
    garden: Optional[bool] = None
    garden_area: Optional[float] = Field(None, alias="garden-area")
    equipped_kitchen: Optional[bool] = Field(None, alias="equipped-kitchen")
    full_address: Optional[str] = Field(None, alias="full-address")
    swimming_pool: Optional[bool] = Field(None, alias="swimming-pool")
    furnished: Optional[bool] = None
    open_fire: Optional[bool] = Field(None, alias="open-fire")
    terrace: Optional[bool] = None
    terrace_area: Optional[float] = Field(None, alias="terrace-area")
    facades_number: Optional[int] = Field(None, alias="facades-number")
    building_state: Optional[str] = Field(None, alias="building-state")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"  # Ignore unknown fields

class InputData(BaseModel):
    data: PropertyData


# ------------------
# 🔹 Load model and encoder
# ------------------

model = joblib.load("model/catboost_model.pkl")

# ------------------
# 🔹 Prediction endpoint
# ------------------

@app.post("/predict")
async def predict(request: Request):
    try:
        raw = await request.json()
        print("📦 Incoming raw request:", raw)

        # Check and parse "data"
        if "data" not in raw:
            raise HTTPException(status_code=400, detail="Missing 'data' field in request body.")

        # Parse to model (accept aliases like hyphens)
        parsed_data = InputData(**raw)
        data = parsed_data.data

        # Convert to DataFrame
        df = pd.DataFrame([data.dict(by_alias=True)])

        # Encode + Predict
        df_encoded = encoder.transform(df)
        prediction = model.predict(df_encoded)

        return {"predicted_price": float(prediction[0])}

    except Exception as e:
        print(f"❌ Internal error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
