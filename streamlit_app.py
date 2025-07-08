import streamlit as st
from prediction import predict_price
import pandas as pd
from catboost import CatBoostRegressor

@st.cache_resource
def load_model():
    # Load the CatBoost model from .cbm format — ensure this file exists in 'model/'
    model = CatBoostRegressor()
    model.load_model("model/catboost_model.cbm")  # use .cbm NOT .joblib
    return model

model = load_model()

st.set_page_config(page_title="Real Estate Price Predictor", layout="centered")

st.title("🏡 Real Estate Price Prediction")
st.write("Fill in the property details below to get a price estimate.")

# --- Form inputs
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        area = st.number_input("Area (m²)", value=100)
        rooms_number = st.number_input("Number of rooms", value=3)
        zip_code = st.number_input("ZIP code", value=1000)
        land_area = st.number_input("Land area (m²)", value=200)
        garden = st.checkbox("Garden")
        garden_area = st.number_input("Garden area (m²)", value=0 if not garden else 50)

    with col2:
        equipped_kitchen = st.checkbox("Equipped kitchen")
        full_address = st.text_input("Full address", value="1000 Brussels")
        swimming_pool = st.checkbox("Swimming pool")
        furnished = st.checkbox("Furnished")
        open_fire = st.checkbox("Open fire")
        terrace = st.checkbox("Terrace")
        terrace_area = st.number_input("Terrace area (m²)", value=0 if not terrace else 15)
        facades_number = st.number_input("Number of facades", value=2)
        building_state = st.selectbox("Building state", ["NEW", "GOOD", "TO RENOVATE", "JUST RENOVATED"])
        property_type = st.selectbox("Property type", ["HOUSE", "APARTMENT"])

    submitted = st.form_submit_button("Predict Price 💰")

# --- Prediction
if submitted:
    input_data = {
        "area": area,
        "property_type": property_type,
        "rooms_number": rooms_number,
        "zip_code": zip_code,
        "land_area": land_area,
        "garden": garden,
        "garden_area": garden_area,
        "equipped_kitchen": equipped_kitchen,
        "full_address": full_address,
        "swimming_pool": swimming_pool,
        "furnished": furnished,
        "open_fire": open_fire,
        "terrace": terrace,
        "terrace_area": terrace_area,
        "facades_number": facades_number,
        "building_state": building_state
    }

    # Convert to DataFrame (optional depending on your predict_price function)
    df = pd.DataFrame([input_data])

    try:
        price = predict_price(model, df)
        st.success(f"💸 Estimated price: €{int(price):,}")
    except Exception as e:
        st.error(f"Prediction failed: {e}")
