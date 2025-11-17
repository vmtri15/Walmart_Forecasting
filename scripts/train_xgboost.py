import pandas as pd
from xgboost import XGBRegressor

df = pd.read_csv("data/walmart_prepared.csv")

features = [
    "Lag_1","Lag_2","Lag_4","Lag_12",
    "Rolling_4w","Rolling_12w",
    "CPI","Fuel_Price","Unemployment",
    "IsHoliday"
]

df = df.dropna(subset=features)

X = df[features]
y = df["Revenue"]

model = XGBRegressor()
model.fit(X, y)

df["xgb_pred"] = model.predict(X)
df.to_csv("data/xgb_predictions.csv", index=False)

print("Saved data/xgb_predictions.csv")
