from joblib import load, dump
from catboost import CatBoostRegressor

model = CatBoostRegressor()
model.load_model("catboost_model.cbm")
dump(model, "catboost_model.pkl")
