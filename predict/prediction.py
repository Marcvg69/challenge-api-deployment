# predict/prediction.py
import joblib
import numpy as np

# Load the model once at module level
model = joblib.load("model/catboost_model.joblib")

def predict_price(data: np.ndarray) -> int:
    """Make a price prediction from preprocessed input"""
    prediction = model.predict(data)
    log_price = prediction[0]
    # transforms log price
    final_price = np.expm1(log_price)
    return int(round(final_price))

#prediction[0]

#return float(final_price)

    
