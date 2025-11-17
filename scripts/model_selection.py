import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error

# Load base data to get store list
full = pd.read_csv("data/walmart_prepared.csv")
full["Date"] = pd.to_datetime(full["Date"])
stores = sorted(full["Store"].unique())

results = []

for s in stores:
    print(f"\nProcessing store {s}...")

    # ----- REAL DATA -----
    real = full[full["Store"] == s].copy()
    real = real.groupby("Date")["Revenue"].sum().reset_index()

    # ----- PROPHET -----
    try:
        p = pd.read_csv(f"data/forecast_prophet_store_{s}.csv")
        p["ds"] = pd.to_datetime(p["ds"])
        p = p.rename(columns={"ds": "Date", "yhat": "prophet_pred"})
        p = p[["Date", "prophet_pred"]]
    except:
        print(f"  Prophet missing for store {s}. Skipping.")
        continue

    # ----- ARIMA -----
    try:
        a = pd.read_csv(f"data/arima_store_{s}.csv")
        a["Date"] = pd.to_datetime(a["Date"])

        # Standardize column naming
        if "forecast" in a.columns:
            pass
        elif "predicted_mean" in a.columns:
            a = a.rename(columns={"predicted_mean": "forecast"})
        else:
            print(f"  ARIMA missing forecast column for store {s}. Skipping.")
            continue

        a = a[["Date", "forecast"]]
        a = a.groupby("Date")["forecast"].sum().reset_index()

    except:
        print(f"  Error loading ARIMA for store {s}. Skipping.")
        continue

    # ----- XGBoost -----
    try:
        x = pd.read_csv("data/xgb_predictions.csv")
        x["Date"] = pd.to_datetime(x["Date"], errors="coerce")

        # Store-level aggregation
        x_store = x[x["Store"] == s]
        x_store = x_store.groupby("Date")["xgb_pred"].sum().reset_index()

        x_store = x_store[["Date", "xgb_pred"]]
    except:
        print(f"  XGB missing for store {s}. Skipping.")
        continue

    # ----- MERGE ALL -----
    merged = (
        real.merge(p, on="Date", how="inner")
            .merge(a, on="Date", how="inner")
            .merge(x_store, on="Date", how="inner")
    )

    if len(merged) < 10:
        print(f"  Not enough overlapping dates for store {s}. Skipping.")
        continue

    # ----- METRICS -----
    try:
        pm = mean_absolute_percentage_error(merged["Revenue"], merged["prophet_pred"])
        am = mean_absolute_percentage_error(merged["Revenue"], merged["forecast"])
        xm = mean_absolute_percentage_error(merged["Revenue"], merged["xgb_pred"])
    except Exception as e:
        print(f"  Error computing MAPE for store {s}: {e}")
        continue

    best = min(
        [("prophet", pm), ("arima", am), ("xgb", xm)],
        key=lambda x: x[1]
    )

    results.append({
        "Store": s,
        "Prophet_MAPE": pm,
        "ARIMA_MAPE": am,
        "XGB_MAPE": xm,
        "Best_Model": best[0]
    })

    print(f"  Prophet MAPE: {pm:.4f}")
    print(f"  ARIMA MAPE:   {am:.4f}")
    print(f"  XGB MAPE:     {xm:.4f}")
    print(f"  Best Model:   {best[0]}")

# ----- SAVE SUMMARY -----
df_results = pd.DataFrame(results)
df_results.to_csv("data/model_selection_summary.csv", index=False)

print("\nSaved model_selection_summary.csv")
