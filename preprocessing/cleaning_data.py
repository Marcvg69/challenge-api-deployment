from pydantic import BaseModel, model_validator
import pandas as pd
import numpy as np
import re
import json

@model_validator(mode='after')
def check_age_name(cls, data):
    if data.age < 18 and data.name.lower() == "admin":
        raise ValueError("Minors cannot be named admin")
    return data


def preprocess(input_dict: dict):
    data = input_dict["data"]

    # Create DataFrame
    df = pd.DataFrame([data])

    # Fill missing optional fields with defaults
    optional_fields = {
        "garden": False,
        "equipped-kitchen": False,
        "swimming-pool": False,
        "terrace": False,
        "building-state": None
    }
    for key, default in optional_fields.items():
        if key not in df:
            df[key] = default
        df[key] = df[key].fillna(default)

    # Map categorical fields to numeric
    df["property-type"] = df["property-type"].map({"APARTMENT": 0, "HOUSE": 1})
    if df["property-type"].isna().any():
        raise ValueError("Invalid property-type")

    df["building-state"] = df["building-state"].map({
        "NEW": 0,
        "JUST RENOVATED": 1,
        "TO BE DONE UP": 2,
        "GOOD": 3,
        "TO RENOVATE": 4,
        "TO RESTORE": 5
    })
    if df["building-state"].isna().any():
        raise ValueError("Invalid building-state")

    # Boolean fields to int
    bool_fields = ["garden", "equipped-kitchen", "swimming-pool", "terrace"]
    for field in bool_fields:
        df[field] = df[field].astype(int)
    
    # Save to file (optional)
    #df.to_json("data_preprocessed.json", orient="records", indent=2)

    # Return as Python object
    return df.to_dict(orient="records")

def is_valid_belgian_postcode(postcode: str) -> bool:
    if not re.fullmatch(r"\d{4}", postcode):
        return False
    num = int(postcode)
    return 1000 <= num <= 9992

def latitude_longitude_columns(self, filepath2):
        df_geo = pd.read_csv(filepath2, sep=';')
        #'data/georef-belgium-postal-codes@public.csv'
        pc_geo_dict = {}
        for pc in self.df['postcode'].unique():
            geo_point = df_geo.loc[df_geo['Post code'] == pc, 'Geo Point'].values
            if len(geo_point) > 0:
                pc_geo_dict[pc] = geo_point[0]
            else:
                pc_geo_dict[pc] = None
        # creating a geocode column
        self.df['geocode'] = self.df['postcode'].map(pc_geo_dict)

        # creating a latitude and longitude column
        self.df[['latitude', 'longitude']] = self.df['geocode'].str.split(',', expand=True)

        self.df['latitude'] = self.df['latitude'].astype(float)
        self.df['longitude'] = self.df['longitude'].astype(float)

        # dropping geo and postcde columns
        self.df.drop(columns=['geocode'], inplace=True)
        self.df.drop(columns=['postcode'], inplace=True)
