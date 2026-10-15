"""Out-of-sample XGBoost forecast of the last HOLDOUT weeks per store (store-week grain)."""
import pandas as pd
from holdout_evaluation import DATA_PATH, EXOG, HOLDOUT, load_store_weeks, xgb_forecast

wk = load_store_weeks(DATA_PATH)

for store_id, g in wk.groupby("Store"):
    g = g.reset_index(drop=True)
    n_train = len(g) - HOLDOUT
    y = g["Revenue"].to_numpy(dtype=float)
    exog = g[EXOG].to_numpy(dtype=float)

    pred = xgb_forecast(y[:n_train], exog[:n_train], exog[n_train:])
    out = f"data/xgb_store_{store_id}.csv"
    pd.DataFrame({"Date": g["Date"][n_train:], "Store": store_id, "xgb_pred": pred}).to_csv(out, index=False)
    print("Saved", out)
