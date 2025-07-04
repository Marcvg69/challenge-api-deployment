import pandas as pd
import numpy as np
import pgeocode

# Initialize pgeocode Nominatim once for Belgium
nomi = pgeocode.Nominatim('BE')

def preprocess(input_data: dict) -> pd.DataFrame:
    # Create a single-row DataFrame from the input dictionary
    df = pd.DataFrame([input_data])

    # Rename 'rooms_number' to 'bedroomcount' if provided
    if "rooms_number" in df.columns:
        df.rename(columns={"rooms_number": "bedroomcount"}, inplace=True)

    # If 'property_type' is provided, map it to 'type_encoded'
    if "property_type" in df.columns:
        df["type_encoded"] = df["property_type"].map({
            "APARTMENT": 0,
            "HOUSE": 1,
            "OTHERS": 2
        }).fillna(2).astype(int)
        df.drop(columns=["property_type"], inplace=True)

    # Extract latitude and longitude from zip_code using pgeocode
    if "zip_code" in df.columns:
        zip_code = str(df["zip_code"].iloc[0])
        location = nomi.query_postal_code(zip_code)
        if pd.notna(location.latitude) and pd.notna(location.longitude):
            latitude = location.latitude
            longitude = location.longitude
        else:
            print(f"⚠️ Warning: Invalid or unknown zip code {zip_code}, using default lat/lon = 0.0")
            latitude = 0.0
            longitude = 0.0
    else:
        latitude = 0.0
        longitude = 0.0

    # Define all expected columns with defaults if missing
    defaults = {
        "bedroomcount": 0,
        "habitablesurface": 0.0,
        "haslift": 0,
        "hasgarden": 0,
        "hasswimmingpool": 0,
        "hasterrace": 0,
        "hasparking": 0,
        "epcscore_encoded": 3,
        "buildingcondition_encoded": 2,
        "region_Brussels": 0,
        "region_Flanders": 0,
        "region_Wallonia": 0,
        "type_encoded": 1,
        "latitude": latitude,
        "longitude": longitude
    }

    # Create missing columns or fill NaNs with defaults
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default)

    # Convert boolean columns to integers
    bool_cols = ["haslift", "hasgarden", "hasswimmingpool", "hasterrace", "hasparking"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # Force integer columns
    int_cols = ["bedroomcount", "haslift", "hasgarden", "hasswimmingpool", "hasterrace",
                "hasparking", "epcscore_encoded", "buildingcondition_encoded",
                "region_Brussels", "region_Flanders", "region_Wallonia", "type_encoded"]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Force float columns
    float_cols = ["habitablesurface", "latitude", "longitude"]
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)

    # Reorder columns for model compatibility
    ordered_columns = ['bedroomcount', 'habitablesurface', 'haslift', 'hasgarden',
                       'hasswimmingpool', 'hasterrace', 'hasparking', 'epcscore_encoded',
                       'buildingcondition_encoded', 'region_Brussels', 'region_Flanders',
                       'region_Wallonia', 'type_encoded', 'latitude', 'longitude']
    df = df[ordered_columns]

    return df
