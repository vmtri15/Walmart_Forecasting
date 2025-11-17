import pandas as pd
from xgboost import XGBRegressor
import os

df = pd.read_csv("data/walmart_prepared.csv")
stores = df["Store"].unique()

features = [
    "Lag_1","Lag_2","Lag_4","Lag_12",
    "Rolling_4w","Rolling_12w",
    "CPI","Fuel_Price","Unemployment","IsHoliday"
]

for store_id in stores:
    s = df[df["Store"] == store_id].dropna(subset=features)

    X = s[features]
    y = s["Revenue"]

    model = XGBRegressor()
    model.fit(X, y)

    s["xgb_pred"] = model.predict(X)
    out = f"data/xgb_store_{store_id}.csv"
    s[["Date","Store","xgb_pred"]].to_csv(out, index=False)

    print("Saved", out)
