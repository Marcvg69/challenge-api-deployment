# predict/prediction.py
import joblib
import numpy as np

# Load the model once at module level
model = joblib.load("model/catboost_model.joblib")

def predict_price(data: np.ndarray) -> float:
    """Make a price prediction from preprocessed input"""
    prediction = model.predict(data)
    return prediction[0]
