# predict/prediction.py

# Import joblib to load the saved machine learning model
import joblib

# Import numpy for numerical array manipulation
import numpy as np

# Load the trained CatBoost model from the specified path.
# This happens once at the module level, so the model is ready to use as soon as this module is imported.
model = joblib.load("model/catboost.joblib")

def predict_price(data: np.ndarray) -> float:
    """
    Predicts the price of a property using the pre-trained CatBoost model.
    
    Parameters:
    - data (np.ndarray): A 2D NumPy array with a single row containing all the preprocessed
                         features expected by the model (in the right order).
    
    Returns:
    - float: The final predicted price, converted back from log scale and rounded to 2 decimals.
    """

    # Model outputs a log-transformed price, as this improves regression performance
    prediction = model.predict(data)
    
    # The prediction is a 1-element array; extract the first element
    log_price = prediction[0]

    # Convert the log price back to the original price scale using inverse of log1p (expm1)
    final_price = np.expm1(log_price)

    # Round the price to 2 decimal places for a clean result
    return float(round(final_price, 2))
