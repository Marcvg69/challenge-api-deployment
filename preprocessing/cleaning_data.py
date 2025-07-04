import pandas as pd
import numpy as np


def preprocess(data: dict) -> pd.DataFrame:
    # Your preprocessing logic here (fill missing, encode, etc.)
    # For now you can just turn it into a DataFrame
    df = pd.DataFrame([data])
    return df


