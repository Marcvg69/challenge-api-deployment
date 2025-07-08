import streamlit as st
from PIL import Image
from catboost import CatBoostRegressor
from preprocessing import cleaning_data as cd
from predict.prediction import predict_price as predict
import pandas as pd
import plotly.express as px
import time

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="ImmoEliza - Real Estate Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# ---------- IMAGE BANNER ----------
image = Image.open("ImmoEliza.png")
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
            area = st.number_input("Living area (m²):", min_value=10, step=1)
            rooms_number = st.number_input("Number of rooms:", min_value=1, step=1)
            zip_code = st.number_input("Postal code:", min_value=1000, max_value=9992, step=1)
        with col2:
            property_type = st.selectbox("Property Type:", ["APARTMENT", "HOUSE"])
            building_state = st.selectbox(
                "Building state:",
                ["NEW", "JUST RENOVATED", "TO BE DONE UP", "GOOD", "TO RENOVATE", "TO RESTORE"]
            )
            lift = st.checkbox("Lift")
            garden = st.checkbox("Garden")
            terrace = st.checkbox("Terrace")
            swimming_pool = st.checkbox("Swimming Pool")

        submitted = st.form_submit_button("💰 Predict Price")

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

            # Adapt settings without modifying preprocess
            input_data_adapted = input_data.copy()
            if not st.session_state.use_region:
                input_data_adapted["zip_code"] = 9999
            if not st.session_state.use_lat_long:
                input_data_adapted["zip_code"] = "0000"

            try:
                with st.spinner("🔄 Preprocessing data locally..."):
                    processed = cd.preprocess(input_data_adapted)

                with st.spinner("🤖 Predicting price locally..."):
                    price = predict(processed)

                st.success(f"💶 Estimated property price: **€{price:,.0f}**")

            except Exception as e:
                st.error(f"❌ Error during prediction: {e}")
                st.exception(e)

# ---------- VISUALIZE ----------
elif page == "📊 Visualize":
    st.write("### 📊 Visualize Predicted Prices by Region")

    try:
        df = pd.read_csv("data/data_cleaned.csv")
        st.write(f"✅ Loaded {len(df)} properties for visualization.")

        sample_df = df.sample(n=min(st.session_state.sample_size, len(df)), random_state=42)

        def predict_batch(row):
            input_dict = {
                "habitablesurface": row["habitablesurface"],
                "bedroomcount": row["bedroomcount"],
                "zip_code": row.get("zip_code", 1000),
                "property_type": "HOUSE" if row["type_encoded"] == 1 else "APARTMENT",
                "building_state": "GOOD",
                "hasterrace": row.get("hasterrace", 0),
                "hasgarden": row.get("hasgarden", 0),
                "hasswimmingpool": row.get("hasswimmingpool", 0),
            }

            input_dict_adapted = input_dict.copy()
            if not st.session_state.use_region:
                input_dict_adapted["zip_code"] = 9999
            if not st.session_state.use_lat_long:
                input_dict_adapted["zip_code"] = "0000"

            try:
                processed = cd.preprocess(input_dict_adapted)
                return predict(processed)
            except:
                return None

        st.info("Generating predictions, please wait...")

        predictions = []
        start_time = time.time()
        total = max(len(sample_df), 1)

        if st.session_state.show_progress:
            progress_bar = st.progress(0, text="Starting predictions...")

        for i, row in sample_df.iterrows():
            pred = predict_batch(row)
            predictions.append(pred)
            if st.session_state.show_progress:
                progress = min((i + 1) / total, 1.0)
                progress_bar.progress(progress, text=f"Processing {i + 1}/{total}")

        sample_df["PredictedPrice"] = predictions

        end_time = time.time()
        minutes, seconds = divmod(end_time - start_time, 60)
        st.success(f"✅ Predictions generated in {int(minutes)} min {int(seconds)} sec.")

        def get_region(row):
            if row.get("region_Brussels", 0) == 1:
                return "Brussels"
            elif row.get("region_Wallonia", 0) == 1:
                return "Wallonia"
            elif row.get("region_Flanders", 0) == 1:
                return "Flanders"
            else:
                return "Unknown"

        def get_property_type(row):
            return "HOUSE" if row.get("type_encoded") == 1 else "APARTMENT"

        sample_df["Region"] = sample_df.apply(get_region, axis=1)
        sample_df["Property Type"] = sample_df.apply(get_property_type, axis=1)

        if st.session_state.viz_type == "Histogram":
            fig = px.histogram(
                sample_df.dropna(subset=["PredictedPrice"]),
                x="Region",
                y="PredictedPrice",
                color="Property Type",
                nbins=50,
                histfunc="avg",
                title="Average Predicted Price per Property Type and Region",
                labels={"PredictedPrice": "Predicted Price (€)"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
        else:
            fig = px.box(
                sample_df.dropna(subset=["PredictedPrice"]),
                x="Region",
                y="PredictedPrice",
                color="Property Type",
                title="Predicted Price Distribution per Property Type and Region",
                labels={"PredictedPrice": "Predicted Price (€)"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Could not generate visualization: {e}")
        st.exception(e)

# ---------- SETTINGS ----------
elif page == "⚙️ Settings":
    st.write("### ⚙️ Settings")

    st.subheader("Prediction Preferences")
    st.session_state.use_lat_long = st.checkbox("Use Latitude/Longitude Features", value=st.session_state.use_lat_long)
    st.session_state.use_region = st.checkbox("Use Region Features", value=st.session_state.use_region)
    st.session_state.sample_size = st.number_input("Sample Size for Visualization", min_value=10, max_value=5000, value=st.session_state.sample_size)

    st.subheader("Interface Preferences")
    st.session_state.theme = st.radio("Choose Theme", ["Light", "Dark"], index=["Light", "Dark"].index(st.session_state.theme))
    st.session_state.show_progress = st.checkbox("Show Progress Bar in Visualize", value=st.session_state.show_progress)
    st.session_state.viz_type = st.selectbox("Visualization Type", ["Histogram", "Boxplot"], index=["Histogram", "Boxplot"].index(st.session_state.viz_type))

    if st.button("Reset to Defaults"):
        st.session_state.use_lat_long = True
        st.session_state.use_region = True
        st.session_state.theme = "Light"
        st.session_state.show_progress = True
        st.session_state.viz_type = "Histogram"
        st.session_state.sample_size = 500
        st.success("Settings have been reset. Please reload the page to apply.")

    st.info("⚡ All settings are currently local and will persist during your session.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>ImmoEliza © 2025 - Powered by Streamlit</center>", unsafe_allow_html=True)
