import streamlit as st
from PIL import Image
from catboost import CatBoostRegressor
#from preprocessing import cleaning_data as cd
#from predict.prediction import predict_price as predict
import pandas as pd
import plotly.express as px
import time
import joblib
import json

from preprocessing.cleaning_data import preprocess
from predict.prediction import predict_price

import numpy as np

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="ImmoEliza - Real Estate Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# ---------- IMAGE BANNER ----------
image = Image.open("utils/ImmoEliza.png")
st.image(image, use_container_width=True)

# ---------- TITLE ----------
st.markdown("""
<style>
.title-section {
    text-align: center;
    margin-top: -20px;
}
.title-section h1 {
    font-size: 48px;
    color: #2c3e50;
    margin-bottom: 0px;
}
.title-section h3 {
    font-size: 20px;
    color: #7f8c8d;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='title-section'>
    <h1>ImmoEliza</h1>
    <h3>AI-Powered Real Estate Price Predictor in Belgium</h3>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📈 Predict", "📊 Visualize", "⚙️ Settings"])


# ---------- INIT SETTINGS ----------
if "use_lat_long" not in st.session_state:
    st.session_state.use_lat_long = True
if "use_region" not in st.session_state:
    st.session_state.use_region = True
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "show_progress" not in st.session_state:
    st.session_state.show_progress = True
if "viz_type" not in st.session_state:
    st.session_state.viz_type = "Histogram"
if "sample_size" not in st.session_state:
    st.session_state.sample_size = 500

# ---------- HOME ----------
if page == "🏠 Home":
    st.info("""
    Welcome to **ImmoEliza**, your smart assistant for estimating property prices in Belgium.

    Navigate using the sidebar:
    - **Predict** to estimate your property's price.
    - **Visualize** to analyze market data.
    - **Settings** to adjust your preferences.
    """)

# ---------- PREDICT ----------
elif page == "📈 Predict":
    st.write("### 🏡 Predict Property Price")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Area (m²)", min_value=10, max_value=1500, value=10)
            rooms_number = st.number_input("Number of bedrooms", min_value=0, max_value=15, value=0)
            zip_code = st.number_input("Zip code", min_value=1000, max_value=9992, value=1000)
        with col2:
            property_type = st.selectbox("Property Type", ["APARTMENT", "HOUSE"])
            building_state = st.selectbox("Building Condition", [
                "NEW", "GOOD", "JUST RENOVATED", "TO BE DONE UP", "TO RENOVATE", "TO RESTORE"
            ])
            lift = st.checkbox("Lift", value=False)
            terrace = st.checkbox("Terrace", value=False)
            garden = st.checkbox("Garden", value=False)
            swimming_pool = st.checkbox("Swimming Pool", value=False)

        submitted = st.form_submit_button("💰 Predict Price")
        input_data = {}

        if submitted:
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

# ---------- VISUALIZE ----------

elif page == "📊 Visualize":
    st.write("### 📊 Visualize Predictions on a Map")

    try:
        # 1️⃣ Load your cleaned data
        df = pd.read_csv("data/data_cleaned.csv")
        st.write(f"✅ Loaded {len(df)} properties for visualization.")

        # 2️⃣ Load your trained model
        model = joblib.load("model/catboost.joblib")

        # 3️⃣ Take a sample if needed
        sample_df = df.sample(n=min(st.session_state.sample_size, len(df)), random_state=42)

        # 4️⃣ Predict batch function
        def predict_batch(row):
            input_dict = {
                "rooms_number": row["bedroomcount"],
                "area": row["habitablesurface"],
                "lift": row.get("haslift", 0),
                "garden": row.get("hasgarden", 0),
                "swimming_pool": row.get("hasswimmingpool", 0),
                "terrace": row.get("hasterrace", 0),
                "building_state": "GOOD",
                "property_type": "HOUSE" if row["type_encoded"] == 1 else "APARTMENT",
                "zip_code": row.get("zip_code", 1000)
            }
            processed = preprocess(input_dict)
            return model.predict(processed)[0]

        # 5️⃣ Show progress bar
        st.info("Generating predictions, please wait...")
        predictions = []
        total = len(sample_df)

        if st.session_state.show_progress:
            progress_bar = st.progress(0, text="Starting predictions...")

        for i, row in sample_df.iterrows():
            pred = predict_batch(row)
            predictions.append(pred)
            if st.session_state.show_progress:
                progress = min((i + 1) / total, 1.0)
                progress_bar.progress(progress, text=f"Processing {i + 1}/{total}")

        sample_df["PredictedPrice"] = predictions
        # transform log price
        sample_df["PredictedPrice"] = np.expm1(sample_df["PredictedPrice"])
        sample_df["PredictedPrice"] = sample_df["PredictedPrice"].round(0).astype(int)
        st.success("✅ Predictions complete!")

        # 6️⃣ Add region and property type
        def get_region(row):
            if row.get("region_Brussels", 0) == 1:
                return "Brussels"
            elif row.get("region_Wallonia", 0) == 1:
                return "Wallonia"
            elif row.get("region_Flanders", 0) == 1:
                return "Flanders"
            else:
                return "Unknown"

        sample_df["Region"] = sample_df.apply(get_region, axis=1)
        sample_df["Property Type"] = sample_df["type_encoded"].apply(lambda x: "HOUSE" if x == 1 else "APARTMENT")

        # 7️⃣ Plot MAP (if you have lat/long)
        if "latitude" in sample_df.columns and "longitude" in sample_df.columns:
            fig = px.scatter_map(
                sample_df,
                lat="latitude",
                lon="longitude",
                color="PredictedPrice",
                size="PredictedPrice",
                #hover_name="zip_code",
                hover_data=["Region", "Property Type"],
                color_continuous_scale=px.colors.sequential.Viridis,
                size_max=15,
                zoom=7,
                title="Predicted Prices on Map"
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("❗ Latitude/Longitude columns missing. Cannot plot map.")

        # 8️⃣ Let user download CSV
        csv = sample_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "💾 Download Predictions CSV",
            csv,
            "predicted_properties.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(f"❌ Could not generate visualization: {e}")
        st.exception(e)