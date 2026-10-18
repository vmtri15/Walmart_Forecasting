"""52 week ahead Prophet forecast with 80% prediction intervals for every store.

Prophet is used because it had the lowest mean MAPE in holdout_evaluation.py.
It also checks the intervals: the model is refit on all but the last HOLDOUT weeks and
the share of held out weeks that fall inside the interval is reported.

Run from the project root:
    python scripts/forecast_future.py
Output:
    data/forecast_future.csv   (Store, Date, Forecast, Lower_80, Upper_80)
"""
import logging

import numpy as np
import pandas as pd
from prophet import Prophet

from holdout_evaluation import DATA_PATH, HOLDOUT, load_store_weeks

logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
logging.getLogger("prophet").setLevel(logging.ERROR)

HORIZON = 52
OUT_PATH = "data/forecast_future.csv"


def fit(dates, y):
    m = Prophet(weekly_seasonality=True, yearly_seasonality=True, interval_width=0.8)
    m.fit(pd.DataFrame({"ds": dates, "y": y}))
    return m


wk = load_store_weeks(DATA_PATH)
rows, inside = [], []
for store, g in wk.groupby("Store"):
    g = g.reset_index(drop=True)

    # coverage check on the last HOLDOUT weeks
    n_train = len(g) - HOLDOUT
    m = fit(g["Date"][:n_train], g["Revenue"][:n_train])
    np.random.seed(int(store))  # Prophet draws its intervals at random; a fixed seed gives the same file every run
    fc = m.predict(pd.DataFrame({"ds": g["Date"][n_train:]}))
    y_test = g["Revenue"][n_train:].to_numpy()
    inside += list((y_test >= fc["yhat_lower"].to_numpy()) & (y_test <= fc["yhat_upper"].to_numpy()))

    # real forecast from all history
    m = fit(g["Date"], g["Revenue"])
    future = m.make_future_dataframe(periods=HORIZON, freq="W-FRI", include_history=False)
    np.random.seed(int(store))
    fc = m.predict(future)
    rows.append(pd.DataFrame({
        "Store": store, "Date": fc["ds"], "Forecast": fc["yhat"],
        "Lower_80": fc["yhat_lower"], "Upper_80": fc["yhat_upper"],
    }))
    print(f"Store {store} done")

out = pd.concat(rows)
assert (out["Lower_80"] <= out["Upper_80"]).all()
out.to_csv(OUT_PATH, index=False)
print(f"Saved {OUT_PATH}: {len(out)} rows, {out['Date'].min().date()} to {out['Date'].max().date()}")
print(f"80% interval covered {sum(inside) / len(inside):.0%} of held out weeks (target 80%)")
