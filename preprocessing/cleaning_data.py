import pandas as pd
import numpy as np
import re

def is_valid_belgian_postcode(postcode: str) -> bool:
    if not re.fullmatch(r"\d{4}", postcode):
        return False
    num = int(postcode)
    return 1000 <= num <= 9992

def latitude_longitude_columns(df, filepath2):
        df_geo = pd.read_csv(filepath2, sep=';')
        #'data/georef-belgium-postal-codes@public.csv'
        pc_geo_dict = {}
        for pc in df['zip_code'].unique():
            geo_point = df_geo.loc[df_geo['Post code'] == pc, 'Geo Point'].values
            if len(geo_point) > 0:
                pc_geo_dict[pc] = geo_point[0]
            else:
                pc_geo_dict[pc] = None
        # creating a geocode column
        df['geocode'] = df['zip_code'].map(pc_geo_dict)

        # creating a latitude and longitude column
        df[['latitude', 'longitude']] = df['geocode'].str.split(',', expand=True)

        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)

        # dropping geo and postcde columns
        df.drop(columns=['geocode'], inplace=True)
        df.drop(columns=['zip_code'], inplace=True)
        return df

def add_region_columns(df):
    # Déduire région en fonction du zip_code (exemple simplifié)
    zip_code = df['zip_code'].iloc[0]
    if 1000 <= zip_code <= 1299:
        region = "Brussels"
    elif zip_code >= 1300 and zip_code <= 1499 or zip_code >= 4000 and zip_code <= 7999:
        region =  "Wallonia"
    else:
        region = 'Flanders'

    df['region_Brussels'] = 1 if region == 'Brussels' else 0
    df['region_Flanders'] = 1 if region == 'Flanders' else 0
    df['region_Wallonia'] = 1 if region == 'Wallonia' else 0

    return df  

def preprocess(input_dict: dict):
    #data = input_dict["data"]

    # Create DataFrame
    df = pd.DataFrame([input_dict])

    # Fill missing optional fields with defaults
    optional_fields = {
        "garden": False,
        "swimming_pool": False,
        "terrace": False,
        "building_state": 'TO BE DONE UP'
    }
    for key, default in optional_fields.items():
        if key not in df:
            df[key] = default
        df[key] = df[key].fillna(default)

    # Boolean fields to int
    bool_fields = ["garden", "swimming_pool", "terrace"] # parking
    for field in bool_fields:
        df[field] = df[field].astype(int)
    
    # Pre processing EPC Score and Building condition
    df["building_state"] = df["building_state"].map({
        "NEW": 0,
        "JUST RENOVATED": 1,
        "TO BE DONE UP": 2,
        "GOOD": 3,
        "TO RENOVATE": 4,
        "TO RESTORE": 5
    })
    if df["building_state"].isna().any():
        raise ValueError("Invalid building_state")
    
    # Map categorical fields to numeric
    df["property_type"] = df["property_type"].map({"APARTMENT": 0, "HOUSE": 1})
    if df["property_type"].isna().any():
        raise ValueError("Invalid property_type")
    
    # Add columns per "region"
    df = add_region_columns(df)
    
    # Checking valid postcode and transforming in latitude and longitude
    if not is_valid_belgian_postcode(str(df['zip_code'].iloc[0])):
        raise ValueError("Invalid zip_code")
    else:
        df=latitude_longitude_columns(df, 'data/georef-belgium-postal-codes@public.csv')    
    
    return df.values # returns a ndarray