"""
Time based holdout comparison of Prophet, ARIMA, and XGBoost for every store.

Why this exists
---------------
The original model_selection.py scored all three models on the same dates they
were trained on, and prep_data.py built Rolling_4w / Rolling_12w with windows
that include the current week's revenue (the value being predicted).
This script fixes both:
  * Every model is fit on weeks BEFORE the holdout only.
  * Every model forecasts the last HOLDOUT weeks multi step (no peeking).
  * XGBoost features use only past weeks. Lags and rolling means exclude the
    week being predicted, and are rebuilt recursively from earlier predictions.
  * A seasonal naive baseline (same week last year) is reported for reference.

Run from the project root:
    python scripts/holdout_evaluation.py
Output:
    data/holdout_predictions.csv  (actual vs each model, last HOLDOUT weeks per store)
    data/holdout_summary.csv   (does not overwrite model_selection_summary.csv)
"""
import sys
import logging
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error as mape
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from xgboost import XGBRegressor

logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
logging.getLogger("prophet").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

DATA_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/walmart_prepared.csv"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "data/holdout_summary.csv"
HOLDOUT = 12  # weeks held out at the end of each store's history
EXOG = ["CPI", "Fuel_Price", "Unemployment", "IsHoliday"]


def load_store_weeks(path):
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["IsHoliday"] = df["IsHoliday"].astype(int)
    wk = (
        df.groupby(["Store", "Date"])
        .agg(
            Revenue=("Revenue", "sum"),
            CPI=("CPI", "mean"),
            Fuel_Price=("Fuel_Price", "mean"),
            Unemployment=("Unemployment", "mean"),
            IsHoliday=("IsHoliday", "max"),
        )
        .reset_index()
        .sort_values(["Store", "Date"])
        .reset_index(drop=True)
    )
    return wk


def feature_row(hist, exog_row):
    """Features for the next week, using only values already in `hist`."""
    h = np.asarray(hist, dtype=float)
    return [
        h[-1], h[-2], h[-4], h[-12],
        h[-4:].mean(), h[-12:].mean(),
        *exog_row,
    ]


def xgb_forecast(y_train, exog_train, exog_test):
    X, t = [], []
    for i in range(12, len(y_train)):
        X.append(feature_row(y_train[:i], exog_train[i]))
        t.append(y_train[i])
    model = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=3, random_state=0)
    model.fit(np.array(X), np.array(t))

    hist = list(y_train)
    preds = []
    for j in range(len(exog_test)):
        p = float(model.predict(np.array([feature_row(hist, exog_test[j])]))[0])
        preds.append(p)
        hist.append(p)  # recursive: later steps rely on earlier predictions
    return np.array(preds)


def arima_forecast(y_train, steps):
    fit = ARIMA(y_train, order=(3, 1, 3)).fit()
    return np.clip(np.asarray(fit.forecast(steps)), 0, None)


def prophet_forecast(dates_train, y_train, dates_test):
    m = Prophet(weekly_seasonality=True, yearly_seasonality=True)
    m.fit(pd.DataFrame({"ds": dates_train, "y": y_train}))
    fc = m.predict(pd.DataFrame({"ds": dates_test}))
    return fc["yhat"].to_numpy()


def seasonal_naive(y_all, n_train, steps):
    return np.array([y_all[n_train + j - 52] for j in range(steps)])


def main():
    wk = load_store_weeks(DATA_PATH)
    rows, preds = [], []
    for store, g in wk.groupby("Store"):
        g = g.reset_index(drop=True)
        n = len(g)
        n_train = n - HOLDOUT
        if n_train < 64:
            print(f"Store {store}: not enough history, skipped")
            continue

        y = g["Revenue"].to_numpy(dtype=float)
        dates = g["Date"]
        exog = g[EXOG].to_numpy(dtype=float)
        y_train, y_test = y[:n_train], y[n_train:]

        res = {"Store": store}
        pred = pd.DataFrame({"Store": store, "Date": dates[n_train:].to_numpy(), "Actual": y_test})
        for name, fn in [
            ("Prophet", lambda: prophet_forecast(dates[:n_train], y_train, dates[n_train:])),
            ("ARIMA", lambda: arima_forecast(y_train, HOLDOUT)),
            ("XGB", lambda: xgb_forecast(y_train, exog[:n_train], exog[n_train:])),
            ("SeasonalNaive", lambda: seasonal_naive(y, n_train, HOLDOUT)),
        ]:
            try:
                pred[name] = fn()
                res[f"{name}_MAPE"] = mape(y_test, pred[name])
            except Exception as e:
                print(f"Store {store}: {name} failed ({type(e).__name__})")
                res[f"{name}_MAPE"] = np.nan

        cands = {k: res[f"{k}_MAPE"] for k in ["Prophet", "ARIMA", "XGB"]}
        cands = {k: v for k, v in cands.items() if not np.isnan(v)}
        res["Best_Model"] = min(cands, key=cands.get) if cands else None
        rows.append(res)
        preds.append(pred)
        print(
            f"Store {store}: Prophet {res['Prophet_MAPE']:.3f}  ARIMA {res['ARIMA_MAPE']:.3f}  "
            f"XGB {res['XGB_MAPE']:.3f}  Naive {res['SeasonalNaive_MAPE']:.3f}  -> {res['Best_Model']}"
        )

    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)
    # one long file of actual vs predicted holdout weeks, for Power BI
    pd.concat(preds).to_csv(OUT_PATH.replace("summary", "predictions"), index=False)

    print("\n=== Holdout summary (last %d weeks per store) ===" % HOLDOUT)
    print("Stores evaluated:", len(out))
    print("Best model counts:\n", out["Best_Model"].value_counts().to_string())
    print("\nMean MAPE:\n", out[[c for c in out.columns if c.endswith("_MAPE")]].mean().round(4).to_string())
    print("Median MAPE:\n", out[[c for c in out.columns if c.endswith("_MAPE")]].median().round(4).to_string())
    for k in ["Prophet", "ARIMA", "XGB"]:
        print(f"{k} beats seasonal naive in {(out[f'{k}_MAPE'] < out['SeasonalNaive_MAPE']).sum()} of {len(out)} stores")
    print("\nSaved", OUT_PATH)


if __name__ == "__main__":
    main()
