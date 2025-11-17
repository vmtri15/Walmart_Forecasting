import pandas as pd
from xgboost import XGBRegressor

df = pd.read_csv("data/walmart_prepared.csv")
stores = df["Store"].unique()

features = [
    "Lag_1","Lag_2","Lag_4","Lag_12",
    "Rolling_4w","Rolling_12w",
    "CPI","Fuel_Price","Unemployment","IsHoliday"
]

for store_id in stores:
    store_df = df[df["Store"] == store_id]

    for dept in store_df["Dept"].unique():
        sub = store_df[store_df["Dept"] == dept].dropna(subset=features)

        if len(sub) < 30:
            continue

        X = sub[features]
        y = sub["Revenue"]

        model = XGBRegressor()
        model.fit(X, y)

        sub["xgb_pred"] = model.predict(X)
        out = f"data/xgb_store_{store_id}_dept_{dept}.csv"
        sub[["Date","Store","Dept","xgb_pred"]].to_csv(out, index=False)

        print("Saved", out)
