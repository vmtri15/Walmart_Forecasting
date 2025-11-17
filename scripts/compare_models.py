import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error

# Load real data (store 1 only)
real = pd.read_csv("data/walmart_prepared.csv")
real["Date"] = pd.to_datetime(real["Date"])
real = real[real["Store"] == 1]
real = real.groupby("Date")["Revenue"].sum().reset_index()

# Load Prophet
prophet = pd.read_csv("data/forecast_prophet_store_1.csv")
prophet["ds"] = pd.to_datetime(prophet["ds"])
prophet = prophet.rename(columns={"ds":"Date","yhat":"prophet_pred"})
prophet = prophet[["Date","prophet_pred"]]

# Load ARIMA
arima = pd.read_csv("data/arima_store_1.csv")
arima["Date"] = pd.to_datetime(arima["Date"])
arima = arima.groupby("Date")["forecast"].sum().reset_index()

# Load XGB
xgb = pd.read_csv("data/xgb_predictions.csv")
xgb["Date"] = pd.to_datetime(xgb["Date"], errors="coerce")
xgb_store = xgb[xgb["Store"] == 1]
xgb_store = xgb_store.groupby("Date")["xgb_pred"].sum().reset_index()

# ---- Merge aligned predictions ----
merged = (
    real.merge(prophet, on="Date", how="inner")
        .merge(arima, on="Date", how="inner")
        .merge(xgb_store, on="Date", how="inner")
)

# Clean missing
merged = merged.dropna(subset=["prophet_pred","forecast","xgb_pred"])

# Compute metrics
metrics = {
    "prophet_mape": mean_absolute_percentage_error(
        merged["Revenue"], merged["prophet_pred"]
    ),
    "arima_mape": mean_absolute_percentage_error(
        merged["Revenue"], merged["forecast"]
    ),
    "xgb_mape": mean_absolute_percentage_error(
        merged["Revenue"], merged["xgb_pred"]
    ),
}

print(metrics)
