import streamlit as st
import pandas as pd
from catboost import CatBoostRegressor
from joblib import load

# --- Load the trained CatBoost model ---
@st.cache_resource
def load_model():
    return load("model/catboost.joblib")

# --- Streamlit UI ---
st.title("🏠 Real Estate Price Predictor")

st.markdown("Enter property details to predict the price.")

# Example user inputs
postal_code = st.number_input("Postal Code", value=1000)
area = st.number_input("Area (m²)", value=100)
rooms = st.slider("Number of Rooms", 1, 10, value=3)
has_garden = st.checkbox("Has Garden?")
garden_area = st.number_input("Garden Area (m²)", value=0 if not has_garden else 20)
has_terrace = st.checkbox("Has Terrace?")
terrace_area = st.number_input("Terrace Area (m²)", value=0 if not has_terrace else 10)
facades = st.selectbox("Number of Facades", [2, 3, 4])
building_state = st.selectbox("Building Condition", ["NEW", "GOOD", "TO RENOVATE"])

# --- Prediction button ---
if st.button("Predict Price"):
    input_data = pd.DataFrame([{
        "postal_code": postal_code,
        "area": area,
        "rooms_number": rooms,
        "garden": has_garden,
        "garden_area": garden_area,
        "terrace": has_terrace,
        "terrace_area": terrace_area,
        "facades_number": facades,
        "building_state": building_state
    }])

    # Ensure categorical values are aligned with training
    input_data["building_state"] = input_data["building_state"].astype(str)

    # --- Run prediction ---
    prediction = model.predict(input_data)[0]
    st.success(f"💰 Estimated Price: €{round(prediction):,}")
