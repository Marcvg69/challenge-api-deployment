import streamlit as st
#import requests

from preprocessing.cleaning_data import preprocess
from predict.prediction import predict_price

# FastAPI endpoint
#API_URL = "http://127.0.0.1:8000/predict"

        # linking front end with backend
        #response = requests.post(API_URL, json=input_data)
"""
        if response.status_code == 200:
            result = response.json()
            st.success(f"💶 Estimated Price: €{result['prediction']:,.0f}")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")"""

st.set_page_config(page_title="🏠 Real Estate Price Predictor", layout="centered")
st.title("🏠 Belgium Property Price Estimator")

# --- User Inputs ---
rooms_number = st.number_input("Number of rooms:", min_value=1, step=1)
area = st.number_input("Living area (m²):", min_value=10.0, step=1.0)
zip_code = st.number_input("Postal code:", min_value=1000, max_value=9992, step=1)

property_type = st.selectbox("Property Type:", ["APARTMENT", "HOUSE"])
building_state = st.selectbox(
    "Building state:",
    ["NEW", "JUST RENOVATED", "TO BE DONE UP", "GOOD", "TO RENOVATE", "TO RESTORE"]
)

lift = st.checkbox("Lift")
garden = st.checkbox("Garden")
terrace = st.checkbox("Terrace")
swimming_pool = st.checkbox("Swimming Pool")

if st.button("Predict price"):
    input_data = {
        "rooms_number": rooms_number,
        "area": area,
        "lift": lift,
        "garden": garden,
        "swimming_pool": swimming_pool,
        "terrace": terrace,
        "building_state": building_state,
        "property_type": property_type,
        "zip_code": zip_code
    }

    try:
        st.info("🔄 Preprocessing data locally...")
        processed = preprocess(input_data)

        st.info("🤖 Predicting price locally...")
        price = predict_price(processed)

        st.success(f"💶 Estimated property price: **€{price:,.0f}**")

    except Exception as e:
        st.error(f"❌ Error during local prediction: {e}")
