import pandas as pd
import numpy as np


def preprocess(input_data: dict) -> pd.DataFrame:
    data = input_data["data"]

    # Create DataFrame
    df = pd.DataFrame([data])

    # Fill missing optional fields with defaults
    optional_fields = {
        "land-area": 0,
        "garden": False,
        "garden-area": 0,
        "equipped-kitchen": False,
        "full-address": "",
        "swimming-pool": False,
        "furnished": False,
        "open-fire": False,
        "terrace": False,
        "terrace-area": 0,
        "facades-number": 2,
        "building-state": "GOOD"
    }
    for key, default in optional_fields.items():
        df[key] = df.get(key, default).fillna(default)

    # Map categorical fields to numeric
    df["property-type"] = df["property-type"].map({"APARTMENT": 0, "HOUSE": 1, "OTHERS": 2})
    df["building-state"] = df["building-state"].map({
        "NEW": 0,
        "JUST RENOVATED": 1,
        "GOOD": 2,
        "TO RENOVATE": 3,
        "TO REBUILD": 4
    })

    # Boolean fields to int
    bool_fields = ["garden", "equipped-kitchen", "swimming-pool", "furnished", "open-fire", "terrace"]
    for field in bool_fields:
        df[field] = df[field].astype(int)

    # Drop irrelevant columns
    if "full-address" in df:
        df.drop(columns=["full-address"], inplace=True)

    return df
